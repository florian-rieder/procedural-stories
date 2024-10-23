from typing import List
import logging

from langchain_core.prompts import PromptTemplate
from langchain.llms import BaseLLM
from langchain_core.output_parsers import JsonOutputParser


from generator.models import LocationData, OutlineData, CharacterData, ItemData
from generator.prompts.world import *
from generator.parsers import ExpandedLocationParser, OutlineParser

logger = logging.getLogger(__name__)


def generate_world(setting: str, model: BaseLLM):
    # 1. Generate an outline of the story world
    logger.info('Generate story world outline...')
    outline = generate_outline(setting, model)

    # Parse locations into LocationData objects
    locations = []
    for loc in outline.locations:
        location = LocationData(name=loc['name'], description=loc['description'])
        locations.append(location)

    # 2. Add intermediate locations between major locations defined in the outline
    logger.info('Generate intermediate locations...')
    intermediate_locations = generate_intermediate_locations(locations, setting, model)

    for loc in intermediate_locations:
        location = LocationData(name=loc['name'], description=loc['description'], relationships=loc['isLinkedToLocation'])
        locations.append(location)

    # 3. Generate the details of each location
    for location in locations:
        print(location)
    
        location = expand_location(setting, location, model)
        
        # Characters from the outline

        print(location)
        # # Generate characters
        # characters = generate_characters_at_location(location, setting, model)
        # # Generate items
        # items = generate_items_at_location(location, setting, model)

        # location.characters = characters
        # location.items = items


def generate_outline(setting: str, model: BaseLLM) -> OutlineData:
    prompt = PromptTemplate(
        input_variables=['setting'],
        template=OUTLINE_GENERATION_PROMPT,
        template_format='jinja2'
    )

    parser = JsonOutputParser() #OutlineParser()

    chain = prompt | model | parser

    result = chain.invoke({'setting': setting})

    return result

def generate_intermediate_locations(locations: List[LocationData], setting: str, model: BaseLLM):
    # Parse locations into LocationData objects
    prompt = PromptTemplate(
        input_variables=["ontology", "context"],
        template=INTERMEDIATE_LOCATIONS_GENERATION_PROMPT,
        template_format='jinja2'
    )

    parser = JsonOutputParser()

    chain = prompt | model | parser

    res = chain.invoke({"setting": setting, "locations": locations})

def expand_location(location: LocationData, setting: str, model: BaseLLM):
    prompt = PromptTemplate(
        input_variables=['setting', 'location_name', 'location_description'],
        template=LOCATION_EXPANSION_PROMPT
    )

    parser = ExpandedLocationParser()

    chain = prompt | model | parser

    result = chain.invoke({
        'setting': setting,
        'location_name': location.name,
        'location_description': location.description
    })

    return result.content


def generate_characters_at_location(location: LocationData, setting: str, model: BaseLLM):
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


def generate_items_at_location(location: LocationData, setting: str, model: BaseLLM):
    pass
