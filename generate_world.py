from typing import List

from langchain.globals import set_verbose
from langchain_community.llms.mlx_pipeline import MLXPipeline
from langchain_community.chat_models.mlx import ChatMLX
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from generator.prompts.world import *
from generator.world_generator import generate_world, generate_outline
from generator.utils.serializers import json2llmready

set_verbose(True)


print('Loading ontology...')
with open("story.json", "r") as f:
    ontology = json2llmready(f.read())
#print(ontology)

print('Loading model...')
llm = MLXPipeline.from_model_id(
    "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",
    pipeline_kwargs={"max_tokens": 2048, "temp": 0.4, "repetition_penalty":1.1},
)
print('Model loaded.')

model = ChatMLX(llm=llm)

setting = "L'histoire se déroule dans la Normandie viking du 9e siècle, à l'époque de l'exploration et de la colonisation de la Normandie par les Vikings. L'environnement comprend des villes côtières, des forêts denses et des campements vikings. L'histoire tourne autour d'une bataille à venir."

#setting = "L'histoire se déroule au Moyen Orient au 10ème siècle. Tu as la liberté du reste du contexte."


from generator.parsers import OutlineParser
#from generator.world_generator import generate_intermediate_locations
from generator.models import LocationData, ItemData, CharacterData

outline = generate_outline(setting, llm)

# with open('outline.txt', 'r') as f:
#     text = f.read()
# outline = OutlineParser().parse(text)

print(outline)

# Parse locations into LocationData objects
locations = []
for loc in outline.locations:
    location = LocationData(name=loc['name'], description=loc['description'])
    locations.append(location)

for itm in outline.items:
    item_location = itm.get('isAtLocation')

    item = ItemData(
        name=itm['name'],
        description=itm['description']
    )
    if item_location:
        # Add the item to the location's item list
        matches = list(filter(lambda x: x == item_location, locations))
        if len(matches) > 0:
            matches[0].items.append(item)

for char in outline.characters:
    char_location = char.get('isAtLocation')
    
    character = CharacterData(
        name=char['name'],
        description=char['description']
    )
    
    if char_location:
        matches = list(filter(lambda x: x == char_location, locations))
        if len(matches) > 0:
            matches[0].characters.append(item)

print(outline)

# prompt = PromptTemplate(
#     input_variables=["setting", "location", "characters", "items"],
#     template=LOCATION_EXPANSION_PROMPT,
#     template_format='jinja2'
# )

# parser = JsonOutputParser()

# chain = prompt | model | parser

# for location in outline.locations:

#     res = chain.invoke({"setting": setting,
#                         "location": location,
#                         "characters": outline.characters,
#                         "items": outline.items })

#     print('----*----')
#     print(res)
#     print('----*----')

# with open('intermediate_locations.txt', 'r') as f:
#     text = f.read()

# if __name__ == "__main__":
#     generate_world(setting, model)
