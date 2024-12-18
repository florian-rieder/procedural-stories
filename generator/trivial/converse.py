# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
import logging
from typing import Optional, List

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

from generator.trivial.prompts import CHAT_SYSTEM_PROMPT


logger = logging.getLogger(__name__)
# Here we use a global variable to store the chat message history.
# This will make it easier to inspect it to see the underlying results.
store = {}


def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]


max_messages = 16


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]

    def clear(self) -> None:
        self.messages = []


class TrivialConverse:
    def __init__(self, model, first_message, setting, language, session_id):
        self.model = model
        self.first_message = first_message
        self.setting = setting
        self.language = language
        self.session_id = session_id

        # Initialize the chat prompt and chain
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CHAT_SYSTEM_PROMPT),
                ("ai", self.first_message),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{{message}}"),
            ],
            template_format="jinja2",
        )

        chain = chat_prompt | self.model

        self.chain = RunnableWithMessageHistory(
            chain,
            get_by_session_id,
            input_messages_key="message",
            history_messages_key="history",
            verbose=True,
        )

        logger.info(f"TrivialConverse initialized.")

    async def converse(self, message: str):
        result = await self.chain.ainvoke(
            {
                "setting": self.setting,
                "language": self.language,
                "message": message,
            },
            config={"configurable": {"session_id": self.session_id}},
        )

        return result.content

    async def postprocess_last_turn(self):
        # Nothing to post-process
        pass

    def reset(self):
        store[self.session_id] = InMemoryHistory()
        store[self.session_id].add_messages([("game", self.first_message)])
