import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px

# Function to load data from MongoDB
def load_data():
    client = MongoClient('mongodb+srv://gatikavinnivarma:uuQoNnIJECtLqyrq@cluster0.y0un9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client["hotel_guests"]
    df = pd.DataFrame(list(db.dining_info.find()))

    # Convert time columns to datetime
    df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
    df['check_in_date'] = pd.to_datetime(df['check_in_date'], errors='coerce')
    df['check_out_date'] = pd.to_datetime(df['check_out_date'], errors='coerce')

    return df

# Set Streamlit Page Config
st.set_page_config(page_title="Dining Analytics", layout="wide")

# Load and clean data
df = load_data()

st.title("🍽️ Hotel Dining Analytics Dashboard")

# Handle missing values
if df.empty:
    st.error("No data available. Please check your database connection.")
else:
    # Section 1: Key Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", df.shape[0])
    with col2:
        st.metric("Most Popular Cuisine", df['Preferred Cusine'].mode()[0] if not df['Preferred Cusine'].isna().all() else "N/A")
    with col3:
        peak_order_hour = df['order_time'].dt.strftime('%H:%M:%S').mode()[0] if not df['order_time'].isna().all() else "N/A"
        st.metric("Peak Order Hour", peak_order_hour)

    # Section 2: Interactive Visualizations
    tab1, tab2 = st.tabs(["📊 Customer Behavior", "⏳ Temporal Patterns"])

    with tab1:
        selected_cuisine = st.selectbox('Select Cuisine', df['Preferred Cusine'].dropna().unique())
        filtered_df = df[df['Preferred Cusine'] == selected_cuisine]

        if not filtered_df.empty:
            fig = px.scatter(filtered_df, x='age', y='price_for_1',
                             size='Qty', color='number_of_stayers',
                             title=f'Customer Profile for {selected_cuisine}')
            st.plotly_chart(fig)
        else:
            st.warning("No data available for the selected cuisine.")

    with tab2:
        if not df['order_time'].isna().all():
            fig = px.histogram(df, x=df['order_time'].dt.hour, nbins=24, title='Order Time Distribution', labels={'x': 'Hour of the Day'})
            st.plotly_chart(fig)
        else:
            st.warning("No valid order time data available.")

    # Section 3: AI Recommendations
    st.header("🔮 AI-Based Menu Optimization")
    if st.button('Generate Recommendations'):
        st.success("Suggested featured items: 🍱 Breakfast Thali & 🥗 Continental Combos")

