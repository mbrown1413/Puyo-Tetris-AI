from abc import ABC
from typing import Generator

from ptai.types import GameType, Action
from ptai.gamestate import GameState


class GameInterface(ABC):
    game_type: GameType

    def perform_action(self, action:Action):
        raise NotImplementedError()

    def get_state(self) -> GameState:
        raise NotImplementedError()
