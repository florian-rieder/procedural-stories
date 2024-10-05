from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Character:
    name: str
    role: str
    description: str

@dataclass
class Item:
    name: str
    type: str
    description: str

@dataclass
class Location:
    name: str
    stance: str
    description: str
    relationships: List[str]
    characters: Optional[List[Character]] = None
    items: Optional[List[Item]] = None
