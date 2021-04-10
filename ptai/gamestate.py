from abc import ABC, abstractmethod
from typing import Iterable, List, Dict, Tuple

import numpy

from ptai.types import GameType, MoveAction


class GameState(ABC):
    """Abstract class for the state of a falling block puzzle game.

    The board is represented as a 2 dimensional array of bytes with the origin
    at the bottom left. The queue of pieces includes the piece currently
    falling, i.e. a pop(0) is performed on the queue when move() is called.
    """
    game_type: GameType

    # Map cell value to tuple of (red, green, blue) color to draw.
    cell_colors: Dict[bytes, Tuple[int, int, int]]

    def __init__(self, board, queue, new_turn):
        assert isinstance(board, numpy.ndarray)
        assert board.dtype == "|S1"
        assert len(board.shape) == 2
        assert all(isinstance(piece, bytes) for piece in queue)

        self.board:numpy.ndarray = board
        self.queue:List[bytes] = queue
        self.new_turn:bool = new_turn

    ############################
    ##### Abstract Methods #####
    ############################

    @abstractmethod
    def copy(self) -> "GameState":
        raise NotImplementedError()

    @abstractmethod
    def move(self, move: MoveAction) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_moves(self) -> Iterable[MoveAction]:
        raise NotImplementedError()

    ##########################
    ##### Helper Methods #####
    ##########################

    def format_board(self):
        lines = []
        for y in range(self.board.shape[1]):
            lines.append(' '.join(
                self.board[x + y*self.board.shape[0]].decode()
                for x in range(self.board.shape[0])
            ))

            # Line dividing visible and non-visible parts of the grid
            #TODO
            # if y == ?:
            #     lines.append('-'.join('-'*self.board.shape[0]))

        return '\n'.join(lines)

    def draw_board(self):
        raise NotImplementedError()
