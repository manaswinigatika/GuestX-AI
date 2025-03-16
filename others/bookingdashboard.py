import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from datetime import datetime, timedelta
from pymongo import MongoClient
import plotly.express as px

# Streamlit App Title
st.title("📊 Hotel Booking Insights Dashboard")

# Connect to MongoDB
client = MongoClient('mongodb+srv://gatikavinnivarma:uuQoNnIJECtLqyrq@cluster0.y0un9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client["hotel_guests"]
collection = db["bookings"]

# Load and preprocess data
data = list(collection.find())
df = pd.DataFrame(data)

# Ensure date format conversion
df['check_in_date'] = pd.to_datetime(df['check_in_date'], format='%d-%m-%Y')
df['day_of_week'] = df['check_in_date'].dt.day_name()
df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
df['month'] = df['check_in_date'].dt.month
df['year'] = df['check_in_date'].dt.year

# User selects month and year
st.subheader("📆 Select Month and Year for Booking Predictions")
selected_year = st.selectbox("Select Year", sorted(df['year'].unique()), index=len(df['year'].unique())-1)
selected_month = st.selectbox("Select Month", 
    ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 
    index=datetime.today().month-1)

# Convert selected month to numeric format
month_number = datetime.strptime(selected_month, "%B").month

# Filter data based on selected month and year
monthly_data = df[(df['month'] == month_number) & (df['year'] == selected_year)]

# Show weekday vs weekend percentage
if not monthly_data.empty:
    weekday_percentage = round((monthly_data['is_weekend'] == False).sum() / len(monthly_data) * 100, 2)
    weekend_percentage = round((monthly_data['is_weekend'] == True).sum() / len(monthly_data) * 100, 2)
    st.metric("📅 Weekday Bookings Percentage", f"{weekday_percentage}%")
    st.metric("🎉 Weekend Bookings Percentage", f"{weekend_percentage}%")
else:
    st.warning("No data available for the selected month and year.")

# Weekday vs. Weekend Bookings (Updated to reflect selected month)
st.subheader("📅 Weekday vs Weekend Bookings")
if not monthly_data.empty:
    booking_counts = monthly_data['is_weekend'].value_counts().rename(index={True: 'Weekend', False: 'Weekday'})
    fig = px.pie(
        values=booking_counts.values, 
        names=booking_counts.index, 
        title="Booking Distribution", 
        hole=0.4, 
        color=booking_counts.index, 
        color_discrete_map={'Weekend': 'blue', 'Weekday': 'green'}
    )
    st.plotly_chart(fig)
else:
    st.warning("No data available for the selected month and year.")

# Aggregate bookings by date for trend analysis
booking_trend = df.groupby('check_in_date').size()

# Forecasting with Exponential Smoothing
if not booking_trend.empty:
    model = ExponentialSmoothing(booking_trend, trend='add', seasonal='add', seasonal_periods=7)
    fit_model = model.fit()

    # Future Booking Prediction
    st.subheader("📈 Future Booking Trends")
    future_dates = pd.date_range(df['check_in_date'].max() + pd.Timedelta(days=1), periods=30)
    forecast = fit_model.forecast(30)
    st.line_chart(pd.Series(forecast.values, index=future_dates))

    # Predict Bookings for a Selected Date
    st.subheader("🔮 Predict Bookings for a Date")
    selected_date = st.date_input("Select a date:", min_value=datetime.today())
    if selected_date:
        predicted_value = fit_model.forecast(1).iloc[0]
        st.metric(label=f"Estimated bookings on {selected_date.strftime('%Y-%m-%d')}", value=int(predicted_value))

    # Predicted Bookings for Next Week
    st.subheader("📅 Next Week Predictions")
    next_week_dates = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
    next_week_forecast = fit_model.forecast(7)
    st.table({"Date": [d.strftime('%Y-%m-%d') for d in next_week_dates], "Predicted Bookings": next_week_forecast.astype(int)})

# Interactive Booking Trends
st.subheader("📊 Previous Booking Trends")
trend_start_date = st.date_input("Start Date", df['check_in_date'].min())
trend_end_date = st.date_input("End Date", df['check_in_date'].max())

filtered_counts = df[(df['check_in_date'] >= pd.to_datetime(trend_start_date)) & 
                      (df['check_in_date'] <= pd.to_datetime(trend_end_date))].groupby('check_in_date').size()

st.line_chart(filtered_counts)
