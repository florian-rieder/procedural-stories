from typing import List

from langchain.globals import set_verbose
from langchain_community.llms.mlx_pipeline import MLXPipeline
from langchain_community.chat_models.mlx import ChatMLX

from generator.parsers.locations import Location, LocationsParser
from generator.prompts.world import ABOX_GENERATION_PROMPT
from generator.world_generator import generate_world

set_verbose(True)


print('Loading ontology...')
with open("story_ontology.owl", "r") as f:
    ontology = f.read()
#print(ontology)

print('Loading model...')
llm = MLXPipeline.from_model_id(
    "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",
    pipeline_kwargs={"max_tokens": 4096, "temp": 0.2, "repetition_penalty":1.0},
)
print('Model loaded.')

model = ChatMLX(llm=llm)

setting = "L'histoire se déroule dans la Normandie viking du 9e siècle, à l'époque de l'exploration et de la colonisation de la Normandie par les Vikings. L'environnement comprend des villes côtières, des forêts denses et des campements vikings. L'histoire tourne autour d'une bataille à venir."

# prompt = PromptTemplate(
#     input_variables=["tbox", "context"],
#     template=ABOX_GENERATION_PROMPT
# )

# chain = prompt | model


# res = chain.invoke({"context": setting, "tbox": ontology})
# print(res.content)

if __name__ == "__main__":
    generate_world(setting, model)
