import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load the .env file
load_dotenv()

# Get the MongoDB URI from environment
mongo_uri = os.getenv("MONGODB_URI")

# Connect to MongoDB Atlas
client = MongoClient(mongo_uri)

# Select your database and collection
db = client["bible_messages"]
collection = db["messages"]

import streamlit as st
from datetime import date

# --- Page Config ---
st.set_page_config(page_title="Bible Message Journal", layout="wide")

# --- In-Memory Storage (for now) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Navigation ---
st.sidebar.title("📖 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Add Message", "View Messages"])

# --- Home Page ---
if page == "Home":
    st.title("📖 Bible Message Journal")
    st.subheader("Your personal archive of Bible messages")

    st.info("Use the sidebar to add or view messages.")
    st.metric("Total Messages", len(st.session_state.messages))

    if st.session_state.messages:
        st.subheader("🕊️ Recent Messages")
        for msg in reversed(st.session_state.messages[-3:]):
            st.markdown(f"**{msg['title']}** by *{msg['speaker']}* on {msg['date']}")
            st.text(msg['summary'])

# --- Add Message Page ---
elif page == "Add Message":
    st.title("📝 Add a New Message")

    with st.form("message_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Message Title", max_chars=100)
            speaker = st.text_input("Speaker / Pastor")
            date_given = st.date_input("Date", value=date.today())
        with col2:
            church = st.text_input("Church / Event")
            tags = st.text_input("Tags / Topics (comma separated)")
            verses = st.text_input("Bible Verses (e.g., John 3:16, Romans 8:28)")

        summary = st.text_area("Message Summary", height=100)
        full_message = st.text_area("Full Message / Notes", height=200)

        submitted = st.form_submit_button("Add Message")

        if submitted:
            new_message = {
                "title": title,
                "speaker": speaker,
                "date": str(date_given),
                "church": church,
                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                "verses": verses,
                "summary": summary,
                "full_message": full_message,
            }
            st.session_state.messages.append(new_message)
            st.success("Message added successfully!")

# --- View Messages Page ---
elif page == "View Messages":
    st.title("📚 View All Messages")

    if not st.session_state.messages:
        st.warning("No messages added yet.")
    else:
        # Filters
        speakers = sorted(set(msg["speaker"] for msg in st.session_state.messages))
        tags = sorted({tag for msg in st.session_state.messages for tag in msg["tags"]})

        col1, col2 = st.columns(2)
        selected_speaker = col1.selectbox("Filter by Speaker", ["All"] + speakers)
        selected_tag = col2.selectbox("Filter by Tag", ["All"] + tags)

        for msg in reversed(st.session_state.messages):
            if (selected_speaker != "All" and msg["speaker"] != selected_speaker) or \
               (selected_tag != "All" and selected_tag not in msg["tags"]):
                continue

            with st.expander(f"📌 {msg['title']} — *{msg['speaker']}* ({msg['date']})"):
                st.markdown(f"**Church/Event:** {msg['church']}")
                st.markdown(f"**Verses:** {msg['verses']}")
                st.markdown(f"**Tags:** {', '.join(msg['tags'])}")
                st.markdown(f"**Summary:** {msg['summary']}")
                st.markdown("---")
                st.markdown(f"**Full Message:**\n{msg['full_message']}")

