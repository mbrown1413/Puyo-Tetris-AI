"""
Memory structures for Puyo Puyo Tetris 2 pertaining to Puyo.
"""
from enum import Enum

import numpy

from ptai.ppt2.switchtypes import SwitchType, Struct, AbstractArray, make_array_t, UInt32, UInt8


class PUYO(Enum):
    BLANK =  b'.'
    RED =    b'r'
    GREEN =  b'g'
    BLUE =   b'b'
    YELLOW = b'y'
    PURPLE = b'p'
    BLACK =  b'k'
    UNKNOWN =  b'?'


class Puyo(SwitchType):
    """
    Represents one puyo, or a blank spot in a grid of puyos.

    Consists of 4 bytes. First is the puyo color. The next 3 bytes are unknown,
    but they are zero in list of next puyos and set to values in the puyo grid.
    """
    size = 4

    INT_TO_COLOR = {
        0: PUYO.BLANK,
        1: PUYO.RED,
        2: PUYO.GREEN,
        3: PUYO.BLUE,
        4: PUYO.YELLOW,
        5: PUYO.PURPLE,
        6: PUYO.BLACK
    }

    def __init__(self, color:PUYO, raw_bytes:bytes):
        self.color = color
        self.raw_bytes = raw_bytes

    def __str__(self):
        #return self.byte.decode()
        return f"{self.byte.decode()}:{self.raw_bytes[1:2].hex()}:{self.raw_bytes[2:3].hex()}:{self.raw_bytes[3:4].hex()}"

    @classmethod
    def from_bytes(cls, data:bytes):
        assert len(data) == cls.size
        try:
            color = cls.INT_TO_COLOR[data[0]]
        except KeyError:
            color = PUYO.UNKNOWN
        return cls(color, data)

    @property
    def byte(self):
        return self.color.value


class PuyoGrid(AbstractArray):
    """
    A grid of puyos making up the game board.

    Puyos are stored as you would read an (English) book: left to right, top to
    bottom. While the visible game board size is 6x12, the actual grid stored
    in this type is 8 wide and 15 tall. This includes:
     * 4 bytes of extra data on both the left and right of each row.
     * 3 rows above the viewable screen.
    """
    base_type_cls = Puyo
    count = 8*15
    size = count * Puyo.size

    def __str__(self):
        lines = []
        for y in range(15):
            line = ' '.join(
                str(self.objects[x + y*8])
                for x in range(1, 7)
            )
            lines.append(line)

            # Line dividing visible and non-visible parts of the grid
            if y == 2:
                lines.append('-'*11)

        return '\n'.join(lines)

    def format_reachable_data(self, switch):
        return str(self)

    def get_byte_array(self):
        """Return byte array with origin at bottom left."""
        return numpy.array([
            [self[x + y*8].byte for y in range(14, 2, -1)]
            for x in range(1, 7)
        ], dtype="|S1")


class Struct3(Struct):
    fields = (
        Struct.Field(name="puyo_grid", type=PuyoGrid.pointer_t, offset=0x58),
    )


class Struct1(Struct):
    fields = (
        Struct.Field(name="struct3", type=Struct3.pointer_t, offset=0x88),
    )


class Board(Struct):
    fields = (
        Struct.Field(name="struct1", type=Struct1.pointer_t, offset=0x18),
        Struct.Field(name="current_puyo_pair", type=make_array_t(Puyo, 2), offset=0xA8),
        # Rotation: 0-3, positive is clockwise
        Struct.Field(name="current_rotation", type=UInt8, offset=0xF4),
        # X/Y: Position of the puyo which is initially on bottom. This is the
        #   one that is the center of the rotation. The origin is upper left
        #   including the non-visible part of the grid above the screen, and
        #   including the padding on the left, so X is effectively one indexed.
        #   Start: (3, 3)
        #   X: 1-6
        #   Y: 3-14
        Struct.Field(name="current_x", type=UInt8, offset=0xF8),
        Struct.Field(name="current_y", type=UInt8, offset=0xF9),
    )


class Struct2(Struct):
    fields = (
        Struct.Field(name="next_puyo_pair", type=make_array_t(Puyo, 2), offset=0xB4),
        Struct.Field(name="next_next_puyo_pair", type=make_array_t(Puyo, 2), offset=0xEC),
    )


class PuyoPlus2Bytes(Struct):
    fields = (
        Struct.Field(name="puyo", type=Puyo),
        Struct.Field(name="extra_data", type=make_array_t(UInt8, 20)),
    )


class PuyoGrid2(AbstractArray):
    """
    A grid of puyos making up the game board.

    Puyos are stored as you would read an (English) book: left to right, top to
    bottom. While the visible game board size is 6x12, the actual grid stored
    in this type is 8 wide and 15 tall. This includes:
     * 4 bytes of extra data on both the left and right of each row.
     * 3 rows above the viewable screen.
    """
    base_type_cls = PuyoPlus2Bytes
    count = 8*15
    size = count * PuyoPlus2Bytes.size

    def __str__(self):
        lines = []
        for y in range(15):
            line = ' '.join(
                str(self.objects[x + y*8].get_field("puyo"))
                for x in range(1, 7)
            )
            lines.append(line)

            # Line dividing visible and non-visible parts of the grid
            if y == 2:
                lines.append('-'*11)

        return '\n'.join(lines)

    def format_reachable_data(self, switch):
        return str(self)


class Board2(Struct):
    fields = (
        #Struct.Field(name="board", type=make_array_t(Puyo, 564), offset=0xA98-(18*88)),
        Struct.Field(name="board", type=PuyoGrid2, offset=0xA98-(0x18*88)-24-192*3),
    )


class Struct5(Struct):
    fields = (
        Struct.Field(name="board", type=Board2.pointer_t, offset=0x110),
    )


class Struct4(Struct):
    fields = (
        Struct.Field(name="struct5", type=Struct5.pointer_t, offset=0x38),
    )


class PlayerGameState(Struct):
    """All state for a given player.

    Initially, before the game has actually started, the game state will look
    like this:
    * Board: Empty
    * Current pair: (blank, blank)
    * Current position: (-1, 14)
    * Next pair: The pairs which will drop on the first turn.
    * Next next pair: The pairs which will drop on the second turn.

    When a new turn is starting, this state changes in the following order:
    1. Falling piece is placed on board. (skipped on start of the first turn)
    2. Queue shifts:
        * Next pair = Next next pair
        * Next next pair = New pair
    3. New turn actually starts:
        * Current pair = Old next pair
        * Current position = (2, 11)
    """
    fields = (
        Struct.Field(name="frame_counter", type=UInt32, offset=0x6C),
        Struct.Field(name="struct2", type=Struct2.pointer_t, offset=0x98),
        Struct.Field(name="board", type=Board.pointer_t, offset=0xA0),
        Struct.Field(name="struct4", type=Struct4.pointer_t, offset=0x30),
    )

    def get_game_state(self, switch):
        board = self["board"].deref(switch)
        grid_pointer = board["struct1"].deref_field(
            switch, "struct3"
        ).deref_field(
            switch, "puyo_grid"
        )
        grid = grid_pointer.deref(switch)
        struct2 = self["struct2"].deref(switch)

        from ptai.puyo.gamestate import PuyoGameState
        return PuyoGameState(
            grid.get_byte_array(),
            [
                board["current_puyo_pair"][0].byte + board["current_puyo_pair"][1].byte,
                struct2["next_puyo_pair"][1].byte + struct2["next_puyo_pair"][0].byte,
                struct2["next_next_puyo_pair"][1].byte + struct2["next_next_puyo_pair"][0].byte,
            ],
            current_position=(
                # Convert to bottom left origin, without padding.
                board["current_x"].value - 1,
                14 - board["current_y"].value
            ),
        )


class MainStruct(Struct):
    fields = (
        # These will be null pointers if no game is being played
        Struct.Field(name="player0", type=PlayerGameState.pointer_t, offset=0x208),
        Struct.Field(name="player1", type=PlayerGameState.pointer_t, offset=0x220),
        Struct.Field(name="player2", type=PlayerGameState.pointer_t, offset=0x238),
        Struct.Field(name="player3", type=PlayerGameState.pointer_t, offset=0x250),
    )
