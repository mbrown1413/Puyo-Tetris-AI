from abc import ABC

from ptai.actions import Action
from ptai.gamestate import GameState


class GameInterface(ABC):

    def perform_action(self, action:Action):
        raise NotImplementedError()

    def get_state(self) -> GameState:
        raise NotImplementedError()
