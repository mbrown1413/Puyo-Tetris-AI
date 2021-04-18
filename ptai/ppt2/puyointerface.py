from typing import Optional

from ptai.actions import Action, PressButtonAction, MoveAction
from ptai.gamestate import GameState
from ptai.gameinterface import GameInterface
from ptai.ppt2.switch import Switch
from ptai.ppt2.switchtypes import Pointer
from ptai.ppt2.puyotypes import MainStruct

MAIN_POINTER = 0x1625840


class PPT2PuyoInterface(GameInterface):

    def __init__(self, player:int=0, switch:Switch=None):
        self.player = player
        if switch is None:
            self.switch = Switch()
        else:
            self.switch = switch

        self.switch.send_command("configure buttonClickSleepTime 20")
        self.switch.set_sleep_time(8)
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

        self.switch.set_sleep_time(8)
        return state

    def perform_move(self, move:MoveAction):
        delta_x = move.x - 2

        # Rotation
        if move.orientation == 0:
            pass
        elif move.orientation == 1:
            self.perform_action(PressButtonAction("A"))
        elif move.orientation == 2:
            self.perform_action(PressButtonAction("A"))
            self.perform_action(PressButtonAction("A"))
        elif move.orientation == 3:
            self.perform_action(PressButtonAction("B"))

            # Since rotation point is the bottom bean, this effectively moves
            # the piece to the left.
            delta_x += 1

        # Left / right
        direction_key = "DRIGHT" if delta_x > 0 else "DLEFT"
        for _ in range(abs(delta_x)):
            self.perform_action(PressButtonAction(direction_key))

        #TODO: Double check that we moved correctly by calling get_state()
        #      before doing fast down.

        # Fast down
        if move.fast_down:
            self.perform_action(PressButtonAction("DUP"))
