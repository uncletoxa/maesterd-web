import logging
from dataclasses import dataclass, field
from typing import List, Dict
from maesterd.models import constants
from pydantic import conint

logger = logging.getLogger(__name__)


@dataclass
class Character:
    name: str
    race: constants.RACES
    character_class: constants.CHARACTER_CLASSES
    background: constants.BACKGROUNDS
    alignment: constants.ALIGNMENTS
    experience_points: conint(ge=0) = 0


@dataclass
class Stats:
    abilities: Dict[constants.ABILITIES, conint(ge=1, le=20)] = field(
        default_factory=lambda: {key: 10 for key in constants.ABILITIES.__args__},
        metadata={"description": "Character's abilities (Strength, Dexterity, etc.)"},
    )
    saving_throws: Dict[constants.ABILITIES, conint(ge=-5, le=10)] = field(
        init=False, metadata={"description": "Character's saving throw modifiers for each ability"}
    )
    skills: Dict[constants.SKILLS, conint(ge=-5, le=10)] = field(
        init=False, metadata={"description": "Character's skill modifiers (Acrobatics, Stealth, etc.)"}
    )


@dataclass
class Inventory:
    equipment: Dict[str, str] = field(
        default_factory=dict,
        metadata={"description": "A dictionary of equipment and its descriptions (e.g. weapon, armor)"},
    )
    currency: Dict[str, int] = field(
        default_factory=lambda: {"CP": 0, "SP": 0, "EP": 0, "GP": 0, "PP": 0},
        metadata={"description": "Currency the character has"},
    )
    items: List[str] = field(default_factory=list, metadata={"description": "List of items the character possesses"})


@dataclass
class Traits:
    personality_traits: str
    ideals: str
    bonds: str
    flaws: str


@dataclass
class HP:
    current: int
    max: int


@dataclass
class CharState:
    hp: HP
    ac: int
    is_alive: bool


@dataclass
class PC:
    character: Character
    stats: Stats
    inventory: Inventory
    traits: Traits
    state: CharState


@dataclass
class NPC:
    character: Character
    state: CharState
