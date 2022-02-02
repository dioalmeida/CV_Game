#  Dev Team: Diogo Almeida, Rodrigo Ferreira & Luís Laranjeira
from epilepsy_dash import Game
import sys

if __name__ == '__main__':
    if len(sys.argv)==2:
        game = Game(hand_mode=int(sys.argv[1]))
    #game = Game()
        game.run()
    else:
        print("missing argument for game mode (0=normal, 1=hand detection mode).")