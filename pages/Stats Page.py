import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from utils.schedule import (load_schedule, get_current_week)
from datetime import datetime

DB_PATH = Path("/Users/coledurham/streamlit-crash-course/data/picks.db")

st.set_page_config(page_title="Leaderboard")

start_date = datetime(2025, 9, 2)
week = get_current_week(start_date)


#Verify User
try:
    user_email = st.user.email.lower()
    user_name = st.user.name
except Exception:
    user_email = st.sidebar.text_input("Dev Email", value="devuser@example.com")
    user_name = st.sidebar.text_input("Dev Name", value="Dev User")

st.sidebar.markdown(f"**Logged in as:** {user_name} ({user_email})")


st.title("Leaderboard")

# Load data
@st.cache_data
def load_picks(weeks):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM picks WHERE Status = 'submitted' AND Week <= ?", 
                           conn,
                           params=(weeks,))
    conn.close()
    return df

df = load_picks(week)

# Display
if not df.empty:
    df['Week'] = df['Week'].astype(int)
    selectable_weeks = sorted(df['Week'].unique())
    selected_week = st.selectbox("Select a week to view all submitted picks", selectable_weeks)

    df_week = df[df['Week'] == selected_week]

    # (Optionally) drop columns from display
    st.dataframe(df_week)
else:
    st.info("No picks submitted yet.")
