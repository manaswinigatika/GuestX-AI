from pinecone import Pinecone
import os
import random
import pandas as pd
import streamlit as st

# Load existing reviews
df = pd.read_excel('C:\Users\VINNI\OneDrive\Desktop\infosys internship\reviews_data.xlsx')

# Set API keys
os.environ["TOGETHER_API_KEY"] = "3f01b9d9ddce6978f90d9daffd9b801f13f517267587cf9c736a1ffe6a60ba5f"

# Initialize Pinecone and Together Embeddings
pc = Pinecone(api_key="pcsk_7Syt4B_2MSNqwKrW1cdtjUTR7ukDQXCQc481bmu5o9FFYDFfwefHXLJxf2XghRFWvSEY9g")
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")
index = pc.Index(host="https://hotel-reviews-woqlw1a.svc.aped-4627-b74a.pinecone.io")
client = Together()

# Function to generate a new review ID
def generate_review_id():
    return max(df["review_id"].tolist()) + random.randint(15000, 100000)

# Function to convert date to numeric format
def convert_date_to_numeric(date_str):
    return int(date_str.replace("-", ""))

# Streamlit UI
st.title("Customer Review Submission")

customer_id = st.text_input("Enter your Customer ID:")
review_text = st.text_area("Enter your review:")
rating = st.slider("Rating", min_value=1.0, max_value=10.0, step=0.1)
staying_now = st.radio("Are you currently staying at the hotel?", ("Yes", "No"))
submit = st.button("Submit Review")

if submit and review_text and customer_id:
    review_id = generate_review_id()
    st.success(f"Review submitted successfully! Your Review ID: {review_id}")
