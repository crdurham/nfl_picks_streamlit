import streamlit as st
from datetime import datetime
import pandas as pd
import sqlite3
from utils.db import (init_db, get_saved_picks_sql,
                      get_connection, register_user_if_needed)
from utils.schedule import (load_schedule, get_current_week)


st.set_page_config(page_title="Picks Sheet(s)")

init_db()

#Verify User
try:
    user_email = st.user.email.lower()
    user_name = st.user.name
except Exception:
    user_email = st.sidebar.text_input("Dev Email", value="devuser@example.com")
    user_name = st.sidebar.text_input("Dev Name", value="Dev User")

st.sidebar.markdown(f"**Logged in as:** {user_name} ({user_email})")

conn = get_connection()
register_user_if_needed(user_email=user_email,
                        user_name=user_name)

cursor = conn.cursor()


#Determine week of season --> access games
start_date = datetime(2025, 9, 2)
league_schedule = load_schedule()
week = get_current_week(start_date)

games = league_schedule[league_schedule['Week'] == week]



#Access picks user has saved
saved_picks_row = get_saved_picks_sql(conn, user_email, week)

user_picks = {}

st.markdown("<h1 style='text-align: center;'>Picks Sheet(s)</h2>", unsafe_allow_html=True)

st.markdown("<h4 style='text-align:center;'>Picks Sheet</h2>", unsafe_allow_html=True)

with st.form(f"picks_form_week_{week}", width="content"):
    st.markdown(f"### Picks Sheet: Week {week}")

    for _, row in games.iterrows():
        game_label = f"{row['VisTm']} @ {row['HomeTm']}"
        if row['Site'] != 'Home':
            game_label += f" ({row['Site']})"      
        
        choose_from = [row['VisTm'], row['HomeTm']]
        default_pick = None

        if saved_picks_row and game_label in saved_picks_row:
            saved_pick = saved_picks_row[game_label]

            if saved_pick in choose_from:
                default_pick = saved_pick

        pick = st.selectbox(game_label, choose_from, 
                    index=choose_from.index(default_pick) if default_pick else 0)

        user_picks[game_label] = pick

    cola, colb = st.columns(2)
    with cola:
        save_picks = st.form_submit_button("Save Picks")
    with colb:
        submit_picks = st.form_submit_button("Submit Picks")


if save_picks:
    for game_label, pick in user_picks.items():
        game_label_base = game_label.split(' (')[0]
        if " @ " in game_label_base:
            away, home = game_label_base.split(" @ ")
        else:
            st.error(f"Could not parse matchup: {game_label_base}")
            continue


        cursor.execute("""
            DELETE FROM picks WHERE UserEmail = ? AND Week = ? AND Home = ? AND Away = ? AND Status = 'saved'
        """, (user_email, week, home, away))
        conn.commit()

        cursor.execute("""
            INSERT INTO picks (Week, Home, Away, UserEmail, Pick, TimeStamp, Status)
            VALUES (?, ?, ?, ?, ?, ?, 'saved')
        """, (week, home, away, user_email, pick, datetime.now().isoformat()))
    
    conn.commit()
    st.success("Picks saved.")


if submit_picks:
    cursor.execute("""
        SELECT 1 FROM picks
        WHERE UserEmail = ? AND Week = ? AND Status = 'submitted'
        LIMIT 1
        """, (user_email, week))

    if cursor.fetchone():
        st.error("You have already submitted picks for this week!")
    else:
        for game_label, pick in user_picks.items():
            game_label_base = game_label.split(' (')[0]
            if " @ " in game_label_base:
                away, home = game_label_base.split(" @ ")
            else:
                st.error(f"Could not parse matchup: {game_label_base}")
                continue
            cursor.execute("""
                DELETE FROM picks WHERE UserEmail = ? AND Week = ? AND Home = ? AND Away = ? AND Status = 'submitted'
                """, (user_email, week, home, away))

            cursor.execute("""
                INSERT INTO picks (Week, Home, Away, UserEmail, Pick, TimeStamp, Status)
                VALUES (?, ?, ?, ?, ?, ?, 'submitted')
            """, (week, home, away, user_email, pick, datetime.now().isoformat()))
    
    conn.commit()
    st.success("Picks submitted.")

