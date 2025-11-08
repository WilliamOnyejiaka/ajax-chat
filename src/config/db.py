import streamlit as st
from pymongo import MongoClient

MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = st.secrets["DB_NAME"]

@st.cache_resource
def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


db = get_db()
