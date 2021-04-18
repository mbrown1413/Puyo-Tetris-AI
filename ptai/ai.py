from abc import ABC, abstractmethod
import random
from typing import Union

from ptai.actions import MoveAction
from ptai.gamestate import GameState


class AI(ABC):

    @abstractmethod
    def get_move(self, state:GameState) -> MoveAction:
        # State may not have new_turn==True, since the driver could
        # speculatively ask for a move from the AI.
        raise NotImplementedError()


class RandomAI(AI):
    """AI that makes completely random moves."""

    def get_move(self, state:GameState) -> MoveAction:
        possible_moves = list(state.get_moves())
        move = random.choice(possible_moves)
        move.fast_down = False
        return move


class ScoreBasedAI(AI):
    """Abstract class for an AI that works by scoring each possible move."""

    def get_move(self, state:GameState) -> MoveAction:
        def score_func(move):
            return self.score_move(state.copy(), move)
        moves = list(state.get_moves())
        random.shuffle(moves)  # Select randomly between ties
        return max(moves, key=score_func)

    def score_move(self, state:GameState, move:MoveAction) -> Union[int, float]:
        """Return a score for a particular move."""
        raise NotImplementedError()
