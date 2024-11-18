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
from pydantic import BaseModel, Field
from owlready2 import *


from generator.nlp import extract_move_intent

from generator.utils import find_levenshtein_match, encode_entity_name

logger = logging.getLogger(__name__)

from generator.story.prompts import CHAT_SYSTEM_PROMPT


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
                {
                    "setting": setting, 
                    "language": language,
                    "location": current_location,
                    "move_intent_location": move_intent_location,
                    'characters_nearby': characters_nearby,
                    'items_nearby': items_nearby,
                    'player': player,
                    'nearby_locations_names': nearby_locations_names,
                    "message": message
                },
                config=config
            )

            text_response = response.content

            # Find if the LLM accepted the move, and filter out the <CONFIRM_MOVE> token
            if '<CONFIRM_MOVE>' in text_response:
                print('Move confirmed by the LLM')
                text_response = text_response.replace('<CONFIRM_MOVE>', '').strip()

                # If the LLM accepted the move, update the KG
                with onto:
                    for follower in player.INDIRECT_hasFollower:
                        follower.isLocatedAt = move_intent_location
                    player.isLocatedAt = move_intent_location

        return text_response

    return converse

