import argparse
from time import sleep

from ptai.gameinterface.ppt2.puyo import PPT2PuyoInterface
from ptai.ai.generic import RandomAI
from ptai.driver import Driver

def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command")
    commands.required = True

    # Get State
    getstate_parser = commands.add_parser("getstate",
        help="Print state of currently running game"
    )
    getstate_parser.set_defaults(func=cmd_getstate)
    getstate_parser.add_argument("--loop", action="store_true")

    # Get Move
    getmove_parser = commands.add_parser("getmove",
        help="Show the move that the AI would make"
    )
    getmove_parser.set_defaults(func=cmd_getmove)

    # Play
    play_parser = commands.add_parser("play",
        help="Play the game!"
    )
    play_parser.set_defaults(func=cmd_play)

    args = parser.parse_args()
    args.func(args)

def cmd_getstate(args):
    interface = PPT2PuyoInterface()
    state = interface.get_state()
    print(state)

    while args.loop:
        sleep(0.5)
        state = interface.get_state()
        print()
        print(state)

def cmd_getmove(args):
    interface = PPT2PuyoInterface()
    ai = RandomAI()

    state = interface.get_state()
    move = ai.get_move(state)
    print("X:", move.x)
    print("Y:", move.y)
    print("Orientation:", move.orientation)

def cmd_play(args):
    interface = PPT2PuyoInterface()
    ai = RandomAI()
    driver = Driver(interface, ai)
    driver.play()
