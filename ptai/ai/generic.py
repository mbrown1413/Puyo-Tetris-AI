import random

from ptai.ai.base import AI
from ptai.types import MoveAction
from ptai.gamestate import GameState


class RandomAI(AI):
    """AI that makes completely random moves."""

    def get_move(self, state:GameState) -> MoveAction:
        possible_moves = list(state.get_moves())
        move = random.choice(possible_moves)
        move.fast_down = False
        return move
