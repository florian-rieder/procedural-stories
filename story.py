"""Main conversation chain, used by main.py and cli.py to provide the
chat model with long term memory"""

from langchain.chains import ConversationChain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts import PromptTemplate

from langchain.memory.buffer_window import ConversationBufferWindowMemory

from langchain_community.vectorstores import Chroma

from langchain_community.llms.mlx_pipeline import MLXPipeline
from langchain_community.chat_models.mlx import ChatMLX
# from langchain_openai import ChatOpenAI
# from langchain_openai import OpenAIEmbeddings
# from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFacePipeline

from config import *



print('Loading model...')
llm = MLXPipeline.from_model_id(
    #"mlx-community/Mistral-7B-Instruct-v0.3",
    #"mlx-community/Mixtral-8x7B-Instruct-v0.1",
    #"mlx-community/Meta-Llama-3-8B-Instruct-4bit",
    "mlx-community/Meta-Llama-3-8B-Instruct-8bit",
    #"mlx-community/Meta-Llama-3-8B-Instruct-bf16",
    pipeline_kwargs={"max_tokens": 512, "temp": 0.2, "repetition_penalty":1.0},
)
print('Model loaded.')

template = """Tu es le moteur d'une fiction interactive qui se déroule dans un contexte médiéval réaliste (9ème siècle, actuelle Normandie).
Tu ne dois pas explicitement donner des options à choix au joueur. Il doit formuler ce qu'il veut faire en language naturel, et tu dois les exécuter, dans la limite du raisonnable.
Tu peux refuser de faire une action si c'est en dehors du contexte du jeu.
Tu devrais ajouter des indices subtiles d'interactions possibles dans les descriptions des scènes.

Commence avec une description du contexte pour le joueur (où est-il, qui est-il ?) ainsi qu'un évènement perturbateur

Utilise toujours le Français ! Limite toi à 1 paragraphe.
N'ajoute aucun texte supplémentaire hors des descriptions que tu fais au joueur.
Chaque message devrait faire un ou deux paragraphes au plus. Reste concis, et laisse à la curiosité du joueur de révéler plus de choses.
Termine toujours avec "Que voulez-vous faire?"

Historique de la conversation:
{history}

Joueur: {input}
Jeu:"""

CONVERSATION_PROMPT = PromptTemplate(
    input_variables=["history", "input"],
    template=template
)

def get_chain() -> ConversationChain:


    # ChatLLM whose responses are streamed to the client
    chat_model = ChatMLX(llm=llm)

    # Regular conversation window memory
    conversation_memory = ConversationBufferWindowMemory(
        k=12,
        human_prefix='Player',
        ai_prefix='Game',
        input_key='input'
    )

    conversation = ConversationChain(
        llm=chat_model,
        prompt=CONVERSATION_PROMPT,
        memory=conversation_memory,
        verbose=True
    )

    return conversation
