import random
from typing import Union

from ptai.ai import AI, ScoreBasedAI
from ptai.types import MoveAction
from ptai.puyo.gamestate import PuyoGameState


class SimpleGreedyAI(ScoreBasedAI):
    """Very, very greedy.

    Scores each move by how many connected cells there are. Each group adds the
    square of the group size to that move's score (so a group of 1 counts as 1,
    and a group of 3 counts as 9). If any moves eliminate pieces, the one with
    the highest score is chosen. Ties are broken randomly.
    """

    def score_move(self, state:PuyoGameState, move:MoveAction) -> float:
        result = state.move(move)
        value = 0.0

        if result.n_cells_eliminated:
            value += result.score

        for x in range(6):
            for y in range(12):
                # Internal call of _get_connected. Should be okay because we
                # know this a puyo game state.
                value += len(state._get_connected(x, y))

        # Don't give yourself a game over
        if state.board[2][11] != b'.':
            value = float("-inf")

        return value


class SimpleComboAI(ScoreBasedAI):
    """
    Like the SimpleGreedyAI, but it values moves more when they have the
    potential to make combos.
    """

    def score_move(self, state:PuyoGameState, move:MoveAction) -> float:
        result = state.move(move)
        value = 0.0

        for color in (b'r', b'g', b'b', b'y', b'p'):
            for x in range(6):
                tmp_result = state.copy()._drop_beans([x], [color])
                if tmp_result.n_combo >= 2:
                    value += tmp_result.score

        if result.n_combo < 2:
            value -= result.score
        elif result.n_combo > 2:
            value += 2*result.score

        n_filled = 0
        for x in range(6):
            for y in range(12):
                value += len(state._get_connected(x, y))
                if state.board[x][y] != b'.':
                    n_filled += 1

        if n_filled > 36 or state.board[2][9] != b'.':
            value += 4*result.score

        # Don't give yourself a game over
        if state.board[0][10] != b'.' or state.board[1][10] != b'.' or state.board[2][10] != b'.' or state.board[3][10] != b'.' or state.board[4][10] != b'.' or state.board[5][10] != b'.':
            value = float("-inf")

        return value
