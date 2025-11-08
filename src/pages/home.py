import streamlit as st
from src.components.modal import alert_modal
from src.config import SECRET_KEY, COOKIE_PREFIX
from src.utils.cookie_manager import CookieManger

st.set_page_config(page_title="Home", page_icon="🏠")

st.title("🏠 Home Page")

# --- Page setup ---
st.set_page_config(
    page_title="Ajax AI",
    page_icon="🏠",
    layout="centered"
)

cookie_manager = CookieManger(COOKIE_PREFIX, SECRET_KEY)

if not cookie_manager.ready():
    st.stop()

# --- Landing Page Content ---
st.title("👋 Welcome to Ajax Chat")
st.subheader("Your gateway to awesome features 🚀")

st.markdown(
    """
    ### Get started
    Choose what you’d like to do:
    """
)

# --- Action buttons ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔑 Log In"):
        st.switch_page("src/pages/auth/login.py")

with col2:
    if st.button("🏃 Logout"):
        cookie_manager.delete("user")
        alert_modal("You have been logged out successfully", "success")

with col3:
    if st.button("📝 Sign Up"):
        st.switch_page("src/pages/auth/sign_up.py")

# --- Optional footer ---
st.markdown("---")
st.caption("© 2025 Ajax")
