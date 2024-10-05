from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CharacterData:
    name: str
    role: str
    description: str

@dataclass
class ItemData:
    name: str
    type: str
    description: str

@dataclass
class LocationData:
    name: str
    stance: str
    description: str
    relationships: List[str]
    characters: Optional[List[CharacterData]] = None
    items: Optional[List[ItemData]] = None
