############ Create Strategy Class to set out a blueprint for the simulations using the constraints above ##############

import pandas as pd

class Strategy: 
    def __init__(self, players_data, fixture_data):
        self.players_data = players_data
        self.fixture_data = fixture_data
        self.gw = 1
        self.team = [] # your current team
        # self.bank = 1000 # starting budget
        self.transfers_used = []
    
    def select_initial_team(self):
        pass

    def make_transfers():
        # the subclass strategy will define this function
        pass    

    def choose_captain():
        # the subclass strategy will define this function
        pass

    def play_gameweek():
        # the subclass strategy will define this function
        pass

    def run_season(self, gws=38):
        self.select_initial_team()
        for gw in range(1, gws + 1):
            self.make_transfers(gw)
            # self.choose_captain()
            # self.play_gameweek()

############# Strategy 1 - Value-based selection (Points per million) #############

class FormStrategy(Strategy):
    # 1 premium, 1 bench fodder, for each position, then split the rest in accordance with the % splits calculated by the wighted points average
    # 2 GKs (12% wpa), 5 DEFs (30% wpa), 5 MIDs (35% wpa), 3 FWDs (23% wpa)
    # Update: You do not have info on GW1 team, so you'll need some logic to get started
    def select_initial_team(self):
        team = []
        positions = ['GKP', 'DEF', 'MID', 'FWD']
        # fill rest of positions
        for pos in positions: 
            if pos == 'GKP':
                slots = 1
            elif pos == 'DEF':
                slots = 3
            elif  pos == 'MID':
                slots = 5
            elif pos == 'FWD':
                slots = 2 
            
            for i in range(slots):
                pos_series = self.players_data[(self.players_data['position'] == pos) & (self.players_data['gameweek_id'] == 1)]
                pos_series = pos_series[~pos_series['player_id'].isin(team)]
                player_series = pos_series.sort_values(by=['form'], ascending=False).iloc[0]
                player_id = player_series['player_id']
                team.append(player_id)
        self.team = team

    # identify players with the lowest PPM, and replace them with with players with the highest PPM within budget. 
    def make_transfers(self, gw):
        team = self.team
        gw = self.gw
        all_player_series = self.players_data[(self.players_data['gameweek_id'] == gw)]
        my_player_series = all_player_series[all_player_series['player_id'].isin(team)]
        out_player = my_player_series.sort_values(by=['form'], ascending=True).iloc[0]
        out_player_id = out_player['player_id']
        pos = out_player['position']
        pos_player = all_player_series[all_player_series['position'].isin([pos])]
        in_player = pos_player.sort_values(by=['form'], ascending=False).iloc[0]
        in_player_id = in_player['player_id']
        team.remove(out_player_id)
        team.append(in_player_id)

        print('Gameweek:' + str(gw) + ' ' + 'Team: ' + str(team))
        self.gw= gw + 1
        self.team = team

############ Strategy 2 - Form-based (Recent points or xG/xA) #############



############ Strategy 3 - Fixture-rotation (FDR-based planning) #############



############ Strategy 4 - Template-following (Top % most-owned) #############



############ Strategy 5 - Differential-focused (low ownership, high upside) #############



############ Strategy C - Captaincy strategy #############

############ Master Script ######################

strategy_data = pd.read_csv(r'C:\Users\alexh\python_projects\fpl_stratergy_sim\data\strategy_data.csv')

strategy = FormStrategy(strategy_data, strategy_data)
strategy.run_season()
