"""
These are just data models required by Langchain's parsers !!!
The real data model is in the ontology !
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CharacterData:
    name: str
    description: str
    

@dataclass
class ItemData:
    name: str
    type: str
    description: str
    quantity: Optional[int] = 1

@dataclass
class LocationData:
    name: str
    stance: Optional[str] = None
    description: Optional[str] = None
    relationships: Optional[List[str]] = None
    characters: Optional[List[str]] = None
    items: Optional[List[ItemData]] = None

@dataclass
class OutlineData:
    locations: List[dict]
    characters: List[dict]
    player: dict
    goal: dict
    events: List[dict]
    items: List[dict]
    comments: List[str]