import streamlit as st
import pandas as pd

def get_saved_picks(sheet, user_email, week):
    records = pd.DataFrame(sheet.get_all_records())
    #print("Records DataFrame columns:", records.columns.tolist())
    print(records.head(2))
    if "Week" not in records.columns:
        return {}  # early exit if no 'Week' column
    records_week = records[records["Week"] == week]
    if user_email in records_week.columns:
        return dict(zip(records_week["Matchup"], records_week[user_email]))
    return {}


