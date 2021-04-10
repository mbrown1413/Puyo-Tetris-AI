from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class GameType(Enum):
    PUYO = "puyo"

class Action(ABC):
    pass

@dataclass
class MoveAction(Action):
    piece: bytes
    orientation: int
    x: int
    y: Optional[int] = None
    fast_down: bool = True

@dataclass
class PressButtonAction(Action):
    button: str
