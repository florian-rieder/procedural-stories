from langchain_community.llms.mlx_pipeline import MLXPipeline
from langchain_community.chat_models.mlx import ChatMLX
from langchain_core.messages import HumanMessage


llm = MLXPipeline.from_model_id(
    "mlx-community/Meta-Llama-3-8B-Instruct-4bit",
    pipeline_kwargs={"max_tokens": 10, "temp": 0.1},
)

messages = [
    HumanMessage(
        content="What happens when an unstoppable force meets an immovable object?"
    ),
]

chat_model = ChatMLX(llm=llm)

print(chat_model._to_chat_prompt(messages))
res = chat_model.invoke(messages)
print(res.content)