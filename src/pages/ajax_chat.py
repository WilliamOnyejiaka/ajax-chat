import json
import streamlit as st
from bson import ObjectId
from google.genai import types
from pymongo import DESCENDING
from datetime import datetime, UTC
from src.config import COOKIE_PREFIX, SECRET_KEY
from src.config.gemini_client import client
from src.repos.chat_repo import ChatRepository
from src.repos.message_repo import MessageRepository
from src.utils.cookie_manager import CookieManger

st.set_page_config(page_title="Chat", page_icon="💬", layout="centered")

cookie_manager = CookieManger(COOKIE_PREFIX, SECRET_KEY)

if not cookie_manager.ready():
    st.stop()

# --- Page Layout ---
current_user = cookie_manager.get("user")

if current_user == "":
    st.warning("You’re not logged in! Go to the Login page.")
    st.switch_page("src/pages/auth/login.py")

current_user = json.loads(current_user)
chat_repo = ChatRepository()
message_repo = MessageRepository()
default_message = {"role": "model", "content": "Hi! I'm Ajax. Ask me anything!"}

# --- State Initialization ---
# Initialize chat history (current session)
if "messages" not in st.session_state:
    st.session_state.messages = [default_message]
    st.session_state.current_chat_id = ""

# Initialize past chat storage
if "past_chats" not in st.session_state:
    st.session_state.past_chats = []
# Initialize a title for the current chat session
if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "New Chat"

def start_new_chat():
    st.session_state.messages = [default_message]
    st.session_state.current_chat_title = "New Chat"
    st.rerun()


def load_past_chat(loaded_chat_id):
    try:
        loaded_chat = chat_repo.chat_with_messages(loaded_chat_id)[0]

        st.session_state.messages = []

        for message in loaded_chat['messages']:
            st.session_state.messages.append(message['message'])

        st.session_state.current_chat_title = loaded_chat["title"]
        st.session_state.current_chat_id = loaded_chat_id
        st.rerun()

    except Exception as e:
        print(f"Error: {type(e).__name__} - {str(e)}")


# --- Sidebar: History & Settings ---
with (st.sidebar):
    st.markdown("## Current Session")
    # Button to start a new chat
    if st.button("➕ Start New Chat", use_container_width=True):
        start_new_chat()

    st.markdown("---")
    st.markdown("## Chat History")
    past_chats = []

    try:
        past_chats = chat_repo.collection.find(
            {"user_id": ObjectId(current_user['_id'])}
        ).sort("updated_at", DESCENDING).to_list()

        for chat in past_chats:
            chat['_id'] = str(chat['_id'])
            chat['user_id'] = str(chat['user_id'])

    except Exception as e:
        st.error(f"Error: {type(e).__name__} - {str(e)}")

    st.session_state.past_chats = past_chats

    if st.session_state.past_chats:
        for i, chat in enumerate(st.session_state.past_chats):
            display_title = chat["title"]
            chat_id = chat['_id']

            col1, col2 = st.columns([4, 2])
            with col1:
                st.markdown(f"**{display_title}**", )
            with col2:
                if st.button("Load", key=f"load_{i}"):
                    load_past_chat(chat_id)
    else:
        st.info("No past chats saved yet.")

# --- App UI ---
st.title("Ajax Chat AI")
st.caption(f"Powered by Sly • **Session: {st.session_state.current_chat_title}**")

# Display history
for msg in st.session_state.messages:
    # Map 'model' role to 'assistant' for the Streamlit icon
    with st.chat_message(msg["role"] if msg["role"] != "model" else "assistant"):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    new_user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(new_user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            # Convert Streamlit's simple history format into the SDK's expected Content/Part format
            contents = []
            for m in st.session_state.messages:
                # Map Streamlit role ('user', 'model') to the SDK's role ('user', 'model')
                role = m['role'] if m['role'] != 'assistant' else 'model'
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=m['content'])]
                    )
                )

            # Use generate_content_stream for real-time output
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=contents,  # Pass the entire conversation history
            )

            # Iterate through the stream and update the placeholder
            for chunk in response_stream:
                full_response += chunk.text
                # Display the partial response with a cursor effect
                placeholder.markdown(full_response + "▌")

            # Final display without the cursor
            placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Error: {type(e).__name__} - {str(e)}")
            full_response = "Sorry, something went wrong. Try again!"

    try:
        current_chat_id = st.session_state.current_chat_id
        messages = []

        if st.session_state.current_chat_title == "New Chat":
            new_title = prompt[:30].strip() + "..."
            st.session_state.current_chat_title = new_title
            current_chat_id = chat_repo.create_chat({
                "user_id": ObjectId(current_user['_id']),
                "title": new_title,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            })

            messages.append({
                "chat_id": ObjectId(current_chat_id),
                "message": default_message,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            })

        new_ajax_message = {"role": "model", "content": full_response}
        st.session_state.messages.append(new_ajax_message)

        messages.append({
            "chat_id": ObjectId(current_chat_id),
            "message": new_user_message,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        })
        messages.append({
            "chat_id": ObjectId(current_chat_id),
            "message": new_ajax_message,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        })
        message_repo.collection.insert_many(messages)

    except Exception as e:
        st.error(f"Error: {type(e).__name__} - {str(e)}")
