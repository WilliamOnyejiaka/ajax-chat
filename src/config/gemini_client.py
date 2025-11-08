from google import genai
from src.config import API_KEY
import streamlit as st

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=API_KEY)

client = get_gemini_client()