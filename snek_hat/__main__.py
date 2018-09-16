import argparse
from snek_hat import SnekBoard

PARSER = argparse.ArgumentParser(
    description='Play snake on the Raspberry Pi Sense Hat!')
PARSER.add_argument('difficulty', help='The difficulty of the game.', choices=[
                    'easy', 'medium', 'hard'], nargs='?')
PARSER.set_defaults(difficulty='easy')
ARGS = PARSER.parse_args()


def main():
    board = SnekBoard()
    if ARGS.difficulty == 'medium':
        board.medium()
    elif ARGS.difficulty == 'hard':
        board.hard()
    else:
        board.easy()
    board.run()


if __name__ == '__main__':
    main()
