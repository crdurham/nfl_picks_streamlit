import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path("/Users/coledurham/streamlit-crash-course/data/picks.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_sheets():
    scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gspread"], scopes
    )

    gc = gspread.authorize(credentials)

    sh = gc.open("NFL Game Picks")
    return {
        "picks": sh.worksheet("Picks")
    }

def create_picks_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS picks (
              Week INTEGER,
              Home TEXT,
              Away TEXT,
              UserEmail TEXT,
              Pick TEXT,
              TimeStamp TEXT,
              Status TEXT,
              PRIMARY KEY (Week, Home, Away, UserEmail, Status) 
        )       
 """)
    conn.commit()
    conn.close()

def create_users_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
              UserEmail TEXT PRIMARY KEY,
              Name TEXT
        )       
 """)
    conn.commit()
    conn.close()

def create_leaderboard_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
              UserEmail TEXT,
              Name TEXT,
              Week INTEGER,
              Correct INTEGER,
              UpsetsCorrect INTEGER,
              ATSCorrect INTEGER,
              PRIMARY KEY (UserEmail, Week)
        )       
 """)
    conn.commit()
    conn.close()

def create_games_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS games (
              Week INTEGER,
              Home TEXT,
              Away TEXT,
              Spread REAL,
              MoneylineFav REAL,
              MoneylineDog REAL,
              HomeScore INTEGER,
              AwayScore INTEGER,
              Winner TEXT,
              Status TEXT,
              Timestamp TEXT,
              PRIMARY KEY (Week, Home, Away)
        )       
    """)
    conn.commit()
    conn.close()

def init_db():
    create_picks_db()
    create_leaderboard_db()
    create_users_db()
    create_games_db()

def get_saved_picks_sql(conn, user_email, week):
    query = """
    SELECT Home, Away, Pick
    FROM picks
    WHERE UserEmail = ? AND Week = ? AND Status = 'saved'
    """
    df = pd.read_sql_query(query, conn, params=(user_email, week))
    return {
        f"{row['Away']} @ {row['Home']}": row["Pick"] for _, row in df.iterrows()
    }


def register_user_if_needed(user_email, user_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE UserEmail = ?", (user_email,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (UserEmail, Name) VALUES (?, ?)", (user_email, user_name))
        conn.commit()

    conn.close()


def update_game_results(conn, week, home, away, home_score, away_score, status="final", timestamp=None):
    """
    Insert or update game results in the games table.
    """
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().isoformat()

    winner = None
    if home_score > away_score:
        winner = home
    elif away_score > home_score:
        winner = away
    else:
        winner = "TIE"

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO games (Week, Home, Away, HomeScore, AwayScore, Winner, Status, Timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(Week, Home, Away) DO UPDATE SET
            HomeScore=excluded.HomeScore,
            AwayScore=excluded.AwayScore,
            Winner=excluded.Winner,
            Status=excluded.Status,
            Timestamp=excluded.Timestamp
    """, (week, home, away, home_score, away_score, winner, status, timestamp))

    conn.commit()

def clear_picks_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM picks")

    conn.commit()
    conn.close()