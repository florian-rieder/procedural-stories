"""
These are just data models required by Langchain's parsers !!!
The real data model is in the ontology !
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CharacterData:
    name: str
    description: str


@dataclass
class ItemData:
    name: str
    description: str
    quantity: Optional[int] = 1


@dataclass
class LocationData:
    name: str
    description: str
    stance: Optional[str] = None
    relationships: Optional[List[str]] = field(default_factory=list)
    characters: Optional[List[str]] = field(default_factory=list)
    items: Optional[List[ItemData]] = field(default_factory=list)

