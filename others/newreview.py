import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_together import TogetherEmbeddings
from pinecone import Pinecone
from together import Together
from datetime import datetime
import os

# Set environment variables 
os.environ["TOGETHER_API_KEY"] = '3f01b9d9ddce6978f90d9daffd9b801f13f517267587cf9c736a1ffe6a60ba5f'

# Initialize Pinecone
pc = Pinecone(api_key='pcsk_7Syt4B_2MSNqwKrW1cdtjUTR7ukDQXCQc481bmu5o9FFYDFfwefHXLJxf2XghRFWvSEY9g')
index = pc.Index(host="https://hotel-reviews-woqlw1a.svc.aped-4627-b74a.pinecone.io")

# Initialize Together embedding model
embeddings = TogetherEmbeddings(
    model='togethercomputer/m2-bert-80M-8k-retrieval',
    together_api_key=os.environ["TOGETHER_API_KEY"]
)



# Streamlit UI
st.markdown("<h1 style='text-align: center;'>Hotel Review Submission</h1>", unsafe_allow_html=True)

# Input form for customer review
with st.form("review_form"):
    customer_id = st.text_input("Customer ID")
    room_number = st.text_input("Room Number")
    rating = st.slider("Rating", 1, 10, 5)
    review = st.text_area("Your Review")
    currently_staying = st.checkbox("I am currently staying at the hotel")
    
    submitted = st.form_submit_button("Submit Review")
    
    if submitted:
        if not customer_id or not review or not room_number:
            st.error("Please fill in all required fields.")
        else:
            try:
                # Load existing data
                df = pd.read_excel(r"C:\Users\VINNI\OneDrive\Desktop\infosys internship\reviews_data.xlsx")
                
                # Generate new review ID
                new_review_id = df['review_id'].max() + 1 if not df.empty else 1
                
                # Current date in format YYYYMMDD
                today = datetime.now()
                date_str = int(today.strftime("%Y%m%d"))
                
                # Create new row for dataframe
                new_review = {
                    'review_id': new_review_id,
                    'customer_id': customer_id,
                    'room_number': room_number,
                    'Review': review,
                    'Rating': rating,
                    'review_date': date_str,
                    'currently_staying': currently_staying
                }
                
                # Add to dataframe
                df = pd.concat([df, pd.DataFrame([new_review])], ignore_index=True)
                
                # Save updated dataframe
                df.to_excel(r'C:\Users\VINNI\OneDrive\Desktop\infosys internship\reviews_data.xlsx', index=False)
                
                # Create embedding for the new review
                review_embedding = embeddings.embed_query(review)
                
                # Define metadata
                metadata = {
                    'review_id': str(new_review_id),
                    'customer_id': customer_id,
                    'room_number': room_number,
                    'Rating': rating,
                    'review_date': date_str,
                    'currently_staying': currently_staying
                }
                
                # Upload to Pinecone
                index.upsert(
                    vectors=[
                        {
                            "id": f"review_{new_review_id}",
                            "values": review_embedding,
                            "metadata": metadata
                        }
                    ],
                )
                
                st.success("Your review has been submitted successfully!")
                
           
                        
            except Exception as e:
                st.error(f"Error submitting review: {str(e)}")
