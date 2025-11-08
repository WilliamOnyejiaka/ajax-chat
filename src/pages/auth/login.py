import streamlit as st
from src.components.modal import alert_modal
from src.config import SECRET_KEY, COOKIE_PREFIX
from src.config.db import db
from src.repos.user_repo import UserRepository
from src.utils.password_util import verify_password
import json
from src.utils.cookie_manager import CookieManger

st.set_page_config(page_title="Login", page_icon="🔑", layout="centered")

cookie_manager = CookieManger(COOKIE_PREFIX, SECRET_KEY)

if not cookie_manager.ready():
    st.stop()

st.title("🔑 Login To Your Account")

def login_user(email: str, password: str):
    user_repo = UserRepository()

    try:
        # collection = db["admins"]
        user = user_repo.collection.find_one({"email": email})
        if user:
            valid_password = verify_password(password, user['password'])
            user["_id"] = str(user["_id"])
            del user['password']
            return {"error": False, "message": None, "user": user} if valid_password else {"error": True, "message": "Invalid password"}
        else:
            return {"error": True, "message": "User was not found"}
    except Exception as e:
        return {"error": True, "message": f"Something went wrong: {e}"}


with st.form("login", clear_on_submit=False):
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    submitted = st.form_submit_button("Login")

    st.page_link("src/pages/auth/sign_up.py",
                 label="📝 Don’t have an account? Sign up",)

    if submitted:
        if not email or not password:
            alert_modal("Please fill in all fields.")
        else:
            result = login_user(email, password)

            if result['error']:
                alert_modal(result['message'], level="error")
            else:
                cookie_manager.set("user", json.dumps(result['user']))
                st.session_state.was_loaded = True
                st.switch_page("src/pages/ajax_chat.py")
