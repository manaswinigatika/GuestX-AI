import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from pymongo import MongoClient

# Streamlit Title
st.title("📊 Hotel Booking Forecast Dashboard")

# MongoDB Connection
client = MongoClient('mongodb+srv://gatikavinnivarma:uuQoNnIJECtLqyrq@cluster0.y0un9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client["hotel_guests"]
collection = db["bookings"]

df_from_mongo = pd.DataFrame(list(collection.find()))

# Data Preprocessing
df_bookings = df_from_mongo.copy()
df_bookings["check_in_date"] = pd.to_datetime(df_bookings["check_in_date"], format="%d-%m-%Y", errors="coerce")
df_bookings.dropna(subset=["check_in_date"], inplace=True)
df_bookings["Booking Count"] = 1

df_time_series = df_bookings.groupby("check_in_date").count().reset_index()
df_time_series = df_time_series[["check_in_date", "Booking Count"]]
df_time_series.columns = ["Date", "Bookings"]  # Renamed for clarity

# User Input for Forecast Period
forecast_days = st.slider("🔮 Select Forecast Period (days)", min_value=30, max_value=365, value=180)

# Prophet Model
model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
df_prophet = df_time_series.rename(columns={"Date": "ds", "Bookings": "y"})  # Prophet expects 'ds' & 'y'
model.fit(df_prophet)

# Generate Future Predictions
future_dates = model.make_future_dataframe(periods=forecast_days)
forecast = model.predict(future_dates)

# Rename Columns for Readability
forecast = forecast.rename(columns={
    "ds": "Date",
    "yhat": "Predicted Bookings",
    "yhat_lower": "Min Expected",
    "yhat_upper": "Max Expected"
})

# Display Forecast Data
st.subheader("📈 Predicted Hotel Bookings")
st.write(forecast[["Date", "Predicted Bookings", "Min Expected", "Max Expected"]].tail())

# Plot Forecast
st.subheader("📊 Forecast Visualization")
fig, ax = plt.subplots(figsize=(12, 6))
model.plot(forecast, ax=ax)
ax.set_title(f"Hotel Booking Forecast for Next {forecast_days} Days")
ax.set_xlabel("Date")
ax.set_ylabel("Number of Bookings")
st.pyplot(fig)

# Option to Download Forecast Data
st.subheader("📥 Download Forecast Data")
st.download_button(
    label="📥 Download CSV",
    data=forecast.to_csv(index=False).encode("utf-8"),
    file_name="hotel_forecast.csv",
    mime="text/csv"
)
