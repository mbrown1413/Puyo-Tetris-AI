from ptai.gameinterface.base import GameInterface
from ptai.types import PressButtonAction
from ptai.ai.base import AI

class Driver:

    def __init__(self, interface:GameInterface, ai:AI):
        self.interface = interface
        self.ai = ai

    def play(self):
        while True:
            state = self.interface.get_state()
            if state.new_turn:
                action = self.ai.get_move(state)
                if action:
                    self.interface.perform_action(action)
