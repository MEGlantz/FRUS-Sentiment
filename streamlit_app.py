
import streamlit as st
import pandas as pd
import random
import os

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("frus_1961_63_volume5_chunks.csv")
    return df

df = load_data()

# Get a random row
if "seen_ids" not in st.session_state:
    st.session_state.seen_ids = set()

unseen = df[~df['id'].isin(st.session_state.seen_ids)]
if unseen.empty:
    st.success("You've labeled all the available chunks!")
    st.stop()

row = unseen.sample(1).iloc[0]
st.session_state.seen_ids.add(row['id'])

# UI
st.title("FRUS Sentiment Labeling Tool")
st.markdown("Label sentiment on a -2 to +2 scale. Your initials and optional comments are helpful.")

st.subheader("Document Excerpt")
st.markdown(
    f"""
    <div style="padding: 1em; background-color: #f9f9f9; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; line-height: 1.6;">
        {row["text_chunk"]}
    </div>
    """,
    unsafe_allow_html=True
)
# Form
with st.form("label_form"):
    sentiment = st.radio(
        "Sentiment (-2 = Very Negative, 0 = Neutral, +2 = Very Positive)",
        [-2, -1, 0, 1, 2], horizontal=True
    )
    initials = st.text_input("Your Initials (or leave blank)")
    comments = st.text_area("Optional Comments")
    submitted = st.form_submit_button("Submit")

# Save response
if submitted:
    result = {
        "id": row["id"],
        "text_chunk": row["text_chunk"],
        "sentiment": sentiment,
        "initials": initials,
        "comments": comments
    }
    out_df = pd.DataFrame([result])
    out_path = "annotations.csv"
    if os.path.exists(out_path):
        out_df.to_csv(out_path, mode="a", index=False, header=False)
    else:
        out_df.to_csv(out_path, index=False)

    st.success("Submitted! You can now refresh or label another item.")
    st.stop()
