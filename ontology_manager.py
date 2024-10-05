from typing import List

from owlready2 import *

from generator.models import LocationData
from generator.utils.serializers import natural2pascal

# # Load ontology from file
# onto = get_ontology("file:///Users/frieder/Documents/GitHub/procedural-stories/story_ontology.owl").load()

# # Reason
# sync_reasoner()

def add_location(onto, location: LocationData):
    with onto:
        instance_name = natural2pascal(location.name)
        new_loc = onto.Location(instance_name)

        new_loc.hasName = location.name
        new_loc.hasDescription = location.description
        new_loc.hasStanceTowardsPlayer = location.stance

def add_locations(onto, locations: List[LocationData]):
    for location in locations:
        add_location(onto, location)
    
    for location in locations:
        instance_name = natural2pascal(location.name)
        this_location = onto.Location(instance_name)

        # Add the relationships
        for relationship in location.relationships:
            other_location_name = natural2pascal(relationship)
            other_location = onto.Location(other_location_name)
            
            # Add relationship between the locations
            this_location.isLinkedToLocation.append(other_location)

def list_onto(onto):
    print('Classes')
    # List all classes in the ontology
    for clas in onto.classes():
        print(clas)

    print('\nObject properties')
    # List all object properties (relationships between classes)
    for prop in onto.object_properties():
        print(prop)

    print('\nData properties')
    # List all data properties (relationships between classes and literals)
    for prop in onto.data_properties():
        print(prop)
        
    print('\nIndividuals')
    for prop in onto.individuals():
        print(prop)
    
    # faction_class = onto.Faction
    
    # print(f"Faction class: {faction_class}")
    
    # print("\nProperties:")
    # for prop in faction_class.get_properties():
    #     print(f"{prop}: Domain={prop.domain}, Range={prop.range}")

# list_onto(onto)
# # serialize rdflib graph to json-ld (might be better for LLM comprehension)
# # g.serialize(format='json-ld')