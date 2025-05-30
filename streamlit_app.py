
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from copy import deepcopy
import random

# ✅ Make a copy of the secrets dictionary

# Load and fix credentials
raw_creds = dict(st.secrets["gcp_service_account"])
raw_creds["private_key"] = raw_creds["private_key"].replace("\\n", "\n")

# Define scopes and authenticate
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(raw_creds, scopes=scopes)

gc = gspread.authorize(credentials)


# Open your sheet by name
SPREADSHEET_NAME = "FRUS Sentiment Annotations"
worksheet = gc.open(SPREADSHEET_NAME).sheet1

# Load data chunks
@st.cache_data
def load_chunks():
    df = pd.read_csv("frus_1961_63_volume5_chunks.csv")
    return df

df = load_chunks()

# Track user progress

if "chunk_index" not in st.session_state:
    st.session_state.chunk_index = random.randint(0, len(df) - 1)

st.title("📜 FRUS Sentiment Labeling")
st.subheader("Help label U.S. diplomatic text with expert-informed sentiment")

current_chunk = df.iloc[st.session_state.chunk_index]

st.markdown("### Document Excerpt")
st.code(current_chunk["text_chunk"], language="markdown")

not_relevant = st.checkbox("Not relevant (e.g., index or non-substantive text)")

sentiment = None
if not not_relevant:
    sentiment = st.radio(
        "Sentiment (−2 = very negative, +2 = very positive)",
        [-2, -1, 0, 1, 2],
        horizontal=True
    )
else:
    st.info("Sentiment selection disabled because 'Not relevant' is checked.")
    
initials = st.text_input("Your initials")
comments = st.text_area("Optional comments")

if st.button("Submit"):
    data_to_save = [
        str(current_chunk["id"]),
        current_chunk["text_chunk"],
        "Not Relevant" if not_relevant else sentiment,
        initials,
        comments
    ]
    worksheet.append_row(data_to_save)
    st.success("Annotation saved!")

    if st.session_state.chunk_index + 1 < len(df):
        st.session_state.chunk_index = random.randint(0, len(df) - 1)
        st.rerun()
    else:
        st.balloons()
        st.markdown("🎉 All chunks labeled! Thank you!")

