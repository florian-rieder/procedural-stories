from typing import List

from langchain.globals import set_verbose
from langchain_community.llms.mlx_pipeline import MLXPipeline
from langchain_community.chat_models.mlx import ChatMLX
from langchain_core.prompts import PromptTemplate

from generator.parsers.locations import LocationsParser
from generator.prompts.world import STORY_GENERATION_PROMPT
from generator.world_generator import generate_world
from generator.utils.serializers import json2llmready

set_verbose(True)


print('Loading ontology...')
with open("story.json", "r") as f:
    ontology = json2llmready(f.read())
#print(ontology)

print('Loading model...')
llm = MLXPipeline.from_model_id(
    "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",
    pipeline_kwargs={"max_tokens": 4096, "temp": 0.2, "repetition_penalty":1.0},
)
print('Model loaded.')

model = ChatMLX(llm=llm)

#setting = "L'histoire se déroule dans la Normandie viking du 9e siècle, à l'époque de l'exploration et de la colonisation de la Normandie par les Vikings. L'environnement comprend des villes côtières, des forêts denses et des campements vikings. L'histoire tourne autour d'une bataille à venir."

setting = "L'histoire se déroule au Moyen Orient au 10ème siècle. Tu as la liberté du reste du contexte."

prompt = PromptTemplate(
    input_variables=["ontology", "context"],
    template=STORY_GENERATION_PROMPT
)

chain = prompt | model

res = chain.invoke({"context": setting, "ontology": ontology})
print(res.content)

# if __name__ == "__main__":
#     generate_world(setting, model)
