#  Dev Team: Diogo Almeida, Rodrigo Ferreira & Luís Laranjeira
from epilepsy_dash import Game
import sys

if __name__ == '__main__':
    game = Game(hand_mode=int(sys.argv[1]))
    game.run()