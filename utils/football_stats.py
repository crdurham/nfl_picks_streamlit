import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import tempfile
from pathlib import Path
from utils.data_retrieval import load_tracking_data_for_week

DATA_DIR = Path(__file__).parent.parent / "data"

def load_seasonal_data():
    seasonal_stats = pd.read_csv(DATA_DIR/"Seasonal Stats - Season Stats.csv")
    seasonal_stats = seasonal_stats.rename(columns={'Tm': 'Team', 
                                                    'win_percent': 'Win Percentage',
                                                    'PF': 'Points For',
                                                    'PA': 'Points Against',
                                                    'SoS': 'Strength of Schedule',
                                                    'W': 'Wins',
                                                    'L': 'Losses',
                                                    'T': 'Ties',
                                                    'PD': 'Point Differential'})
    return seasonal_stats


def load_games_data():
    games_df = pd.read_csv(DATA_DIR/"tracking_data/games.csv")
    return games_df

def load_tracking_data(team="BUF", week=1):
    """
    Load tracking data for specific (team, week) combination.
    """
    games_df = load_games_data()
    team_games = games_df[(games_df["homeTeamAbbr"]==team) | (games_df["visitorTeamAbbr"]==team)]["gameId"].unique()
    tracking_week_df = load_tracking_data_for_week(week)

    tracking_week_team_df = tracking_week_df[tracking_week_df['gameId'].isin(team_games)]
    return tracking_week_team_df
    
team_name_color_dict = {'BUF':[(0, 51/255, 141/255), (198/255, 12/255, 48/255)],
                        'LA': [(0, 53/255, 148/255), (1, 163/255, 0)], 
                        'LAR': [(0, 53/255, 148/255), (1, 163/255, 0)],
                        'football':[(130/255, 64/255, 7/255), (130/255, 64/255, 7/255)], 
                        'NO':[(211/255, 188/255, 141/255), (16/255, 24/255, 31/255)], 
                        'ATL':[(167/255, 25/255, 48/255), (0, 0, 0)], 
                        'CLE':[(49/255, 29/255, 0), (1, 60/255, 0)], 
                        'CAR':[(0, 133/255, 202/255), (16/255, 24/255, 32/255)], 
                        'SF':[(170/255, 0, 0), (173/255, 153/255, 93/255)], 
                        'CHI':[(11/255, 22/255, 42/255), (200/255, 56/255, 3/255)],
                        'CIN':[(251/255, 79/255, 20/255),(0, 0, 0)], 
                        'PIT':[(1, 182/255, 18/255), (16/255, 24/255, 32/255)], 
                        'PHI':[(0, 76/255, 84/255), (165/255, 172/255, 175/255)], 
                        'DET':[(0, 118/255, 182/255), (176/255, 183/255, 188/255)], 
                        'IND':[(0, 44/255, 95/255), (162/255, 170/255, 173/255)], 
                        'HOU':[(3/255, 32/255, 47/255), (167/255, 25/255, 48/255)], 
                        'MIA':[(0, 142/255, 151/255), (252/255, 76/255, 2/255)], 
                        'NE':[(0, 34/255, 68/255), (198/255, 12/255, 48/255)], 
                        'NYJ':[(18/255, 87/255, 64/255), (0, 0, 0)],
                        'BAL':[(26/255, 25/255, 95/255),(0, 0, 0)], 
                        'TEN':[(75/255, 146/255, 219/255), (200/255, 16/255, 46/255)], 
                        'NYG':[(1/255, 35/255, 82/255), (163/255, 13/255, 45/255)], 
                        'JAX':[(0, 103/255, 120/255), (215/255, 162/255, 42/255)], 
                        'WAS':[(90/255, 20/255, 20/255), (1, 182/255, 18/255)], 
                        'KC':[(227/255, 24/255, 55/255), (1, 184/255, 28/255)], 
                        'ARI':[(151/255, 35/255, 63/255), (0, 0, 0)], 
                        'LV':[(0, 0, 0), (165/255, 172/255, 175/255)], 
                        'LAC':[(0, 128/255, 198/255), (1, 194/255, 14/255)], 
                        'MIN':[(79/255, 38/255, 131/255), (1, 198/255, 47/255)],
                        'GB':[(24/255, 48/255, 40/255), (1, 184/255, 28/255)], 
                        'TB':[(1, 121/255, 0), (213/255, 10/255, 10/255)], 
                        'DAL':[(0, 53/255, 148/255), (134/255, 147/255, 151/255)], 
                        'DEN':[(251/255, 79/255, 20/255), (0, 34/255, 68/255)], 
                        'SEA':[(0, 34/255, 68/255), (105/255, 190/255, 40/255)]}

def animate_play(week=1, team="BUF", play_id=2137):
    tracking_data = load_tracking_data(team=team, week=week)
    #tracking_data = tracking_data[tracking_data['club'] == team]
    play_tracking = tracking_data[tracking_data['playId'] == play_id].copy()

    if play_tracking.empty:
        print(f"No tracking data located for given data.\n Please enter different combination of Week/Team/Play ID.")
        return
    
    frames = play_tracking['frameId'].nunique()

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(12, 5.33)


    ax.set_facecolor('green')
    ax.set_xlim([0, 120])
    ax.set_ylim([0, 53.3])

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    def animate_play_frame(i):
        ax.clear() 
        ax.set_facecolor('green')
        ax.set_xlim([0, 120])
        ax.set_ylim([0, 53.3])
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # Endzones
        ax.axvspan(0, 10, ymin=0, ymax=1, facecolor='gray', alpha=0.3)    # Left endzone
        ax.axvspan(110, 120, ymin=0, ymax=1, facecolor='gray', alpha=0.3) # Right endzone

        # Sidelines
        ax.vlines(x=[10, 110], ymin=0, ymax=53.3, colors='black')

        # Yard markers 
        for x in range(20, 110, 10):
            ax.axvline(x, color='white', linestyle='--', alpha=0.6, linewidth=1)

        players_in_play = play_tracking['displayName'].unique()
        for player in players_in_play:
            player_path = play_tracking[play_tracking['displayName'] == player]
            frame_data = player_path[player_path['frameId'] == i]

            if not frame_data.empty:
                x_pos = frame_data['x'].values[0]
                y_pos = frame_data['y'].values[0]
                club = frame_data['club'].values[0]

                if club == 'football':
                    ax.plot(x_pos, y_pos, color=team_name_color_dict['football'][0], marker='d', markersize=10)
                else:
                    facecolor = team_name_color_dict.get(club, [(0, 0, 0)])[0]
                    edgecolor = team_name_color_dict.get(club, [(0, 0, 0)])[1]
                    ax.plot(x_pos, y_pos, marker='o', markerfacecolor=facecolor, 
                            markeredgecolor=edgecolor, markersize=12, markeredgewidth=2)

    ani = FuncAnimation(fig, animate_play_frame, frames=frames, interval=100)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as tmpfile:
        ani.save(tmpfile.name, writer=PillowWriter(fps=10))
        tmpfile.seek(0)
        gif_bytes = tmpfile.read()

    plt.close(fig)
    return gif_bytes




