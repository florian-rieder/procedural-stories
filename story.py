"""Main conversation chain, used by main.py and cli.py to provide the
chat model with long term memory"""

from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.memory import (
    CombinedMemory, ConversationBufferWindowMemory
)

from langchain_community.vectorstores import Chroma

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFacePipeline

from config import *


template = """Tu es le moteur d'une fiction interactive qui se déroule dans un contexte médiéval réaliste (9ème siècle).

The setting is: {setting}

Conversation history:
{history}

Player: {input}
Assistant:"""

CONVERSATION_PROMPT = PromptTemplate(
    input_variables=["setting", "history", "input"],
    template=template
)


def get_chain() -> ConversationChain:

    # Used for streaming
    # manager = AsyncCallbackManager([])
    # stream_manager = AsyncCallbackManager([stream_handler])

    # ChatLLM whose responses are streamed to the client
    stream_llm = ChatOpenAI(
        model=CHAT_MODEL_NAME,
        temperature=CHAT_MODEL_TEMPERATURE,
        #streaming=True,
        # callback_manager=stream_manager
    )

    # Workhorse LLM
    background_llm = ChatOpenAI(
        model=WORKHORSE_MODEL_NAME,
        temperature=WORKHORSE_MODEL_TEMPERATURE
    )

    # Embedding function to be used by vector stores
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        show_progress_bar=False
    )

    # Regular conversation window memory
    conversation_memory = ConversationBufferWindowMemory(
        k=4,
        human_prefix='Player',
        ai_prefix='Game',
        input_key='input'
    )

    conversation = ConversationChain(
        llm=stream_llm,
        prompt=CONVERSATION_PROMPT,
        memory=CombinedMemory(
            memories=[
                conversation_memory
            ]
        ),
        #callback_manager=manager,  # used for streaming
        verbose=True
    )

    return conversation
