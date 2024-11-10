# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
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

The game is played by interactions between the game (you) and the player. The player will type in natural language whatever they want to do, etc.
Do not reveal everything all at once: let the player discover things. Only output natural text, as one would read in a book they actually were the hero of.

Your messages should be short. Please do not produce lengthy messages. Your messages should be one to two sentences long. The player can always ask for more details ! For dialogues, you will output only one line of dialogue, and let the player respond.

Always answer in {{language}}
"""

HUMAN_MESSAGE_TEMPLATE = """
{{message}}
"""


def get_chain(model, start_message: str):
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CHAT_SYSTEM_PROMPT),
            ('ai', start_message),
            MessagesPlaceholder(variable_name="history"),
            ("human", HUMAN_MESSAGE_TEMPLATE),
        ],
        template_format='jinja2',

    )

    chain = chat_prompt | model

    chain = RunnableWithMessageHistory(
        chain,
        get_by_session_id,
        input_messages_key="message",
        history_messages_key="history",
        verbose=True
    )

    async def ainvoke_wrapper(*args, **kwargs):
        # makeshift verbose mode
        # print('helloooooooooooooo')
        # history = chain.get_session_history()
        # params = args[0]
        # params['history'] = history
        # print(chat_prompt.invoke(*args).text)


        result = await chain.ainvoke(*args, **kwargs)

        return result

    return ainvoke_wrapper
