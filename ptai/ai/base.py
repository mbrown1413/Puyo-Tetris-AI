from abc import ABC, abstractmethod

from ptai.types import MoveAction
from ptai.gamestate import GameState


class AI(ABC):

    @abstractmethod
    def get_move(self, state:GameState) -> MoveAction:
        # State may not have new_turn==True, since the driver could
        # speculatively ask for a move from the AI.
        raise NotImplementedError()
