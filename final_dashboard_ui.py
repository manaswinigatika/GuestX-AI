import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pymongo import MongoClient

# ---- 1. Page Config & Basic Styling ----
st.set_page_config(page_title="Hotel Analytics Dashboard", layout="wide")

# Inject some CSS for a sleeker look
st.markdown(
    """
    <style>
    /* General body styling */
    body {
        background-color: #F7F9FB;
        color: #333;
    }
    /* Titles and headers */
    h1, h2, h3, h4 {
        color: #4A76A8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Tabs text color */
    .stTabs [role='tab'] {
        color: #4A76A8;
    }
    /* Streamlit metric boxes */
    [data-testid="stMetricDelta"] > div:nth-child(2) {
        color: #FF6B6B;
    }
    /* Pie charts and other plots */
    .plotly-graph-div {
        background-color: #FFFFFF;
        border-radius: 10px;
    }
    /* Div styling for reviews */
    .review-box {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        line-height: 1.3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- 2. MongoDB Connection ----
MONGO_URI = "mongodb+srv://gatikavinnivarma:uuQoNnIJECtLqyrq@cluster0.y0un9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["hotel_guests"]

# ---- 3. Data Load Functions ----
@st.cache_data
def load_dining_data():
    df = pd.DataFrame(list(db.dining_info.find()))
    if not df.empty:
        df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
        df['check_in_date'] = pd.to_datetime(df['check_in_date'], errors='coerce')
        df['check_out_date'] = pd.to_datetime(df['check_out_date'], errors='coerce')
    return df

@st.cache_data
def load_booking_data():
    df = pd.DataFrame(list(db.bookings.find()))
    if not df.empty:
        df['check_in_date'] = pd.to_datetime(df['check_in_date'], format='%d-%m-%Y', errors='coerce')
        df['day_of_week'] = df['check_in_date'].dt.day_name()
        df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
        df['month'] = df['check_in_date'].dt.month
        df['year'] = df['check_in_date'].dt.year
    return df

@st.cache_data
def load_reviews():
    happy = list(db.reviews.find({"Rating": {"$gte": 8}}).sort("review_date_numeric", -1).limit(5))
    angry = list(db.reviews.find({"Rating": {"$lte": 5}}).sort("review_date_numeric", -1).limit(5))
    return happy, angry

# ---- 4. Main UI with Tabs ----
st.title("🏨 Hotel Analytics Dashboard")

tab1, tab2, tab3 = st.tabs(["🍽️ Dining Analytics", "📊 Booking Insights", "😊 Recent Reviews"])

# ---- 4.1 Dining Analytics Tab ----
with tab1:
    st.subheader("🍽️ Dining Analytics")
    df_dining = load_dining_data()
    
    if df_dining.empty:
        st.error("No dining data available. Please check your database connection.")
    else:
        # --- Key Metrics ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Orders", df_dining.shape[0])
        with col2:
            popular_cuisine = (
                df_dining['Preferred Cusine'].mode()[0]
                if not df_dining['Preferred Cusine'].isna().all()
                else "N/A"
            )
            st.metric("Most Popular Cuisine", popular_cuisine)
        with col3:
            if not df_dining['order_time'].isna().all():
                peak_order_hour = df_dining['order_time'].dt.hour.mode()[0]
            else:
                peak_order_hour = "N/A"
            st.metric("Peak Order Hour", peak_order_hour)

        # --- Interactive Visualizations ---
        tabA, tabB = st.tabs(["📊 Customer Behavior", "⏳ Temporal Patterns"])
        with tabA:
            if 'Preferred Cusine' in df_dining.columns and df_dining['Preferred Cusine'].dropna().any():
                cuisine_options = df_dining['Preferred Cusine'].dropna().unique()
                selected_cuisine = st.selectbox("Select Cuisine", cuisine_options)
                filtered_df = df_dining[df_dining['Preferred Cusine'] == selected_cuisine]

                if not filtered_df.empty:
                    fig = px.scatter(
                        filtered_df,
                        x='age',
                        y='price_for_1',
                        size='Qty',
                        color='number_of_stayers',
                        title=f'Customer Profile for {selected_cuisine}'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for the selected cuisine.")
            else:
                st.warning("No valid cuisine data found.")

        with tabB:
            if not df_dining['order_time'].isna().all():
                fig = px.histogram(
                    df_dining,
                    x=df_dining['order_time'].dt.hour,
                    nbins=24,
                    title='Order Time Distribution',
                    labels={'x': 'Hour of the Day'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No valid order time data available.")

        # --- AI Recommendations ---
        st.subheader("🔮 AI-Based Menu Optimization")
        if st.button("Generate Recommendations"):
            st.success("Suggested featured items: 🍱 Breakfast Thali & 🥗 Continental Combos")

# ---- 4.2 Booking Insights Tab ----
with tab2:
    st.subheader("📊 Booking Insights")
    df_bookings = load_booking_data()

    if df_bookings.empty:
        st.error("No booking data available. Please check your database connection.")
    else:
        # User selects month and year
        st.markdown("**Select Month and Year for Booking Predictions**")
        available_years = sorted(df_bookings['year'].dropna().unique())
        if len(available_years) == 0:
            st.warning("No valid year data found.")
        else:
            selected_year = st.selectbox("Select Year", available_years, index=len(available_years)-1)
            months_list = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            current_month_idx = datetime.today().month - 1
            selected_month = st.selectbox("Select Month", months_list, index=current_month_idx)
            month_number = datetime.strptime(selected_month, "%B").month

            # Filter data based on selected month/year
            monthly_data = df_bookings[
                (df_bookings['month'] == month_number) &
                (df_bookings['year'] == selected_year)
            ]

            # Show weekday vs weekend percentage
            if not monthly_data.empty:
                weekday_count = (monthly_data['is_weekend'] == False).sum()
                weekend_count = (monthly_data['is_weekend'] == True).sum()
                total_monthly = len(monthly_data)
                weekday_percentage = round(weekday_count / total_monthly * 100, 2)
                weekend_percentage = round(weekend_count / total_monthly * 100, 2)

                colA, colB = st.columns(2)
                with colA:
                    st.metric("📅 Weekday Bookings (%)", f"{weekday_percentage}%")
                with colB:
                    st.metric("🎉 Weekend Bookings (%)", f"{weekend_percentage}%")
            else:
                st.warning("No data available for the selected month and year.")

            # Weekday vs. Weekend Bookings
            st.subheader("📅 Weekday vs Weekend Bookings")
            if not monthly_data.empty:
                booking_counts = monthly_data['is_weekend'].value_counts().rename(index={True: 'Weekend', False: 'Weekday'})
                fig = px.pie(
                    values=booking_counts.values,
                    names=booking_counts.index,
                    title="Booking Distribution",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for the selected month and year.")

            # Aggregate bookings by date for trend analysis
            booking_trend = df_bookings.groupby('check_in_date').size()

            # Forecasting with Exponential Smoothing
            if not booking_trend.empty:
                st.subheader("📈 Future Booking Trends")
                model = ExponentialSmoothing(booking_trend, trend='add', seasonal='add', seasonal_periods=7)
                fit_model = model.fit()

                # Predict next 30 days
                last_date = booking_trend.index.max()
                future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=30)
                forecast = fit_model.forecast(30)
                st.line_chart(pd.Series(forecast.values, index=future_dates))

                # Predict Bookings for a Selected Date
                st.subheader("🔮 Predict Bookings for a Date")
                selected_date = st.date_input("Select a date:", min_value=datetime.today())
                if selected_date:
                    single_day_forecast = fit_model.forecast(1).iloc[0]
                    st.metric(
                        label=f"Estimated bookings on {selected_date.strftime('%Y-%m-%d')}",
                        value=int(single_day_forecast)
                    )

                # Predicted Bookings for Next Week
                st.subheader("📅 Next Week Predictions")
                next_week_dates = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
                next_week_forecast = fit_model.forecast(7)
                st.table({
                    "Date": [d.strftime('%Y-%m-%d') for d in next_week_dates],
                    "Predicted Bookings": next_week_forecast.astype(int)
                })

            # Interactive Booking Trends
            st.subheader("📊 Previous Booking Trends")
            if not df_bookings['check_in_date'].isna().all():
                trend_start_date = st.date_input("Start Date", df_bookings['check_in_date'].min())
                trend_end_date = st.date_input("End Date", df_bookings['check_in_date'].max())
                filtered_counts = df_bookings[
                    (df_bookings['check_in_date'] >= pd.to_datetime(trend_start_date)) &
                    (df_bookings['check_in_date'] <= pd.to_datetime(trend_end_date))
                ].groupby('check_in_date').size()

                if not filtered_counts.empty:
                    st.line_chart(filtered_counts)
                else:
                    st.warning("No data available for the selected date range.")
            else:
                st.warning("No valid check_in_date data to display trends.")

# ---- 4.3 Recent Reviews Tab ----
with tab3:
    st.subheader("😊 Recent Happy & 😡 Angry Reviews")
    happy_reviews, angry_reviews = load_reviews()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 😊 Happy Reviews")
        if happy_reviews:
            for review in happy_reviews:
                st.markdown(
                    f"""
                    <div class="review-box" style="border: 2px solid green; background-color: #eaffea;">
                        <b>⭐ Rating:</b> {review.get('Rating', 'N/A')}<br>
                        <b>📝 Review:</b> {review.get('Review', 'N/A')}<br>
                        <b>📅 Date:</b> {review.get('review_date', 'N/A')}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("No happy reviews found.")

    with col2:
        st.markdown("#### 😡 Angry Reviews")
        if angry_reviews:
            for review in angry_reviews:
                st.markdown(
                    f"""
                    <div class="review-box" style="border: 2px solid red; background-color: #ffeaea;">
                        <b>⭐ Rating:</b> {review.get('Rating', 'N/A')}<br>
                        <b>📝 Review:</b> {review.get('Review', 'N/A')}<br>
                        <b>📅 Date:</b> {review.get('review_date', 'N/A')}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("No angry reviews found.")
