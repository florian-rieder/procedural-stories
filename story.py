"""Main conversation chain, used by main.py and cli.py to provide the
chat model with long term memory"""

from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.memory import (
    CombinedMemory, ConversationBufferWindowMemory
)

from langchain_community.vectorstores import Chroma

from langchain_community.llms.mlx_pipeline import MLXPipeline
from langchain_community.chat_models.mlx import ChatMLX
# from langchain_openai import ChatOpenAI
# from langchain_openai import OpenAIEmbeddings
# from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFacePipeline

from config import *




llm = MLXPipeline.from_model_id(
    #"mlx-community/Mixtral-8x7B-Instruct-v0.1",
    #"mlx-community/mixtral-8x22b-4bit",
    "mlx-community/Meta-Llama-3-8B-Instruct-4bit",
    pipeline_kwargs={"max_tokens": 512, "temp": 0.2, "repetition_penalty":1.0},
)


template = """Tu es le moteur d'une fiction interactive qui se déroule dans un contexte médiéval réaliste (9ème siècle, actuelle Normandie).
Tu ne dois pas explicitement donner des options à choix au joueur. Il doit formuler ce qu'il veut faire en language naturel, et tu dois les exécuter, dans la limite du raisonnable.
Tu peux refuser de faire une action si c'est en dehors du contexte du jeu.
Tu devrais ajouter des indices subtiles d'interactions possibles dans les descriptions des scènes.

Commence avec une description du contexte pour le joueur: où est-il, qui est-il ?

Utilise toujours le Français !
N'ajoute aucun texte supplémentaire hors des descriptions que tu fais au joueur.

Historique de la conversation:
{history}

Joueur: {input}
Jeu:"""

CONVERSATION_PROMPT = PromptTemplate(
    input_variables=["history", "input"],
    template=template
)


def get_chain(stream_handler) -> ConversationChain:

    # Used for streaming
    manager = AsyncCallbackManager([])
    stream_manager = AsyncCallbackManager([stream_handler])

    # ChatLLM whose responses are streamed to the client
    chat_model = ChatMLX(llm=llm)

    # Regular conversation window memory
    conversation_memory = ConversationBufferWindowMemory(
        k=4,
        human_prefix='Player',
        ai_prefix='Game',
        input_key='input'
    )

    conversation = ConversationChain(
        llm=chat_model,
        prompt=CONVERSATION_PROMPT,
        memory=conversation_memory,
        callback_manager=manager,  # used for streaming
        verbose=True
    )

    return conversation
