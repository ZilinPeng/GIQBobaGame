from game import Game
from config import TURNS_PER_DAY

def main():
    game = Game()
    game.run_days(3, TURNS_PER_DAY)

if __name__ == "__main__":
    main()