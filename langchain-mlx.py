from langchain_core.prompts import PromptTemplate
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from langchain_community.llms.mlx_pipeline import MLXPipeline
from langchain_community.chat_models.mlx import ChatMLX


llm = MLXPipeline.from_model_id(
    # "mlx-community/Mixtral-8x7B-Instruct-v0.1",
    # "mlx-community/mixtral-8x22b-4bit",
    "mlx-community/Meta-Llama-3-8B-Instruct-4bit",
    pipeline_kwargs={"max_tokens": 128, "temp": 0.1},
)

chat_model = ChatMLX(llm=llm)

# messages = [
#     HumanMessage(
#         content="En quelques phrases, crée un cadre concise pour une fiction interactive qui se déroule dans un contexte médiéval réaliste (9e siècle). La description du setting de départ doit donner quelques indices au joueur d'actions qui lui serait possible de faire (sans pour autant lui indiquer explicitement la voie). Ne produis que la description du contexte à destination du joueur"
#     ),
# ]

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate.from_template(template)


chain = prompt | chat_model

question = "What is the question to the answer 42 ?"
print(chain.invoke({"question": question}))

# print(chat_model._to_chat_prompt(messages))
# res = chat_model.invoke(messages)
# print(res.content)
