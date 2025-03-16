import streamlit as st
import pymongo
import pandas as pd

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://gatikavinnivarma:uuQoNnIJECtLqyrq@cluster0.y0un9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["hotel_guests"]
collection = db["reviews"]

# Fetch recent happy (rating >= 8) and angry (rating <= 5) reviews
happy_reviews = list(collection.find({"Rating": {"$gte": 8}}).sort("review_date_numeric", -1).limit(5))
angry_reviews = list(collection.find({"Rating": {"$lte": 5}}).sort("review_date_numeric", -1).limit(5))

# Streamlit UI
st.set_page_config(page_title="Hotel Reviews Dashboard", layout="wide")
st.title("😊 Recent Happy & 😡 Angry Reviews")

# Layout with two columns
col1, col2 = st.columns(2)

# Happy Reviews Section
with col1:
    st.subheader("😊 Happy Reviews")
    for review in happy_reviews:
        st.markdown(f"""
        <div style="border: 2px solid green; padding: 10px; margin: 10px; border-radius: 10px; background-color: #eaffea;">
            <b>⭐ Rating:</b> {review['Rating']} <br>
            <b>📝 Review:</b> {review['Review']} <br>
            <b>📅 Date:</b> {review['review_date']}
        </div>
        """, unsafe_allow_html=True)

# Angry Reviews Section
with col2:
    st.subheader("😡 Angry Reviews")
    for review in angry_reviews:
        st.markdown(f"""
        <div style="border: 2px solid red; padding: 10px; margin: 10px; border-radius: 10px; background-color: #ffeaea;">
            <b>⭐ Rating:</b> {review['Rating']} <br>
            <b>📝 Review:</b> {review['Review']} <br>
            <b>📅 Date:</b> {review['review_date']}
        </div>
        """, unsafe_allow_html=True)

# Run: streamlit run app.py
