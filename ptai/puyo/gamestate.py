import numpy
from typing import Iterable

from ptai.gamestate import GameState, MoveResult
from ptai.actions import MoveAction


# Score calculation tables
CHAIN_POWER_TABLE = (0, 8, 16, 32, 64, 128, 256, 512, 999)
COLOR_BONUS_TABLE = (0, 0, 3, 6, 12, 24)
GROUP_BONUS_TABLE = (0, 0, 0, 0, 0, 2, 3, 4, 5, 6, 7, 10)


class PuyoGameState(GameState):

    cell_colors = {
        b'.': (255, 255, 255),
        b'r': (0, 0, 255),
        b'g': (0, 255, 0),
        b'b': (200, 200, 0),
        b'y': (0, 255, 255),
        b'p': (128, 0, 128),
        b'k': (0, 0, 0),
    }

    def __init__(self, board=None, queue=None, new_turn=False, current_position=None):
        """
        Args additional to superclass:
        * current_position - (x, y) of the currently falling piece.
        """
        if board is None:
            board = numpy.array([[b'.' for y in range(12)]
                                       for x in range(6)], dtype="|S1")
        else:
            board = numpy.array(board, dtype="|S1")
        assert board.shape == (6, 12)

        super().__init__(board, queue or [], new_turn)
        self.current_position = current_position

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
        return PuyoGameState(self.board, self.queue, self.new_turn)

    def move(self, move: MoveAction) -> MoveResult:
        assert self._can_make_move(move)
        assert len(move.piece) == 2
        pair = [move.piece[0:1], move.piece[1:2]]

        for bean in pair:
            assert bean in {b'r', b'g', b'b', b'y', b'p'}

        if move.x == 2 and move.orientation == 0 and self.board[2][11] != b'.':
            # This column is filled, so it's the only valid move, and results
            # in a game over.
            #return Combo(0, 0, 0, True)
            return MoveResult(0, 0, 0, True)

        # Force orientation to be 0 or 1, switching order of pair if needed.
        if move.orientation > 1:
            orientation = move.orientation - 2
        else:
            orientation = move.orientation
            pair = pair[::-1]

        if orientation == 0:
            return self._drop_beans((move.x, move.x), pair)
        else:
            return self._drop_beans((move.x, move.x+1), pair)

    def get_moves(self) -> Iterable[MoveAction]:
        piece = self.queue[0]
        for orientation in range(4):
            for x in range(5 if orientation%2 else 6):
                y = None  # Puyo doesn't use Y because of its gravity rules
                move = MoveAction(piece, orientation, x, y)
                if self._can_make_move(move):
                    yield move


    ############################
    ##### Internal Methods #####
    ############################

    def _can_make_move(self, move:MoveAction):
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

    def _drop_beans(self, xs, beans) -> MoveResult:
        for x, bean in zip(xs, beans):
            self._drop(x, bean)

        total_score = 0
        total_n_beans = 0
        for i in range(25):  # Shouldn't be possible to have more than a 25-combo
            n_beans, n_colors, group_bonus = self._eliminate_beans()
            if n_beans == 0:
                break

            self._do_gravity()

            # Calculate Score
            # Based on: http://puyonexus.net/wiki/Scoring
            if i >= len(CHAIN_POWER_TABLE):
                chain_power = CHAIN_POWER_TABLE[-1]
            else:
                chain_power = CHAIN_POWER_TABLE[i]
            color_bonus = COLOR_BONUS_TABLE[n_colors]
            multiplier = chain_power + color_bonus + group_bonus
            multiplier = max(1, min(999, multiplier))
            score = 10 * n_beans * multiplier

            total_score += score
            total_n_beans += n_beans

        return MoveResult(
            score=total_score,
            n_combo=i,
            n_cells_eliminated=total_n_beans,
        )

    def _drop(self, x, bean):
        for y in range(12):
            if self.board[x][y] == b'.':
                self.board[x][y] = bean
                break

    def _eliminate_beans(self):

        def eliminate_if_black_bean(x, y):
            if x < 0 or x > 5 or y < 0 or y > 11:
                return
            if self.board[x][y] == b'k':
                self.board[x][y] = b'.'

        n_beans = 0
        colors_eliminated = set()
        group_bonus = 0
        for x in range(6):
            for y in range(12):
                if self.board[x][y] == b'.' or self.board[x][y] == b'k':
                    continue
                coordinates = self._get_connected(x, y)
                if len(coordinates) < 4:
                    continue

                colors_eliminated.add(self.board[x][y])
                if len(coordinates) >= len(GROUP_BONUS_TABLE):
                    group_bonus += GROUP_BONUS_TABLE[-1]
                else:
                    group_bonus += GROUP_BONUS_TABLE[len(coordinates)]

                for x, y in coordinates:
                    eliminate_if_black_bean(x-1, y)
                    eliminate_if_black_bean(x+1, y)
                    eliminate_if_black_bean(x, y-1)
                    eliminate_if_black_bean(x, y+1)
                    self.board[x][y] = b'.'
                    n_beans += 1

        return n_beans, len(colors_eliminated), group_bonus

    def _get_connected(self, x, y):
        """Return a list of coordinates connected by color to (x, y)."""
        color = self.board[x][y]
        if color == b' ' or color == b'k':
            return []

        visited = set()

        def visit(x, y):
            if (x, y) in visited:
                return
            if x < 0 or x >= 6 or y < 0 or y >= 12:
                return
            if self.board[x][y] == color:
                visited.add((x, y))

                visit(x-1, y)
                visit(x+1, y)
                visit(x, y-1)
                visit(x, y+1)

        visit(x, y)
        return list(visited)

    def _do_gravity(self):
        """Make floating beans fall."""
        for x in range(6):
            lowest_free_y = 0
            for y in range(12):

                if self.board[x][y] != b'.':
                    tmp = self.board[x][lowest_free_y]
                    self.board[x][lowest_free_y] = self.board[x][y]
                    self.board[x][y] = tmp

                    lowest_free_y += 1
