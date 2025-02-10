import h5py
import os.path
import numpy as np
from datetime import datetime

h5_name = "ELO.hdf5"
ALL_SETS = []
ALL_PLAYERS = []

def calculate_elo(player_rating, opponent_rating, result, k=32):
    """
    Calculate the new ELO rating for a player.
    
    :param player_rating: Current ELO rating of the player
    :param opponent_rating: Current ELO rating of the opponent
    :param result: Game result (1 for win, 0.5 for draw, 0 for loss)
    :param k: K-factor, which determines the maximum possible adjustment per game
    :return: New ELO rating for the player
    """
    expected_score = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))
    new_rating = player_rating + k * (result - expected_score)
    return new_rating

class player:
    def __init__(self, name = 'Bob', ranking = 1200, player_number = 0):
        self.name = name
        self.ranking = ranking
        self.games = 0
        self.player_number = player_number

    def __repr__(self):
        pretty_name = self.name.replace("_", " ")
        my_string = f"{pretty_name} - {self.ranking:.0f}"#" ({self.games} games played)"
        return my_string

    def __str__(self):
        return self.__repr__()

class game:
    def __init__(self, player_1, player_2, winner):
        self.player_1 = player_1
        self.player_2 = player_2
        self.winner = winner

    def __repr__(self):
        if self.winner == 1:
            p1_num = 1
            p2_num = 0
        else:
            p1_num = 0
            p2_num = 1
        my_string = f"{player_1.name} {p1_num} - {p2_num} {player_2.name}"
        return my_string

    def __str__(self):
        return self.__repr__()

class game_set:
    def __init__(self, player_1, player_2, wins_tuple, date=None):
        self.player_1 = player_1
        self.player_2 = player_2
        self.results = wins_tuple
        self.num_games = wins_tuple[0] + wins_tuple[1]
        if date is None:
            self.date = datetime.today().strftime('%Y-%m-%d')
        else:
            self.date = date
        player_1.games += self.num_games
        player_2.games += self.num_games

    def __repr__(self):
        my_string = f"{self.player_1.name} {self.results[0]} - {self.results[1]} {self.player_2.name} -- {self.date}"
        return my_string

    def __str__(self):
        return self.__repr__()

    @property
    def games(self):
        tot_games = self.num_games
        G = []
        for g1 in range(self.results[0]):
            G.append(game(self.player_1, self.player_2, self.player_1))
        for g2 in range(self.results[1]):
            G.append(game(self.player_1, self.player_2, self.player_2))
        return G

def search_player(name):
    for pp in ALL_PLAYERS:
        if pp.name == name:
            return pp

    return None

def add_set(player_1, player_2, wins_tuple):
    if isinstance(player_1, str):
        player_1 = search_player(player_1)
    if isinstance(player_2, str):
        player_2 = search_player(player_2)
        
    new_set = game_set(player_1, player_2, wins_tuple)
    GAMES = new_set.games
    print(f"Adding game of {player_1.name} vs. {player_2.name} with score {wins_tuple[0]}-{wins_tuple[1]}")
    print(f"Starting {player_1.name} ELO = {player_1.ranking}")
    print(f"Starting {player_2.name} ELO = {player_2.ranking}")
    tot_games = sum(wins_tuple)
    tied_games = min(wins_tuple)
    for ii in range(tied_games):
        new_p1_elo = calculate_elo(player_1.ranking, player_2.ranking, 1)
        new_p2_elo = calculate_elo(player_2.ranking, player_1.ranking, 0)
        player_1.ranking = new_p1_elo
        player_2.ranking = new_p2_elo

        new_p1_elo = calculate_elo(player_1.ranking, player_2.ranking, 0)
        new_p2_elo = calculate_elo(player_2.ranking, player_1.ranking, 1)
        player_1.ranking = new_p1_elo
        player_2.ranking = new_p2_elo

    p1_on_top = max((wins_tuple[0] - tied_games, 0))
    for ii in range(p1_on_top):
        new_p1_elo = calculate_elo(player_1.ranking, player_2.ranking, 1)
        new_p2_elo = calculate_elo(player_2.ranking, player_1.ranking, 0)
        player_1.ranking = new_p1_elo
        player_2.ranking = new_p2_elo

    p2_on_top = max((wins_tuple[1] - tied_games, 0))
    for ii in range(p2_on_top):
        new_p1_elo = calculate_elo(player_1.ranking, player_2.ranking, 0)
        new_p2_elo = calculate_elo(player_2.ranking, player_1.ranking, 1)
        player_1.ranking = new_p1_elo
        player_2.ranking = new_p2_elo

    print(f"\nAdded {tied_games} tied games, {p1_on_top} extra for {player_1.name} and {p2_on_top} for {player_2.name}\n")
    print(f"Final {player_1.name} ELO = {player_1.ranking}")
    print(f"Final {player_2.name} ELO = {player_2.ranking}")
    ALL_SETS.append(new_set)
    save_data()

def add_player(name, ranking=1200, player_number=None, saving=True, verbose=True):
    if player_number is None:
        player_number = len(ALL_PLAYERS)
    new_player = player(name, ranking, player_number)

    if verbose:
        print(f"Added player {name} with starting ranking of {ranking} to list of players, player number is {player_number}!")

    ALL_PLAYERS.append(new_player)

    if saving:
        save_data()

def save_data(savename = h5_name):
    fid = h5py.File(savename, 'w')
    player_names = []
    rankings = []
    player_numbers = []

    for pp in ALL_PLAYERS:
        player_names.append(pp.name)
        rankings.append(pp.ranking)
        player_numbers.append(pp.player_number)

    fid['player_names'] = player_names
    fid['rankings'] = rankings
    fid['player_numbers'] = player_numbers

    tot_sets = len(ALL_SETS)
    set_info = np.zeros((tot_sets, 4), dtype=int)
    set_dates = []
    for ii in range(tot_sets):
        my_set = ALL_SETS[ii]
        set_info[ii,0] = my_set.player_1.player_number
        set_info[ii,1] = my_set.player_2.player_number
        set_info[ii,2:] = my_set.results
        set_dates.append(my_set.date)
    fid['tot_sets'] = tot_sets
    fid['set_info'] = set_info
    fid['set_dates'] = set_dates
    fid.close()

def load_data(savename = h5_name):
    fid = h5py.File(savename, 'r')

    player_names = []
    for pp in fid['player_names']:
        player_names.append(pp.decode())
    rankings = fid['rankings'][()]
    player_numbers = fid['player_numbers'][()]

    num_players = len(player_numbers)
    for ii in range(num_players):
        add_player(player_names[ii], rankings[ii], player_numbers[ii], saving=False, verbose=False)

    tot_sets = fid['tot_sets'][()]
    set_info = fid['set_info'][()]

    set_dates = []
    for pp in fid['set_dates']:
        set_dates.append(pp.decode())

    for ii in range(tot_sets):
        p1 = ALL_PLAYERS[set_info[ii,0]]
        p2 = ALL_PLAYERS[set_info[ii,1]]
        wins_tuple = tuple(set_info[ii,2:])
        my_set = game_set(p1, p2, wins_tuple, set_dates[ii])
        ALL_SETS.append(my_set)
    fid.close()

    
def late_since_last_game(player):
    last_date = None
    for my_set in ALL_SETS:
        if player == my_set.player_1 or player == my_set.player_2:
            last_date = my_set.date

    today_datetime = datetime.today()
    last_datetime = datetime.strptime(last_date, '%Y-%m-%d')
    diff = today_datetime - last_datetime

    return diff.days

def display_players():
    all_elos = []
    for pp in ALL_PLAYERS:
        all_elos.append(pp.ranking)
    order = np.argsort(all_elos)[::-1]

    print("## LIST OF PLAYERS AND ELO RANKINGS\n\n")
    
    idx = 1
    for ii in range(len(all_elos)):
        player_ii = ALL_PLAYERS[order[ii]]
        days_since_last = late_since_last_game(player_ii)
        if days_since_last <= 21:
            print(f'{idx} - {player_ii}')
            print("\n")
            idx += 1

    print('\n--------------------------------------------------------------')

print("\n\n--------------   Welcome to ELO score tracking  --------------\n")

if os.path.isfile(h5_name):
    load_data()
