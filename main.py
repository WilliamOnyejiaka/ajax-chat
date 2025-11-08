import streamlit as st

from src.repos.chat_repo import ChatRepository
from src.repos.user_repo import UserRepository

def create_indexes():
    user_repo = UserRepository()
    chat_repo = ChatRepository()

    user_repo.create_indexes()
    chat_repo.create_indexes()


st.set_page_config(page_title="Ajax AI", layout="wide")



# Define navigation
nav = st.navigation(
    {
        "Home": [st.Page("src/pages/home.py", title="🏠 Home")],
        "Auth": [
            st.Page("src/pages/auth/login.py", title="🔑 Login"),
            st.Page("src/pages/auth/sign_up.py", title="📝 Sign Up")
        ],
        "Chat": [st.Page("src/pages/ajax_chat.py", title="💬 Chat")],
    },
    # position="top"  # 👈 This puts it as a top navbar
)

# Run the selected page
nav.run()
