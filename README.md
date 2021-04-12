# Puyo Puyo Tetris AI
A framework for writing AIs for falling block games such as Puyo Puyo and Tetris.

While this framework is designed to work with any falling brick game, so far
it's only implemented for Puyo in the Nintendo Switch game Puyo Puyo Tetris 2.


## Setup

### Botbase

First you'll need a Switch with a homebrew OS and
[USB-Botbase](https://github.com/fishguy6564/USB-Botbase) installed. This
allows the AI to control the game via USB.

Next, install Python 3.6 or above. Install all of the python requirements in
the "requirements.txt" file. If you're using pip, you can do that with this
command:

    $ pip install -r requirements.txt


## Usage

Run Puyo Puyo Tetris 2 and connect the USB cable to your Switch. You can run
ptai.py when you are in a Puyo Puyo game, otherwise it will read a null pointer
on the Switch.

### Play with the AI

    $ python ptai.py play

### Printing game state

    $ python ptai.py getstate

### Showing the AI's move

    $ python ptai.py getmove


## Developing

There are some extra packages you'll have to install for things like running
tests and updating requirements:

    $ pip install -r dev-requirements.txt

### Running Tests

    $ pytest

### Updating Requirements

Requirements are pinned to specific versions using
[pip-tools](https://github.com/jazzband/pip-tools). "requirements.in" contains
the package names directly used, and "requirements.txt" has the exact versions
pinned, including sub dependencies. After updating "requirements.in", run:

    $ pip-compile
    $ pip install -r requirements.txt
