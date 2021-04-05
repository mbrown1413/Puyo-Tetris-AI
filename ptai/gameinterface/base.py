from abc import ABC
from typing import Generator

from ptai.types import GameType, Action
from ptai.gamestate import GameState


class GameInterface(ABC):
    game_type: GameType

    def perform_action(self, action:Action):
        raise NotImplementedError()

    def get_game_state(self) -> GameState:
        raise NotImplementedError()

    async def get_game_updates(self) -> Generator[GameState, None, None]:
        #TODO: Default implementation of this that calls get_game_state()
        raise NotImplementedError()
