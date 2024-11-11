# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
import logging
from typing import Optional, List
import os

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from langchain_core.runnables import (
    RunnableLambda,
    ConfigurableFieldSpec,
    RunnablePassthrough,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from owlready2 import *

logger = logging.getLogger(__name__)

# Here we use a global variable to store the chat message history.
# This will make it easier to inspect it to see the underlying results.
store = {}


def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


CHAT_SYSTEM_PROMPT = """
You are an LLM designed to act as the engine for a text adventure game set in "{{setting}}".

Keep in mind that more things can and should be revealed later, after interaction with the player, so feel free to keep some information to yourself for later.
Keep in mind that not everything that is in a location is necessarily immediately visible or known to the player. Things can be hidden within a location, and a location can be quite large.

The game is played by interactions between the game (you) and the player. The player will type in natural language whatever they want to do, etc.
Do not reveal everything all at once: let the player discover things. Only output natural text, as one would read in a book they actually were the hero of.

Your messages should be short. Please do not produce lengthy messages. Your messages should be one to two sentences long. The player can always ask for more details ! For dialogues, you will output only one line of dialogue, and let the player respond.

Use the game elements provided.

Always answer in {{language}}
"""

HUMAN_MESSAGE_TEMPLATE = """
[INST]
The player's current location is "{{location.hasName}}". {{location.hasName}} is described as "{{location.hasDescription}}".

The locations accessible from where the player is are {{nearby_locations_names}}. You should discreetly tell the player they can go there, without being too explicit.

The player's character is named "{{player.hasName}}" and is described as "{{player.hasDescription}}".
The player's goal is "{{player.hasGoal.hasDescription}}"

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

Answer directly and briefly to the user's message. **You answer should be one or two sentences at most !** If the player is curious they will ask.
The player cannot invent new items, locations or characters. You cannot invent new locations or characters. You have to always refer to the given information above.
Do not reveal all the given information at once.
[/INST]
The player's message:
{{message}}
"""


def get_chain(model, predictable_model, start_message: str, setting: str, language: str, user_name: str, config: dict):
    # Load the ontology
    logger.info(f'Loading ontology for user {user_name}')
    onto = get_ontology('file://story_poptest.rdf').load()

    # with onto:
    #     sync_reasoner()

    logger.info(f'Ontology loaded for user {user_name}')
    # Define the chat prompt
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CHAT_SYSTEM_PROMPT),
            ('ai', start_message),
            MessagesPlaceholder(variable_name="history"),
            ("human", HUMAN_MESSAGE_TEMPLATE),
        ],
        template_format='jinja2',
    )

    # Define the chain
    chain = chat_prompt | model

    chain = RunnableWithMessageHistory(
        chain,
        get_by_session_id,
        input_messages_key="message",
        history_messages_key="history",
    )

    # Define the function that will be called to generate the next message
    async def converse(message: str):

        # Retrieve relevant information from the KG
        with onto:
            player = list(onto.Player.instances())[0]
            current_location = player.INDIRECT_isLocatedAt
            characters_nearby = current_location.INDIRECT_containsCharacter
            locations_nearby = current_location.INDIRECT_isLinkedToLocation
            nearby_locations_names = [l.hasName for l in locations_nearby]
            items_nearby = current_location.INDIRECT_containsItem

            logger.info(f'Player is at {current_location}')
            logger.info(f'Characters nearby: {characters_nearby}')
            logger.info(f'Locations nearby: {nearby_locations_names}')
            logger.info(f'Items nearby: {items_nearby}')


            result = await chain.ainvoke(
                {
                    "setting": setting, 
                    "language": language,
                    "location": current_location,
                    'characters_nearby': characters_nearby,
                    'items_nearby': items_nearby,
                    'player': player,
                    'nearby_locations_names': nearby_locations_names,
                    "message": message
                },
                config=config
            )

        return result

    return converse
