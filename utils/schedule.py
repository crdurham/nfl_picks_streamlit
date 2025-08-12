import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_schedule():
    '''
    Load the NFL_2025_schedule.csv for purposes of releasing
    pick sheets by date/time.
    '''
    raw_schedule = pd.read_csv(DATA_DIR/"NFL_2025_sched.csv")
    raw_schedule[["month", "day_number"]] = raw_schedule["Date"].str.extract(r"^([A-Za-z]+)\s+(\d+)")
    raw_schedule["year"] = raw_schedule["month"].apply(lambda m: 2026 if m == "January" else 2025)
    
    return raw_schedule


def get_current_week(season_start_date, week_duration_days=7):
    today = datetime.today()
    time_since_start = today - season_start_date
    days_since_start = time_since_start.days
    
    #if days_since_start < 0:
        #return 0
    
    week = (days_since_start // week_duration_days) + 1

    return week