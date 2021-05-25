import random
from typing import Type, FrozenSet, Dict
from itertools import product

from .gamestate import GameState
from .puyo.gamestate import PuyoGameState


class Game:
    name: str
    pieces: FrozenSet[bytes]
    cells: FrozenSet[bytes]

    state_cls: Type[GameState]

    interfaces: Dict[str, str]
    default_interface: str
    simulated_interface: str

    ais: Dict[str, str]
    default_ai: str

    def get_random_piece(self):
        return random.choice(list(self.pieces))


class PuyoGame:
    name = "puyo",
    pieces = frozenset(
        b''.join(pair)
        for pair in product(
            [b'r', b'g', b'b', b'y', b'p'],
            repeat=2
        )
    ),
    cells = frozenset([
        b'.', b'r', b'g', b'b', b'y', b'p', b'k'
    ]),

    state_cls = PuyoGameState,

    interfaces = {
        "ppt2": "ptai.ppt2.puyointerface.PPT2PuyoInterface",
        "simulated": "ptai.puyo.simulate.SimulatedPuyoInterface",
    }
    default_interface = "ppt2"
    simulated_interface = "simulated"

    ais = {
        "simple_greedy": "ptai.puyo.ai.SimpleGreedyAI",
        "simple_combo": "ptai.puyo.ai.SimpleComboAI",
    }
    default_ai = "simple_combo"


GAMES = {
    "puyo": PuyoGame,
}
