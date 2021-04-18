from ptai.actions import MoveAction
from .puyointerface import PPT2PuyoInterface
from ptai.ppt2.switch import Switch


class MockSwitch(Switch):

    def __init__(self, *args, **kwargs):
        self.key_presses = []

    def press_button(self, button):
        self.key_presses.append(button)

    def send_command(self, command):
        pass


def test_perform_move():
    mock_switch = MockSwitch()
    interface = PPT2PuyoInterface(switch=mock_switch)

    testdata = [
        # rotation=0
        (MoveAction(b'rr', 0, 0), ["DLEFT", "DLEFT", "DUP"]),
        (MoveAction(b'rr', 0, 1), ["DLEFT", "DUP"]),
        (MoveAction(b'rr', 0, 2), ["DUP"]),
        (MoveAction(b'rr', 0, 3), ["DRIGHT", "DUP"]),
        (MoveAction(b'rr', 0, 4), ["DRIGHT", "DRIGHT", "DUP"]),
        (MoveAction(b'rr', 0, 5), ["DRIGHT", "DRIGHT", "DRIGHT", "DUP"]),

        # rotation=1
        (MoveAction(b'rr', 1, 0), ["A", "DLEFT", "DLEFT", "DUP"]),
        (MoveAction(b'rr', 1, 2), ["A", "DUP"]),
        (MoveAction(b'rr', 1, 4), ["A", "DRIGHT", "DRIGHT", "DUP"]),

        # rotation=2
        (MoveAction(b'rr', 2, 0), ["A", "A", "DLEFT", "DLEFT", "DUP"]),
        (MoveAction(b'rr', 2, 1), ["A", "A", "DLEFT", "DUP"]),
        (MoveAction(b'rr', 2, 2), ["A", "A", "DUP"]),
        (MoveAction(b'rr', 2, 3), ["A", "A", "DRIGHT", "DUP"]),
        (MoveAction(b'rr', 2, 4), ["A", "A", "DRIGHT", "DRIGHT", "DUP"]),
        (MoveAction(b'rr', 2, 5), ["A", "A", "DRIGHT", "DRIGHT", "DRIGHT", "DUP"]),

        # rotation=3
        (MoveAction(b'rr', 3, 0), ["B", "DLEFT", "DUP"]),
        (MoveAction(b'rr', 3, 1), ["B", "DUP"]),
        (MoveAction(b'rr', 3, 2), ["B", "DRIGHT", "DUP"]),
        (MoveAction(b'rr', 3, 3), ["B", "DRIGHT", "DRIGHT", "DUP"]),
        (MoveAction(b'rr', 3, 4), ["B", "DRIGHT", "DRIGHT", "DRIGHT", "DUP"]),

        # fast_down=False
        (MoveAction(b'rr', 0, 2, fast_down=False), []),
        (MoveAction(b'rr', 0, 3, fast_down=False), ["DRIGHT"]),
    ]

    for move, expected_keys in testdata:
        mock_switch.key_presses = []
        interface.perform_action(move)
        assert mock_switch.key_presses == expected_keys
