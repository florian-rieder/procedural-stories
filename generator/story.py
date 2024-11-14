# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
import logging
import os
from typing import List, Optional

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import (
    ConfigurableFieldSpec,
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from owlready2 import *
from pydantic import BaseModel, Field


from generator.nlp import extract_move_intent

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """
You are an LLM designed to act as the engine for a text adventure game set in "{{setting}}".

Keep in mind that more things can and should be revealed later, after interaction with the player, so feel free to keep some information to yourself for later.
Keep in mind that not everything that is in a location is necessarily immediately visible or known to the player. Things can be hidden within a location, and a location can be quite large. You should discreetly tell the player they can go there, without being too explicit.
If the player has spent a long time in a location, you can push them a little more explicitly to move to different locations.
The game is played by interactions between the game (you) and the player. The player will type in natural language whatever they want to do, etc.
Do not reveal everything all at once: let the player discover things. Only output natural text, as one would read in a book they actually were the hero of.

Your messages should be short. Please do not produce lengthy messages. Your messages should be one to two sentences long. The player can always ask for more details ! For dialogues, you will output only one line of dialogue, and let the player respond.

Use the game elements provided:

# Game state
The player's current location is "{{location.hasName}}". {{location.hasName}} is described as "{{location.hasDescription}}".

The locations accessible from where the player is are {{nearby_locations_names}}. You should discreetly tell the player they can go there, without being too explicit.

The player's character is named "{{player.hasName}}" and is described as "{{player.hasDescription}}".
The player's goal is "{{player.hasGoal[0].hasDescription}}"

{%- if characters_nearby %}
Characters present in {{location.hasName}}:
{%- for character in characters_nearby %}
    - {{ character.hasName }}: {{character.hasDescription}} (narrative importance {{character.hasImportance}})
{%- endfor %}
{%- else %}
    There are no other characters present in {{location.hasName}}.
{%- endif %}

{%- if items_nearby %}
Items present in {{location.hasName}}:
{%- for item in items_nearby %}
    - {{ item.hasName }}: {{item.hasDescription}} (narrative importance {{item.hasImportance}})
{%- endfor %}
{%- else %}
    There are no items present in {{location.hasName}}.
{%- endif %}

{%- if player.INDIRECT_ownsItem %}
Items in the player's inventory:
{%- for item in player.INDIRECT_ownsItem %}
    - {{ item.hasName }}: {{item.hasDescription}} (narrative importance {{item.hasImportance}})
{%- endfor %}
{%- else %}
    The player has no items in their inventory.
{%- endif %}

{%- if move_intent_location %}
The parser has detected that the player intends to move to {{move_intent_location.hasName}}.
    {{move_intent_location.hasName}} is described as "{{move_intent_location.hasDescription}}".
    {%- if move_intent_location.INDIRECT_containsCharacter %}
        Characters present in {{move_intent_location.hasName}}:
        {%- for character in move_intent_location.INDIRECT_containsCharacter %}
            - {{ character.hasName }}: {{character.hasDescription}} (narrative importance {{character.hasImportance}})
        {%- endfor %}
    {%- endif %}
    {%- if move_intent_location.INDIRECT_containsItem %}
        Items present in {{move_intent_location.hasName}}:
        {%- for item in move_intent_location.INDIRECT_containsItem %}
            - {{ item.hasName }}: {{item.hasDescription}} (narrative importance {{item.hasImportance}})
        {%- endfor %}
    {%- endif %}

If you confirm the move, add the token "<CONFIRM_MOVE>" to your response.
**Keep in mind that the player will read your response before typing theirs, and only the token will be removed from your response.**
{%- endif %}

Always answer in {{language}}
"""


# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


# Here we use a global variable to store the chat message history.
# This will make it easier to inspect it to see the underlying results.
store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]



def get_chain(model, predictable_model, first_message: str, setting: str, language: str, user_name: str, config: dict):
    # Load the ontology
    logger.info(f'Loading ontology for user {user_name}')
    onto = get_ontology('file://story_poptest70b.rdf').load()

    # with onto:
    #     sync_reasoner()

    logger.info(f'Ontology loaded for user {user_name}')
    # Define the chat prompt

    # Initialize the history
    history = InMemoryHistory()
    system_prompt_template = PromptTemplate(template=CHAT_SYSTEM_PROMPT, template_format='jinja2')
    history.system_prompt = system_prompt_template.invoke({
        'setting': setting,
        'language': language
    }).text

    # Add the first messages to the history
    history.add_messages([('ai', first_message)])

    # Define the function that will be called to generate the next message
    
    
    async def converse(message: str):
            # 1. Extract move intent
        move_intent_location = extract_move_intent(predictable_model, message, onto)

        # 2. Retrieve relevant information from the KG
        # 2.1 If the player intends to move, add the new location information to the chat prompt
        if move_intent_location:
            print(f'Move intent: {move_intent_location}')


        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", CHAT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{{message}}"),
        ], template_format='jinja2')

        chain = chat_prompt | model

        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_by_session_id,
            input_messages_key="message",
            history_messages_key="history",
        )


        # Retrieve relevant information from the KG
        with onto:
            player = list(onto.Player.instances())[0]
            current_location = player.INDIRECT_isLocatedAt
            characters_nearby = current_location.INDIRECT_containsCharacter
            locations_nearby = current_location.INDIRECT_isLinkedToLocation
            nearby_locations_names = [l.hasName for l in locations_nearby]
            items_nearby = current_location.INDIRECT_containsItem


            response = await chain_with_history.ainvoke(
                {"setting": setting, 
                "language": language,
                "location": current_location,
                "move_intent_location": move_intent_location,
                'characters_nearby': characters_nearby,
                'items_nearby': items_nearby,
                'player': player,
                'nearby_locations_names': nearby_locations_names,
                "message": message},
                config={"configurable": {"session_id": "foo"}}
            )

            # Find if the LLM accepted the move, and filter out the <CONFIRM_MOVE> token
            if '<CONFIRM_MOVE>' in response.content:
                print('Move confirmed by the LLM')
                response = response.replace('<CONFIRM_MOVE>', '').strip()

                # If the LLM accepted the move, update the KG
                with onto:
                    for follower in player.INDIRECT_hasFollower:
                        follower.isLocatedAt = move_intent_location
                    player.isLocatedAt = move_intent_location

        return response

    return converse
