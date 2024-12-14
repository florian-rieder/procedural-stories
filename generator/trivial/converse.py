import logging

from tracet import Chain, ConversationMemory, Jinja2Template

from generator.trivial.prompts import CHAT_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class TrivialConverse:
    def __init__(self, model, first_message, setting, language):
        self.model = model
        self.first_message = first_message
        self.setting = setting
        self.language = language

        # Initialize the message history
        self.history = []
        self.history.append({"role": "game", "content": self.first_message})

        # Initialize the conversation chain
        self.chain = Chain(
            Jinja2Template(
                CHAT_SYSTEM_PROMPT,
                output_key="system_prompt",
            ),
            model.using(
                input_key="message",
                output_key="game_response",
                history_key="history",
                system_prompt_key="system_prompt",
                temperature=1.0,
            ),
            ConversationMemory(
                human_message_key="message",
                llm_response_key="game_response",
                output_key="history",
                human_prefix="player",
                llm_prefix="game",
                max_messages=16,
            ),
            verbose=True,
        )

        logger.info("TrivialConverse initialized.")

    async def converse(self, message: str):
        result = await self.chain.acall(
            message=message,
            setting=self.setting,
            language=self.language,
            history=self.history,
        )

        # Update the message history
        self.history = result["history"]

        print("Player move intent: ", result.get("move_intent_location"))
        print(
            "Player's final position: ",
            result.get("onto").Player.instances()[0].INDIRECT_isLocatedAt.hasName,
        )

        return result["game_response"]

    async def postprocess_last_turn(self):
        # Nothing to post-process
        pass

    def reset(self, first_message: str):
        self.history = []
        self.history.append({"role": "game", "content": first_message})
