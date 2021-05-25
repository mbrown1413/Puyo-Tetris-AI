import argparse
import importlib
import sys
from time import sleep
from typing import Dict

from ptai.driver import Driver
from ptai.gameinterface import GameInterface
from ptai.ai import AI
from ptai.games import GAMES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", "-g", default="puyo", choices=GAMES.keys())

    def add_interface_arg(p):
        p.add_argument("-i", "--interface", default="", help="""
            The name or full path of an interface class. Use `--interface
            help` to get a list of valid interfaces for the current game.
            The default depends on the active game type.
        """)

    def add_ai_arg(p):
        p.add_argument("-a", "--ai", default="", help="""
            The name or full path of an AI class. Use `--ai help` to get a
            list of valid AIs for the current game. The default depends on
            the active game type.
        """)

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    # Get State
    getstate_parser = commands.add_parser("getstate",
        help="Print state of currently running game"
    )
    getstate_parser.set_defaults(func=cmd_getstate)
    add_interface_arg(getstate_parser)
    getstate_parser.add_argument("--loop", action="store_true")

    # Get Move
    getmove_parser = commands.add_parser("getmove",
        help="Show the move that the AI would make"
    )
    getmove_parser.set_defaults(func=cmd_getmove)
    add_interface_arg(getmove_parser)
    add_ai_arg(getmove_parser)

    # Play
    play_parser = commands.add_parser("play",
        help="Play the game!"
    )
    play_parser.set_defaults(func=cmd_play)
    add_interface_arg(play_parser)
    add_ai_arg(play_parser)

    args = parser.parse_args()
    game = GAMES[args.game]
    args.func(game, args)

def usage_error(msg):
    print(msg, file=sys.stderr)
    sys.exit(-1)

def instantiate_class(spec_string: str,
                      shortcut_names: Dict[str, str],
                      expected_base_cls: type):
    """Import and instantiate a class.

    :arg spec_string: A string in the form "path.to.Class".
    :arg shortcut_names: Maps names that can be used as a shortcut for the
        whole import path of the class.
    :arg expected_base_cls: Base class which the given class should be a
        subclass of. This is for catching user mistakes of importing the wrong
        class.
    """
    path = shortcut_names.get(spec_string, spec_string)
    GENERIC_ERROR = 'Paths for AIs and Interfaces should be ' + \
        'dot-separated python paths. For example: ' + \
        '"path.to.module.ClassName". Use "--interface help" or "--ai help" ' + \
        'to get a list of valid ' 'interfaces or AIs.'


    if "." not in path:
        usage_error(
            f'Bad path "{spec_string}"\n' + GENERIC_ERROR
        )

    module_path, class_name = path.rsplit('.', 1)
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        usage_error(str(e) + "\n" + GENERIC_ERROR)
    try:
        cls = getattr(module, class_name, )
    except AttributeError as e:
        usage_error(str(e) + "\n" + GENERIC_ERROR)
    try:
        is_subclass = issubclass(cls, expected_base_cls)
    except TypeError:
        is_subclass = False
    if not is_subclass:
        usage_error(f'Imported {spec_string} successfully, but it is not a subclass of {expected_base_cls} as expected.\n' + GENERIC_ERROR)
    return cls()

def get_interface(game, name_or_path):
    if name_or_path == "help":
        usage_error(
            "Valid interfaces for this game: " +
            " ".join(f'"{name}"' for name in game.interfaces.keys()) + "\n" +
            "You can also specify the full path to a game interface.\n" +
            f'For example: "{list(game.interfaces.values())[0]}"'
        )
    if name_or_path == "simulated":
        name_or_path = game.simulated_interface
    if not name_or_path:
        name_or_path = game.default_interface

    return instantiate_class(
        name_or_path,
        game.interfaces,
        GameInterface,
    )

def get_ai(game, name_or_path):
    if name_or_path == "help":
        usage_error(
            "Valid AIs for this game: " +
            " ".join(f'"{name}"' for name in game.ais.keys()) + "\n" +
            "You can also specify the full path to an ai.\n" +
            f'For example: "{list(game.ais.values())[0]}"'
        )
    if not name_or_path:
        name_or_path = game.default_ai

    return instantiate_class(
        name_or_path,
        game.ais,
        AI,
    )

def cmd_getstate(game, args):
    interface = get_interface(game, args.interface)
    state = interface.get_state()
    print(state)

    while args.loop:
        sleep(0.5)
        state = interface.get_state()
        print()
        print(state)

def cmd_getmove(game, args):
    interface = get_interface(game, args.interface)
    ai = get_ai(game, args.ai)

    state = interface.get_state()
    move = ai.get_move(state)
    print("X:", move.x)
    print("Y:", move.y)
    print("Orientation:", move.orientation)

def cmd_play(game, args):
    interface = get_interface(game, args.interface)
    ai = get_ai(game, args.ai)
    driver = Driver(interface, ai)

    driver.play()
