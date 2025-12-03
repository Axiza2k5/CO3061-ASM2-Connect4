import argparse
from src.game import GameView

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('iterations', nargs='?', default=20, action="store", help="Store the number of iterations to train computer")
    args = parser.parse_args()

    GameView(1200, 760).main_menu(int(args.iterations))
