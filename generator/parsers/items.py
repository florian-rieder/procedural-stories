import re
from typing import List

from langchain.schema import BaseOutputParser
from generator.models import Item


class CharactersParser(BaseOutputParser[List[Location]]):
    def parse(self, text: str) -> List[Location]:
        """
        Parses the markdown list of items into a list of Item objects.
        """

        locations = parse_items(text)

        return locations

    @property
    def output_format(self) -> str:
        return "A list of Items objects with name, description, and relationships."


def parse_items(items_string: str) -> List[Item]:
    pass
