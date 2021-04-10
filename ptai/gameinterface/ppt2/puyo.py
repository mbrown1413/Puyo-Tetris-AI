from typing import Optional

from ptai.types import GameType, Action, PressButtonAction, MoveAction
from ptai.gamestate import GameState
from ptai.gameinterface.base import GameInterface
from ptai.gameinterface.switch import Switch
from ptai.gameinterface.switchtypes import Pointer
from ptai.gameinterface.ppt2.puyotypes import MainStruct

MAIN_POINTER = 0x1625840


class PPT2PuyoInterface(GameInterface):
    game_type = GameType.PUYO

    def __init__(self, player:int=0):
        self.player = player
        self.switch = Switch()

        self._previous_queue:Optional[tuple] = None

    def perform_action(self, action:Action):
        if isinstance(action, PressButtonAction):
            self.switch.press_button(action.button)
        elif isinstance(action, MoveAction):
            self.perform_move(action)
        else:
            raise NotImplementedError(f"Interface does not support action f{action}")

    def get_state(self) -> GameState:
        self.switch.set_sleep_time(0)

        pointer = Pointer(MAIN_POINTER, "main")
        main_pointer = pointer.deref(self.switch, MainStruct.pointer_t)
        player_pointer = main_pointer.deref_field(self.switch, f"player{self.player}")
        player = player_pointer.deref(self.switch)
        state = player.get_game_state(self.switch)

        #TODO: If a puyo pair is repeated, new_turn is not set. Use current x/y
        #      instead? Just account for pieces being able to be bumped up when
        #      rotated.
        queue = tuple(state.queue[0])
        if queue != self._previous_queue and self._previous_queue is not None:
            state.new_turn = True
        self._previous_queue = queue

        self.switch.set_sleep_time(16)
        return state

    def perform_move(self, move:MoveAction):

        # Rotation
        #TODO: Press B to rotate if orientation == 3
        for _ in range(abs(move.orientation)):
            self.perform_action(
                PressButtonAction("A")
            )

        # Left / right
        direction_key = "DRIGHT" if move.x > 1 else "DLEFT"
        for _ in range(abs(move.x - 2)):
            self.perform_action(
                PressButtonAction(direction_key)
            )

        # Fast down
        if move.fast_down:
            self.perform_action(
                PressButtonAction("DUP")
            )

        #TODO: Double check that we moved correctly by calling get_state()
