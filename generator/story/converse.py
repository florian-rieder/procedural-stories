# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
import logging

from tracet import Chain, Jinja2Template, ConversationMemory, chainable


from owlready2 import get_ontology


from generator.story.nlp.nlp import (
    apply_inventory_actions,
    apply_character_actions,
    get_move_intent_extraction_chain,
    get_inventory_actions_extraction_chain,
    get_character_actions_extraction_chain,
)

from generator.story.prompts import CHAT_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


@chainable(input_keys=["history"], output_key="previous_game_response")
def get_previous_game_response(history):
    return history[-1]["content"]


@chainable(
    input_keys=["move_intent_location", "history", "message", "onto"],
    output_key="info",
)
def get_relevant_information(move_intent_location, history, message, onto):
    # Retrieve relevant information from the KG
    with onto:
        player = list(onto.Player.instances())[0]
        current_location = player.INDIRECT_isLocatedAt
        characters_nearby = current_location.INDIRECT_containsCharacter
        locations_nearby = current_location.INDIRECT_isLinkedToLocation
        nearby_locations_names = [location.hasName for location in locations_nearby]
        items_nearby = current_location.INDIRECT_containsItem

        return {
            "current_location": current_location,
            "characters_nearby": characters_nearby,
            "locations_nearby": locations_nearby,
            "nearby_locations_names": nearby_locations_names,
            "items_nearby": items_nearby,
            "player": player,
        }


@chainable(
    input_keys=["game_response", "move_intent_location", "onto"],
    output_key="cleaned_game_response",
)
def extract_move_confirmation(game_response: str, move_intent_location, onto):
    # Find if the LLM accepted the move, and filter out the <CONFIRM_MOVE> token
    cleaned_game_response = game_response
    if "<CONFIRM_MOVE>" in game_response:
        print("Move confirmed by the LLM")
        cleaned_game_response = cleaned_game_response.replace(
            "<CONFIRM_MOVE>", ""
        ).strip()

        # If the LLM accepted the move, update the KG
        with onto:
            player = onto.Player.instances()[0]
            for follower in player.INDIRECT_hasFollower:
                follower.isLocatedAt = move_intent_location
            player.isLocatedAt = move_intent_location

    # Overwrite the response with the new one
    return cleaned_game_response


class StoryConverse:
    def __init__(
        self,
        model,
        first_message,
        setting,
        language,
        start_ontology_file,
    ):
        self.model = model
        self.setting = setting
        self.language = language
        self.start_ontology_file = start_ontology_file

        self.onto = get_ontology(f"file://{start_ontology_file}").load()

        # Initialize the history
        self.history = []

        # Add the first messages to the history
        self.history.append({"role": "game", "content": first_message})

        self.move_intent_extraction_chain = get_move_intent_extraction_chain(model)
        self.inventory_actions_extraction_chain = (
            get_inventory_actions_extraction_chain(model)
        )
        self.character_actions_extraction_chain = (
            get_character_actions_extraction_chain(model)
        )

        self.conversation_chain = Chain(
            get_previous_game_response,
            self.move_intent_extraction_chain,
            get_relevant_information,
            Jinja2Template(  # Format system prompt with the relevant information
                CHAT_SYSTEM_PROMPT,
                output_key="system_prompt",
            ),
            self.model.using(
                output_key="game_response",
                history_key="history",
                system_prompt_key="system_prompt",
            ),
            extract_move_confirmation,
            ConversationMemory(
                human_message_key="message",
                llm_response_key="cleaned_game_response",
                output_key="history",
                human_prefix="player",
                llm_prefix="game",
            ),
            verbose=True,
            debug=True,
        )

        self.postprocess_chain = Chain(
            self.inventory_actions_extraction_chain,
            apply_inventory_actions,
            self.character_actions_extraction_chain,
            apply_character_actions,
            verbose=True,
            debug=True,
        )

        logger.info("StoryConverse initialized.")

    async def converse(self, message: str):
        response = await self.conversation_chain.acall(
            setting=self.setting,
            language=self.language,
            message=message,
            history=self.history,
            onto=self.onto,
        )

        # TODO Write the new messages to a file

        # Update the message history
        self.history = response["history"]

        return response["cleaned_game_response"]

    async def postprocess_last_turn(self):
        # Post-process the response to update the KG
        # This allows the LLM to make changes to the world
        # Doing this after the reply ensures we take advantage of the time the player will take to respond
        # print(self.history.messages)
        player_message, game_response = self.history[-2:]

        await self.postprocess_chain.acall(
            message=player_message["content"],
            game_response=game_response["content"],
            onto=self.onto,
        )

    def reset(self):
        self.history = []
        self.history.append({"role": "game", "content": self.first_message})
