from ptai.types import GameType, Action, ButtonPressAction
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

    def perform_action(self, action:Action):
        raise NotImplementedError(f"Interface does not support action f{action}")

    def get_game_state(self) -> GameState:
        pointer = Pointer(MAIN_POINTER, "main")
        main_pointer = pointer.deref(self.switch, MainStruct.pointer_t)
        player_pointer = main_pointer.deref_field(self.switch, f"player{self.player}")
        player = player_pointer.deref(self.switch)
        return player.get_game_state(self.switch)
