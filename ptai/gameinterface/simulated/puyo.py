import random

from ptai.types import GameType, Action, MoveAction
from ptai.gamestate import GameState
from ptai.gameinterface.base import GameInterface
from ptai.puyo.gamestate import PuyoGameState


class SimulatedPuyoInterface(GameInterface):
    game_type = GameType.PUYO

    def __init__(self):
        self.state = PuyoGameState()
        for _ in range(3):
            self.state.queue.append(self._get_random_piece())

    def _get_random_piece(self):
        return b''.join(random.choices(
            [b'r', b'g', b'b', b'y', b'p'],
            k=2
        ))

    def perform_action(self, action:Action):
        if isinstance(action, MoveAction):
            self.perform_move(action)
        else:
            raise NotImplementedError(f"Interface does not support action f{action}")

    def get_state(self) -> GameState:
      state = self.state.copy()
      state.new_turn = True
      print()
      print(state)
      return state

    def perform_move(self, move:MoveAction):
        result = self.state.move(move)
        if result.n_combo > 0:
            print(result.n_combo)
            print(result.n_cells_eliminated)
        self.state.queue.pop(0)
        self.state.queue.append(self._get_random_piece())
