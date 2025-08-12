import streamlit as st
import pandas as pd
import requests
from io import StringIO
import gdown

#If using tracking data stored in google drive (better for deployment to not have big files)

def gdrive_direct_url(share_url):
    file_id = share_url.split("/d/")[1].split("/")[0]
    return f"https://drive.google.com/uc?export=download&id={file_id}"

TRACKING_FILES = {
    1: "https://drive.google.com/file/d/1yp6zN5RARRwswkPLZ2NvXCIpBDgS-Hi0/view?usp=share_link",
    2: "https://drive.google.com/file/d/1OIbGrqzlTcA6aFnMgz9hFupbBIMT07xL/view?usp=share_link",
    3: "https://drive.google.com/file/d/1EYehmTtzu8qgZbZBScDyIX5oUJEyHkAq/view?usp=share_link",
    4: "https://drive.google.com/file/d/1O1taCCfWFs3G6c6EFQYgZAB84_evzRfL/view?usp=share_link",
    5: "https://drive.google.com/file/d/17Ml-x5CSgnbV7QXdkWwg5x_tHqAh9MNV/view?usp=share_link",
    6: "https://drive.google.com/file/d/13-ZyfonC7liO0-0NLm1OJcTUm_jvp5QD/view?usp=share_link",
    7: "https://drive.google.com/file/d/1upXUmrBBNrflG0IC3gvM1AT7B_JBT6KQ/view?usp=share_link",
    8: "https://drive.google.com/file/d/1ay2_mM5FJktQhUx2BdGUw2eHAYUR1tfj/view?usp=share_link",
    9: "https://drive.google.com/file/d/1Kbu89RdSOQiKEduqbcCznIgvaS3IKnHt/view?usp=share_link"
    # etc.
}

@st.cache_data
def load_tracking_data_for_week(week):
    share_url = TRACKING_FILES.get(week)
    if not share_url:
        st.error(f"No tracking data for week {week}")
        return None
    file_id = share_url.split("/d/")[1].split("/")[0]
    url = f"https://drive.google.com/uc?id={file_id}"
    
    # Download file to temp location
    output = f"/tmp/week_{week}.csv"  # or use tempfile.NamedTemporaryFile if preferred
    gdown.download(url, output, quiet=True)
    
    df = pd.read_csv(output)
    return df
