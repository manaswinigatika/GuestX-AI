import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from datetime import datetime, timedelta

# MongoDB Connection
client = MongoClient('mongodb+srv://gatikavinnivarma:uuQoNnIJECtLqyrq@cluster0.y0un9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client["hotel_guests"]

# Load Data Functions
def load_dining_data():
    df = pd.DataFrame(list(db.dining_info.find()))
    df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
    df['check_in_date'] = pd.to_datetime(df['check_in_date'], errors='coerce')
    df['check_out_date'] = pd.to_datetime(df['check_out_date'], errors='coerce')
    return df

def load_booking_data():
    df = pd.DataFrame(list(db.bookings.find()))
    df['check_in_date'] = pd.to_datetime(df['check_in_date'], format='%d-%m-%Y')
    df['day_of_week'] = df['check_in_date'].dt.day_name()
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
    df['month'] = df['check_in_date'].dt.month
    df['year'] = df['check_in_date'].dt.year
    return df

def load_reviews():
    reviews = list(db.reviews.find())
    return pd.DataFrame(reviews)

# Streamlit UI
st.set_page_config(page_title="Hotel Analytics Dashboard", layout="wide")
st.title("🏨 Hotel Analytics Dashboard")

# Sidebar for Navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Dining Analytics", "Booking Insights", "Customer Reviews"])

if section == "Dining Analytics":
    df = load_dining_data()
    if df.empty:
        st.error("No dining data available.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Orders", df.shape[0])
        with col2:
            st.metric("Most Popular Cuisine", df['Preferred Cusine'].mode()[0] if not df['Preferred Cusine'].isna().all() else "N/A")
        with col3:
            peak_hour = df['order_time'].dt.hour.mode()[0] if not df['order_time'].isna().all() else "N/A"
            st.metric("Peak Order Hour", peak_hour)

        selected_cuisine = st.selectbox('Select Cuisine', df['Preferred Cusine'].dropna().unique())
        filtered_df = df[df['Preferred Cusine'] == selected_cuisine]
        if not filtered_df.empty:
            fig = px.scatter(filtered_df, x='age', y='price_for_1', size='Qty', color='number_of_stayers')
            st.plotly_chart(fig)
        
        if st.button('Generate AI Recommendations'):
            st.success("Suggested Menu: 🍱 Breakfast Thali & 🥗 Continental Combos")

elif section == "Booking Insights":
    df = load_booking_data()
    selected_year = st.selectbox("Select Year", sorted(df['year'].unique()), index=len(df['year'].unique())-1)
    selected_month = st.selectbox("Select Month", list(range(1, 13)), index=datetime.today().month-1)
    monthly_data = df[(df['month'] == selected_month) & (df['year'] == selected_year)]
    
    if not monthly_data.empty:
        booking_counts = monthly_data['is_weekend'].value_counts().rename(index={True: 'Weekend', False: 'Weekday'})
        fig = px.pie(values=booking_counts.values, names=booking_counts.index)
        st.plotly_chart(fig)
    
        booking_trend = df.groupby('check_in_date').size()
        if not booking_trend.empty:
            model = ExponentialSmoothing(booking_trend, trend='add', seasonal='add', seasonal_periods=7).fit()
            future_dates = pd.date_range(df['check_in_date'].max() + pd.Timedelta(days=1), periods=30)
            forecast = model.forecast(30)
            st.line_chart(pd.Series(forecast.values, index=future_dates))

elif section == "Customer Reviews":
    reviews_df = load_reviews()
    if reviews_df.empty:
        st.warning("No reviews available.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("😊 Happy Reviews")
            happy_reviews = reviews_df[reviews_df['Rating'] >= 8].head(5)
            for _, review in happy_reviews.iterrows():
                st.markdown(f"**⭐ Rating:** {review['Rating']}\n**📝 Review:** {review['Review']}")
        with col2:
            st.subheader("😡 Angry Reviews")
            angry_reviews = reviews_df[reviews_df['Rating'] <= 5].head(5)
            for _, review in angry_reviews.iterrows():
                st.markdown(f"**⭐ Rating:** {review['Rating']}\n**📝 Review:** {review['Review']}")
