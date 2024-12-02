import logging

from tracet import Chain, ConversationMemory, Jinja2Template

from generator.trivial.prompts import CHAT_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class TrivialConverse:
    def __init__(self, model, first_message, setting, language, session_id):
        self.model = model
        self.first_message = first_message
        self.setting = setting
        self.language = language
        self.session_id = session_id

        # Initialize the message history
        self.history = []
        self.history.append({"role": "ai", "content": self.first_message})

        # Initialize the conversation chain
        self.chain = Chain(
            Jinja2Template(
                CHAT_SYSTEM_PROMPT,
                output_key="system_prompt",
            ),
            model.using(
                output_key="response",
                history_key="history",
                system_prompt_key="system_prompt",
            ),
            ConversationMemory(
                human_message_key="message",
                llm_message_key="response",
                output_key="history",
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

        # TODO Write the new messages to a file

        # Update the message history
        self.history = result["history"]

        return result["response"]

    async def postprocess_last_turn(self):
        # Nothing to post-process
        pass

    def reset(self):
        self.history = []
        self.history.append({"role": "system", "content": CHAT_SYSTEM_PROMPT})
        self.history.append({"role": "ai", "content": self.first_message})
