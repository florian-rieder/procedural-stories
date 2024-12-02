# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
import logging
import os
from typing import List, Optional

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables import (
    ConfigurableFieldSpec,
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from pydantic import BaseModel, Field
from owlready2 import *


from generator.story.nlp.nlp import (
    extract_move_intent,
    extract_inventory_actions,
    extract_character_actions,
    apply_inventory_actions,
    apply_character_actions,
)
from generator.utils import find_levenshtein_match, encode_entity_name
from generator.story.prompts import CHAT_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


# Here we use a global variable to store the chat message history.
# This will make it easier to inspect it to see the underlying results.
store = {}


def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]


# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


class StoryConverse:
    def __init__(
        self,
        model,
        predictable_model,
        first_message,
        setting,
        language,
        start_ontology_file,
        session_id,
    ):
        self.model = model
        self.predictable_model = predictable_model
        self.setting = setting
        self.language = language
        self.session_id = session_id
        self.start_ontology_file = start_ontology_file
        self.config = {"configurable": {"session_id": session_id}}
        self.onto = get_ontology(f"file://{start_ontology_file}").load()

        # Initialize the history
        self.history = InMemoryHistory()

        # Add the first messages to the history
        self.history.add_messages([("game", first_message)])

        logger.info(f"StoryConverse initialized.")

    async def converse(self, message: str):
        # 1. Extract move intent
        previous_game_response = self.history.messages[-1][1]
        move_intent_location = extract_move_intent(
            self.predictable_model, previous_game_response, message, self.onto
        )

        # 2. Retrieve relevant information from the KG
        # 2.1 If the player intends to move, add the new location information to the chat prompt
        if move_intent_location:
            print(f"MOVE INTENT: {move_intent_location}")

        chat_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CHAT_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{{message}}"),
            ],
            template_format="jinja2",
        )

        chain = chat_prompt | self.model

        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_by_session_id,
            input_messages_key="message",
            history_messages_key="history",
        )

        # Retrieve relevant information from the KG
        with self.onto:
            player = list(self.onto.Player.instances())[0]
            current_location = player.INDIRECT_isLocatedAt
            characters_nearby = current_location.INDIRECT_containsCharacter
            locations_nearby = current_location.INDIRECT_isLinkedToLocation
            nearby_locations_names = [l.hasName for l in locations_nearby]
            items_nearby = current_location.INDIRECT_containsItem

            response = await chain_with_history.ainvoke(
                {
                    "setting": self.setting,
                    "language": self.language,
                    "location": current_location,
                    "move_intent_location": move_intent_location,
                    "characters_nearby": characters_nearby,
                    "items_nearby": items_nearby,
                    "player": player,
                    "nearby_locations_names": nearby_locations_names,
                    "message": message,
                },
                config={"configurable": {"session_id": self.session_id}},
            )

            text_response = response.content

            # Find if the LLM accepted the move, and filter out the <CONFIRM_MOVE> token
            if "<CONFIRM_MOVE>" in text_response:
                print("Move confirmed by the LLM")
                # text_response = text_response.replace('<CONFIRM_MOVE>', '').strip()

                # If the LLM accepted the move, update the KG
                with self.onto:
                    for follower in player.INDIRECT_hasFollower:
                        follower.isLocatedAt = move_intent_location
                    player.isLocatedAt = move_intent_location

        self.history.add_messages([("human", message), ("game", text_response)])

        return text_response

    async def postprocess_last_turn(self):
        # Post-process the response to update the KG
        # This allows the LLM to make changes to the world
        # Doing this after the reply ensures we take advantage of the time the player will take to respond
        # print(self.history.messages)
        player_message, game_response = self.history.messages[-2:]
        inventory_actions = extract_inventory_actions(
            self.predictable_model, player_message[1], game_response[1], self.onto
        )
        print(f"INVENTORY ACTIONS: {inventory_actions}")
        apply_inventory_actions(inventory_actions, self.onto)
        character_actions = extract_character_actions(
            self.predictable_model, player_message[1], game_response[1], self.onto
        )
        print(f"CHARACTER ACTIONS: {character_actions}")
        apply_character_actions(character_actions, self.onto)
