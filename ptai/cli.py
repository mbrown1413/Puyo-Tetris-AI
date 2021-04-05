import argparse

from ptai.gameinterface.ppt2.puyo import PPT2PuyoInterface

def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command")
    commands.required = True

    getstate_parser = commands.add_parser("getstate",
        help="Print state of currently running game"
    )
    getstate_parser.set_defaults(func=cmd_getstate)

    args = parser.parse_args()
    args.func(args)

def cmd_getstate(args):
    interface = PPT2PuyoInterface()
    state = interface.get_game_state()
    print(state)
