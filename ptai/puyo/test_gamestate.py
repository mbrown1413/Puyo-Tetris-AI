from ptai.types import MoveAction
from ptai.gamestate import MoveResult
from . import gamestate


def test_simple_moves():
    state = gamestate.PuyoGameState(queue=[b'rg']*4)
    assert (state.board[0][0:2] == [b'.', b'.']).all()
    assert (state.board[1][0:2] == [b'.', b'.']).all()
    assert (state.board[2][0:2] == [b'.', b'.']).all()
    assert (state.board[3][0:2] == [b'.', b'.']).all()

    result = state.move(MoveAction(b'rg', 0, 0))
    assert (state.board[0][0:2] == [b'g', b'r']).all()
    assert (state.board[1][0:2] == [b'.', b'.']).all()
    assert (state.board[2][0:2] == [b'.', b'.']).all()
    assert (state.board[3][0:2] == [b'.', b'.']).all()
    assert result == gamestate.MoveResult(
        score=0,
        n_combo=0,
        n_cells_eliminated=0,
        game_over=False,
    )

    result = state.move(MoveAction(b'rg', 0, 1))
    assert (state.board[0][0:2] == [b'g', b'r']).all()
    assert (state.board[1][0:2] == [b'g', b'r']).all()
    assert (state.board[2][0:2] == [b'.', b'.']).all()
    assert (state.board[3][0:2] == [b'.', b'.']).all()
    assert result == gamestate.MoveResult(
        score=0,
        n_combo=0,
        n_cells_eliminated=0,
        game_over=False,
    )

    result = state.move(MoveAction(b'rg', 0, 2))
    assert (state.board[0][0:2] == [b'g', b'r']).all()
    assert (state.board[1][0:2] == [b'g', b'r']).all()
    assert (state.board[2][0:2] == [b'g', b'r']).all()
    assert (state.board[3][0:2] == [b'.', b'.']).all()
    assert result == gamestate.MoveResult(
        score=0,
        n_combo=0,
        n_cells_eliminated=0,
        game_over=False,
    )

    result = state.move(MoveAction(b'rg', 0, 3))
    assert (state.board[0][0:2] == [b'.', b'.']).all()
    assert (state.board[1][0:2] == [b'.', b'.']).all()
    assert (state.board[2][0:2] == [b'.', b'.']).all()
    assert (state.board[3][0:2] == [b'.', b'.']).all()
    assert result == gamestate.MoveResult(
        score=240,
        n_combo=1,
        n_cells_eliminated=8,
        game_over=False,
    )
