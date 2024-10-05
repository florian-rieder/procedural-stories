from typing import List

from langchain_core.prompts import PromptTemplate

from generator.models import Location
from generator.prompts.world import LOCATION_GENERATION_PROMPT
from generator.parsers.locations import LocationsParser



def generate_world(setting: str, model):
    locations = generate_locations(setting, model)

    for location in locations:
        print(location)
        # Generate characters
        characters = generate_characters_at_location(location, setting, model)
        # Generate items
        items = generate_items_at_location(location, setting, model)
        
        location.characters = characters
        location.items = items


def generate_locations(setting: str, model) -> List[Location]:
    # Generate locations
    location_prompt = PromptTemplate(
        input_variables=["setting"],
        template=LOCATION_GENERATION_PROMPT
    )

    location_parser = LocationsParser()

    location_chain = location_prompt | model | location_parser

    locations = location_chain.invoke({"setting": setting})
    
    return locations

def generate_characters_at_location(location: Location, setting: str, model):
    #     # Generate locations
    # prompt = PromptTemplate(
    #     input_variables=["setting"],
    #     template=LOCATION_GENERATION_PROMPT
    # )

    # parser = CharacterParser()

    # chain = prompt | model | location_parser

    # locations = location_chain.invoke({"setting": setting})
    
    # return locations
    pass

def generate_items_at_location(location: Location, setting: str, model):
    pass
