import numpy
from typing import Iterable

from ptai.gamestate import GameState
from ptai.types import GameType, MoveAction


class PuyoGameState(GameState):
    game_type = GameType.PUYO

    cell_colors = {
        b'.': (255, 255, 255),
        b'r': (0, 0, 255),
        b'g': (0, 255, 0),
        b'b': (200, 200, 0),
        b'y': (0, 255, 255),
        b'p': (128, 0, 128),
        b'k': (0, 0, 0),
    }

    def __init__(self, board=None, queue=None, new_turn=False):
        if board is None:
            board = numpy.array([[b'.' for y in range(12)]
                                       for x in range(6)], dtype="|S1")
        else:
            board = numpy.array(board, dtype="|S1")
        assert board.shape == (6, 12)

        super().__init__(board, queue or [], new_turn)

    def __str__(self):
        lines = []
        for i, y in enumerate(range(self.board.shape[1]-1, -1, -1)):
            line = ' '.join(
                self.board[x][y].decode()
                for x in range(self.board.shape[0])
            )

            # Puyo Queue
            if i < 2:
                line += "  " + ''.join(chr(pair[i]) for pair in self.queue)

            lines.append(line)

            # Line dividing visible and non-visible parts of the grid
            #TODO
            #if y == 2:
            #    lines.append('-'*11)

        return '\n'.join(lines)

    def copy(self) -> "PuyoGameState":
        return PuyoGameState(self.board, self.queue)

    def move(self, move: MoveAction) -> None:
        assert self.queue.length > 0 and move.piece == self.queue[0]
        raise NotImplementedError()

    def get_moves(self) -> Iterable[MoveAction]:
        piece = self.queue[0]
        for orientation in range(4):
            for x in range(5 if orientation%2 else 6):
                y = None  # Puyo doesn't use Y because of its gravity rules
                move = MoveAction(piece, orientation, x, y)
                if self.can_make_move(move):
                    yield move

    def can_make_move(self, move:MoveAction):
        """Return True if the move can be made, False otherwise."""

        # Is this even a valid move?
        assert move.orientation in range(4)
        if move.orientation % 2 == 0:
            assert move.orientation in range(6)
        else:
            assert move.orientation in range(5)

        # Any beans blocking the path?
        if move.orientation == 2 and move.orientation == 0:
            # This move is always possible. If this column is completely
            # filled, this move results in a game over.
            return True
        elif move.orientation >= 2:
            pos_range = list(range(2, move.orientation+1 + move.orientation%2))
        else:
            pos_range = list(range(2, move.orientation-1, -1))
        for i in pos_range:
            if self.board[i][11] != b'.':
                return False

        # Make sure there is room to rotate the beans
        if move.orientation != 0 and self.board[1][11] != b'.' and \
                             self.board[3][11] != b'.':
            return False

        return True
