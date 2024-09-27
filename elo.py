import numpy as np
import sys

from utils import *

num_args = len(sys.argv)
if num_args == 1:
    print("\n\n------------------------------------------")
    print("Welcome to ELO score tracking! How to use:")
    print("------------------------------------------\n")
    print("     - Adding new player: 'python elo.py Nacho'")
    print("     - Adding new player with starting ELO different from default 1200: 'python elo.py Nacho 1400'")
    print("     - Adding result for match: 'python elo.py Nacho Danial 4-2'\n\n\n")
    print("\n\nPrinting players:")
    display_players()
    print("\nPrinting game history:")
    for my_set in ALL_SETS:
        print(my_set)
    print("\n")
else:
    p1_name = sys.argv[1]
    if num_args == 2:
        player_1 = search_player(p1_name)
        if player_1 is None:
            add_player(p1_name)
            player_1 = search_player(p1_name)
            print(f"Added player {player_1}")
        else:
            print(f"Player {player_1} already exists!")

    if num_args > 2:
        if num_args == 3:
            elo_score = int(sys.argv[2])
            player_1 = search_player(p1_name)
            if player_1 is None:
                add_player(p1_name, elo_score)
                player_1 = search_player(p1_name)
                print(f"Added player {player_1}")
            else:
                print(f"Player {player_1} already exists!")


    if num_args == 4:
        p2_name = sys.argv[2]
        score = sys.argv[3].split('-')
        score_tuple = (int(score[0]), int(score[1]))
        add_set(p1_name, p2_name, score_tuple)

    display_players()
