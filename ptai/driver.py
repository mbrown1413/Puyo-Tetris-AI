from ptai.gameinterface import GameInterface
from ptai.ai import AI

class Driver:

    def __init__(self, interface:GameInterface, ai:AI):
        self.interface = interface
        self.ai = ai

    def play(self, max_turns=float("inf")):
        expected_next_state = None
        last_move = None
        last_state = None
        n_turns = 0
        while n_turns <= max_turns:
            state = self.interface.get_state()
            if state.new_turn:
                n_turns += 1

                if expected_next_state:
                    # Check if the previous move was performed correctly
                    #TODO: Account for nuisance
                    if not (state.board == expected_next_state.board).all():
                        print()
                        print("Move performed incorrectly!")
                        print("Move:", last_move)
                        print("Before move:")
                        print(last_state)
                        print("Expected:")
                        print(expected_next_state)
                        print("Actual:")
                        print(state)
                        print()

                action = self.ai.get_move(state)
                expected_next_state = None
                if action:
                    self.interface.perform_action(action)

                    # Record the expected next board given the current state
                    # and the move given
                    last_state = state
                    expected_next_state = state.copy()
                    expected_next_state.move(action)
                    last_move = action
