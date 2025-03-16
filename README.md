# GuestX-AI
# GuestX-AI: AI-Powered Guest Experience Personalization System

## Overview

GuestX-AI is an AI-powered system designed to enhance guest experiences in the hospitality industry. It leverages machine learning, NLP, and interactive dashboards to personalize dining recommendations, analyze guest reviews, and provide hotel management with actionable insights.

## Features

- **Predict Favorite Dishes**: Uses XGBoost to recommend dishes based on guest dining behavior.
- **Review Sentiment Analysis**: NLP-powered analysis of customer reviews to determine sentiment.
- **Interactive Dashboards**: Visualizes booking trends, dining preferences, and sentiment analysis using Dash & Plotly.
- **Real-Time Review Alerts**: Sends automated alerts to hotel management if a guest staying in the hotel gives a negative review.
- **Streamlit UI**: User-friendly interface for dish recommendations and review analysis.

## Project Modules

### **Module 1: Predicting Customer's Favorite Dish**

- Trains an XGBoost model to predict a customer’s favorite dish.
- Preprocesses data, performs feature engineering, and applies one-hot encoding.
- Outputs a trained model used for dish recommendations.

**Key Files:**

- `ass1_dining_xgboost.ipynb`: Develops and trains the XGBoost model.
- `training_and_features.py`: Data preprocessing and feature engineering.
- `demo.py`: Streamlit app for dish prediction.
- `featureimportance.png`: Feature importance visualization.

### **Module 2: Database & UI Setup**

- Stores customer and dining data in MongoDB.
- Implements a hotel booking form UI for data entry.
- Runs the trained model and serves predictions via Streamlit.

**Key Files:**

- `customer_features.xlsx`, `cuisine_features.xlsx`, `features.xlsx`
- `encoder.pkl`, `label_encoder.pkl`, `xgb_model_dining.pkl`
- `demo.py`: Streamlit-based deployment.
- **Hotel booking form UI**

### **Module 3: Review Sentiment Analysis**

- Uses Pinecone and Together.AI for NLP and vector search.
- Implements a sentiment analysis UI.
- Sends automated emails for negative reviews.

**Key Files:**

- `ass3 - review analysis.ipynb`: NLP-based sentiment analysis.
- `review_sentimentanalysisUI.py`: UI for analyzing and visualizing review sentiments.
- `newreview.py`: Processes new reviews.
- `email sending code part.py`: Automates email notifications.
- `UI1 - review analysis.png`, `UI2 - review analysis.png`: UI outputs.

### **Module 4: Data Storage, Processing & Dashboards**

- Stores booking, dining, and review data in MongoDB.
- Fetches and processes data using Pandas.
- Creates interactive dashboards with Dash & Plotly.
- Integrates sentiment analysis with real-time email alerts.

**Key Files:**

- `bookingdashboard.py`: Hotel booking insights dashboard.
- `diningdashboard.py`: Dining trends dashboard.
- `reviewsdashboard.py`: Sentiment analysis visualization.
- `final_dashboard_ui.py`: Integrated UI.
- `report output dashboard.pdf`, `output UI images`: Documentation and UI snapshots.
