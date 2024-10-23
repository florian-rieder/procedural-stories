import json
import re
from typing import List

from langchain.schema import BaseOutputParser

from generator.models import OutlineData, ItemData, CharacterData, LocationData


class OutlineParser(BaseOutputParser[OutlineData]):
    def parse(self, text: str) -> OutlineData:
        """
        Parses the json story outline.
        """

        outline = parse_outline(text)

        return outline

    @property
    def output_format(self) -> str:
        return "A collection of properties that define the outline of a story world"


def parse_outline(outline_string: str) -> OutlineData:
    print('---')
    print(outline_string)
    print('---')

    # https://regex101.com/r/y13CrG/1
    json_extraction_pattern = r'```(?:json)?\n?((?:.*\n)*)\n?```'

    json_match = re.search(json_extraction_pattern, outline_string)

    json_text = json_match.group(1)
    
    data = json.loads(json_text)

    outline = OutlineData(
        locations = data['Locations'],
        characters = data['Characters'],
        player = data['Player'],
        goal = data['Goal'],
        events = data['Events'],
        items = data['Items'],
        comments = data['Comments'],
    )
    return outline
