import streamlit as st
import pandas as pd
import numpy as np
from utils.football_stats import (load_seasonal_data,
                                  team_name_color_dict, 
                                  load_tracking_data,
                                  animate_play)
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from utils.db import register_user_if_needed
from utils.data_retrieval import load_tracking_data_for_week

stats = load_seasonal_data()[['Team','Season','Wins','Losses','Ties','Win Percentage','Points For','Points Against','Point Differential','Strength of Schedule','Playoffs']]
teams_stats = stats['Team'].unique()
teams_gif = teams_stats

st.set_page_config(page_title="Home")

try:
    user_email = st.user.email.lower()
    user_name = st.user.name
except Exception:
    user_email = st.sidebar.text_input("Dev Email", value="devuser@example.com")
    user_name = st.sidebar.text_input("Dev Name", value="Dev User")

registration = register_user_if_needed(user_email=user_email, user_name=user_name)

st.sidebar.markdown(f"**Logged in as:** {user_name} ({user_email})")



st.title("NFL Picks Site")

with st.sidebar:
    st.header("About the app:")
    st.write("My first streamlit app, aimed at hosting NFL " \
    "picks and producing some basic data visualization.")

st.markdown("<h4 style='text-align: left;'>Weekly Picks</h4>", unsafe_allow_html=True)

st.markdown("""
<p style='text-indent: 2em'>
Through the Weekly Picks page, submit your choice for the winner (straight up) of each NFL game. Guess the total score of the final game of the week as a tiebreaker.
Entry fee is $5, though tips are accepted!
</p>
            
<p style='text-indent: 2em'>
Check the Leaderboard page for overall standings and other statistics.
</p>
""", unsafe_allow_html=True)


#Edit the layout/number of columns using st.columns

st.markdown("<h4 style='text-align: left;'>Data Visualization: Some Basics</h4>", unsafe_allow_html=True)

st.markdown("""
<p style='text-indent: 2em'>
Below are a few simple data visualizations with the option for user input. Data was obtained from
<a href="https://www.pro-football-reference.com" target="_blank">Pro Football Reference</a> and their trove of data, as well as 
<a href="https://www.kaggle.com/competitions/nfl-big-data-bowl-2024" target="_blank">NFL Big Data Bowl 2024</a>.
</p>
""", unsafe_allow_html=True)
with st.container():
    st.markdown("<h5 style='text-align: left;'>Example 1: Team Stats Over the Years</h4>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-indent: 2em'>
    Select team(s), season(s) from 1990-2024, and a statistical category to see trends and comparisons over time.
    </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        teams = st.multiselect(
        "Teams:",
        teams_stats,
        default=["BUF", "NE"],
    )

    with col2:
        seasons = st.slider("Select a range of values", 1990, 2024, (2001, 2019))

    with col3:
        stat_options = stats.columns.drop(["Team", "Season", "Playoffs"])
        default_stat = "Point Differential"
        default_index = stat_options.tolist().index(default_stat) if default_stat in stat_options else 0

        stat_category = st.selectbox("Statistic:", stat_options, index=default_index)


    fig,ax = plt.subplots(figsize=(12,5))
    ax.set_title(f"{stat_category} Over Time")
    ax.set_xlabel("Season")
    ax.set_ylabel(stat_category)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    for team in teams:
        facecolor = team_name_color_dict.get(team, [(0,0,0)])[0]
        edgecolor = team_name_color_dict.get(team, [(0,0,0)])[1]
        team_stat = stats[(stats['Team'] == team) & 
                        (stats["Season"].between(seasons[0], seasons[1]))][[stat_category, "Season"]]
        team_stat = team_stat.sort_values("Season")
        ax.plot(team_stat["Season"], team_stat[stat_category], marker='o', 
                color = facecolor, label=team, markersize=14)
        
    ax.legend(title="Team")

    st.pyplot(fig)


with st.container():
    st.markdown("<h5 style='text-align: left;'>Example 2: Play Animation with Player Tracking Data</h4>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-indent: 2em'>
    Enter a week (1-9) and a team, then select a play ID to produce a GIF of that play. Please note
    that not all frames are included, so you may only see the end of a given play.
    </p>
    """, unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)
    with col4:
        week = st.selectbox("Week:", [1,2,3,4,5,6,7,8,9])

    with col5:
        team_gif = st.selectbox("Team:", options=teams_gif)

    tracking_data = load_tracking_data(team=team_gif, week=week)

    with col6:
        play_id = st.selectbox("Play ID:", tracking_data["playId"].unique())

if week is not None:
        with st.spinner(f"Loading tracking data for week {week}..."):
            tracking_data = load_tracking_data(team=team_gif, week=week)

if st.button("Create GIF"):
        cola, colb, colc = st.columns([1,8,1])
        with colb:
            gif = animate_play(team=team_gif, week=week, play_id=play_id)

        if gif:
            st.image(image=gif, use_container_width=True, caption=f"{team_gif} play from week {week}, 2022.")
        else:
            st.warning("No animation available.")