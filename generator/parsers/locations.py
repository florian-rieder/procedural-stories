import re
from typing import List, Optional

from langchain.schema import BaseOutputParser
from generator.models import Location

from graph_locations import display_location_relationships


class LocationsParser(BaseOutputParser[List[Location]]):
    def parse(self, text: str) -> List[Location]:
        """
        Parses the markdown list of locations into a list of Location objects.
        """

        locations = parse_locations(text)
        
        display_location_relationships(locations)

        return locations

    @property
    def output_format(self) -> str:
        return "A list of Location objects with name, description, and relationships."


def parse_locations(locations_string: str) -> List[Location]:
    pattern = r'\s*-\s*\*\*(.*?)\*\*\s*\[(.*)\]:\s*(.*?)\s*\((.*)\)'

    locations = list()
    
    print(locations_string)

    lines = locations_string.strip().split('\n')
    for line in lines:
        match = re.search(pattern, line)

        if not match:
            print(f"Line didn't match pattern: {line}")
            continue

        name = match.group(1)           # Location name
        stance = match.group(2)         # Stance of the location towards the player
        description = match.group(3)    # Description
        relationships = match.group(4)  # Comma-separated relationships

        # Split and clean the relationships
        relationships = [rel.strip().strip('*') for rel in relationships.split(',')]
        
        # Remove empty locations
        relationships = list(filter(len, relationships))

        location = Location(
            name=name,
            stance=stance,
            description=description,
            relationships=relationships
        )
        locations.append(location)

    # Remove nodes that are referenced but never defined
    # (is contained in the relationships of a location but doesn't exist as a Location)
    for location in locations:
        for rel in location.relationships:
            # Remove relationships which don't point to an existing Location
            location.relationships = [
                    rel for rel in location.relationships
                    # check that this relationship points to an existing Location
                    if any(loc.name == rel for loc in locations)
                ]

    return locations
