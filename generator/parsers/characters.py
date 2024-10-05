import re
from typing import List

from langchain.schema import BaseOutputParser
from generator.models import CharacterData

class CharactersParser(BaseOutputParser[List[CharacterData]]):
    def parse(self, text: str) -> List[CharacterData]:
        """
        Parses the markdown list of characters into a list of Character objects.
        """

        locations = parse_characters(text)

        return locations

    @property
    def output_format(self) -> str:
        return "A list of Characters objects with name, description, and relationships."


def parse_characters(characters_string: str) -> List[CharacterData]:
    pass
