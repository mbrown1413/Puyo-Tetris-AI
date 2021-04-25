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
        self._prev_queue:Optional[tuple] = None
        self._queue_changed = True
        self._expected_pair = None

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

        # Detect changes in the next puyo queue since the last new turn
        queue = tuple(state.queue)
        if queue != self._prev_queue:
            self._queue_changed = True
            # When the queue changes, we mark down what the previous state's
            # next pair was going to be. This is because the game updates the
            # next pair before it updates the currently falling pair. We'll use
            # this to double check that we've actually seen a new state.
            if not self._expected_pair and self._prev_queue:
                self._expected_pair = self._prev_queue[1]
        self._prev_queue = queue

        # Detect new turn
        if (
            # (2, 11) is where the falling pair starts
            state.current_position == (2, 11) and \
            # If the queue hasn't changed since the last new turn, the odds are
            # very low that we're on a new turn.
            self._queue_changed and \
            # The current pair must be the same as what we're expecting to come
            # from the queue. Things work alright without this, but there are
            # some edge cases it catches.
            (self._expected_pair is None or queue[0] == self._expected_pair)
        ):
            state.new_turn = True
            self._queue_changed = False
            self._expected_pair = None

        self.switch.set_sleep_time(8)
        return state

    def perform_move(self, move:MoveAction):
        delta_x = move.x - 2

        # Rotation
        if move.orientation == 0:
            rotation_key = None
            rotation_count = 0
        elif move.orientation == 1:
            rotation_key = "A"
            rotation_count = 1
        elif move.orientation == 2:
            rotation_key = "A"
            rotation_count = 2
        elif move.orientation == 3:
            rotation_key = "B"
            rotation_count = 1

            # Since rotation point is the bottom bean, this effectively moves
            # the piece to the left.
            delta_x += 1

        # Direction
        direction_count = abs(delta_x)
        direction_key = "DRIGHT" if delta_x > 0 else "DLEFT"

        # Press buttons, alternating between rotation and direction
        self.switch.set_sleep_time(20)
        for _ in range(3):
            if rotation_count > 0:
                self.switch.press_button(rotation_key)
                rotation_count -= 1

            if direction_count > 0:
                self.switch.press_button(direction_key)
                direction_count -= 1

        #TODO: Double check that we moved correctly by calling get_state()
        #      before doing fast down.

        # Fast down
        if move.fast_down:
            self.switch.press_button("DUP")

        self.switch.set_sleep_time(8)
