"""This script handles the data processing for the strategy simulation script. 
    It will pull player and team data from local databases that store Premier 
     Leauge data for previous seasons. """

import json
import pandas as pd
import psycopg2
from pathlib import Path
import warnings

# warnings.filterwarnings('ignore')  # Suppress all warnings

# trying to get the rolling average to work
def movingSum(df: pd.DataFrame, col):
    df = df.sort_values(by=['player_id', 'gameweek_id'])
    df[col + '_moving_avg'] = df.groupby(['player_id'])[col].expanding().sum().reset_index(level=0, drop=True)
    return df

# setup the database password as var
with open(r'C:\Users\alexh\PycharmProjects\fpl_data_pull\pw.json') as f:
    config = json.load(f)
    database_password = config['PASSWORDS']['DATABASE_PASSWORD']

# setup the database name as var
name_database_24_25 = 'fpl_db_24_25'
name_database_23_24 = 'fpl_db_23_24'
name_database_22_23 = 'fpl.db.22.23'

# add databease to list for loop
databases = [name_database_23_24, name_database_24_25, name_database_22_23]

# loop through databases
for database in databases:

    # establish connection
    conn = psycopg2.connect("dbname='" + database + "' user='postgres' host='localhost' password=" + database_password)

    # Create cursor
    cur = conn.cursor()

    # define queries to pull necessary data from database
    player_gw_query = 'SELECT * FROM player_gw_stats'
    player_info_query = 'SELECT * FROM player_info'
    team_query = 'SELECT * FROM team_info'

    team_fixture_query = """
    SELECT 
    gameweek_id,
    team_id,
    opponent_id,
    fixture_difficulty
    FROM public.fixture_difficulty
    """

    # use queries to read data from sql into dataframe
    player_df = pd.read_sql(player_info_query, conn)
    player_gw_df = pd.read_sql(player_gw_query, conn)
    team_fixture_df = pd.read_sql(team_fixture_query, conn)
    team_df = pd.read_sql(team_query, conn)
    
    # set season name
    player_gw_df['year'] = database
    team_df['year'] = database
    # remove double gameweeks
    player_gw_df = player_gw_df[player_gw_df['dgw'] == False]
    # remove duplicates from fixture list
    team_fixture_df = team_fixture_df.drop_duplicates(subset=['gameweek_id', 'team_id'], keep='first')
    
    # create opponent df use fixture df
    opponent_df = pd.merge(team_fixture_df,
                        team_df.add_prefix('opponent_'),
                        left_on='opponent_id',
                        right_on='opponent_team_id',
                        )
    # add avg goals against
    opponent_df['opponent_avg_goals_against'] = opponent_df['opponent_total_goals_against'] / opponent_df['opponent_games_played']
    # reduce df to necessary columns
    opponent_df = opponent_df[['gameweek_id', 'team_id', 'opponent_league_position', 'opponent_total_goals_against', 'opponent_avg_goals_against', 'opponent_team_name', 'fixture_difficulty']]
    player_team_df = team_df[['team_id', 'team_name', 'games_played', 'league_position', 'total_goals_scored']]
    player_df_reduced = player_df[['player_id', 'team_id', 'position', 'second_name', 'current_price']]
    # player_team_df['team_avg_goals_scored'] = player_team_df['total_goals_scored'] / player_team_df['games_played']

    player_gw_df = pd.merge(player_gw_df,
                  player_df_reduced,
                  left_on='player_id',
                  right_on='player_id')

    player_gw_df = pd.merge(player_gw_df,
                  opponent_df,
                  left_on=['gameweek_id', 'team_id'],
                  right_on=['gameweek_id', 'team_id'])

    player_gw_df = pd.merge(player_gw_df,
                  player_team_df.add_prefix('player_team_'),
                  left_on='team_id',
                  right_on='player_team_team_id')


player_gw_df = movingSum(player_gw_df, 'points')
player_gw_df['points_per_million'] = player_gw_df['points_moving_avg'] / player_gw_df['current_price']

output_file = Path(r'C:\Users\alexh\python_projects\fpl_stratergy_sim\data\strategy_data.csv')
# output_file.mkdir(exist_ok=True, parents=True)

player_gw_df.to_csv(output_file)