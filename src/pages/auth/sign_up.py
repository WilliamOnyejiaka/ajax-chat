import json
import streamlit as st
from src.components.modal import alert_modal
from src.config import ACCESS_KEY, SECRET_KEY, COOKIE_PREFIX
from src.repos.user_repo import UserRepository
from src.utils.cookie_manager import CookieManger
from src.utils.password_util import hash_password

st.set_page_config(page_title="Sign Up", page_icon="📝", layout="centered")

st.title("📝 Create Your Account")

cookie_manager = CookieManger(COOKIE_PREFIX, SECRET_KEY)

if not cookie_manager.ready():
    st.stop()


def create_user(name: str, email: str, password: str):
    user_repo = UserRepository()
    try:
        email_exists = user_repo.collection.find_one({"email": email})
        if not email_exists:
            hashed_password = hash_password(password)
            result = user_repo.create_user({
                "name": name,
                "email": email,
                "password": hashed_password
            })

            if result:
                return {"error": False, "message": None, "user": {
                    "name": name,
                    "email": email,
                    "_id": result
                }}
            return {"error": True, "message": "Something went wrong"}
        else:
            return {"error": True, "message": "Email already exists"}
    except Exception as e:
        return {"error": True, "message": f"Something went wrong: {e}"}


with st.form("signup_form", clear_on_submit=False):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    submitted = st.form_submit_button("Sign Up")

    if submitted:
        if not full_name or not email or not password:
            alert_modal("Please fill in all fields.")
        elif password != confirm_password:
            alert_modal("Passwords do not match.", level="error")
        else:
            result = create_user(full_name, email, password)
            if result['error']:
                alert_modal(result['message'], level="error")
            else:
                cookie_manager.set("user", json.dumps(result["user"]))
                st.session_state.was_loaded = True
                st.switch_page("src/pages/ajax_chat.py")
