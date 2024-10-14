import re
from typing import List, Optional

from langchain.schema import BaseOutputParser
from generator.models import LocationData

from graph_locations import display_location_relationships


class ExpandedLocationParser(BaseOutputParser[LocationData]):
    def parse(self, text: str) -> List[LocationData]:
        """
        Parses the location into a LocationData object.
        """

        locations = parse_expanded_location(text)

        return locations

    @property
    def output_format(self) -> str:
        return "A LocationData object"


def parse_locations(location_string: str) -> LocationData:
    print(location_string)

    location = LocationData()

    return location
