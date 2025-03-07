# GuestX-AI
AI-Powered Guest Experience Personalization uses LLMs like OpenAI GPT and Meta LLaMA to analyze guest feedback (mock CRM data), track sentiment trends, and personalize recommendations for amenities and activities. Real-time alerts enable service teams to adapt dynamically, ensuring tailored experiences that evolve with guest preferences.

Personalized Recommendations: Dining, activity, and amenity suggestions based on guest behavior analysis.

Real-Time Sentiment Monitoring: Proactively addresses guest feedback for improved satisfaction.

Enhanced Guest Experience: Dynamic personalization increases guest satisfaction and engagement.

Automated Alerts: Staff receive notifications to resolve issues and optimize service delivery.


1. ass1_dining_xgboost.ipynb -  develops an XGBoost-based machine learning model to predict a customer’s favorite dish based on dining preferences and behavior. It involves data preprocessing, feature engineering, one-hot encoding, and time-aware model training. The system ensures real-world applicability by handling missing data, optimizing hyperparameters, and evaluating model performance using accuracy, log loss, and feature importance analysis.
2. training_and_features.py preprocesses data, generates features, and trains an XGBoost model for dish recommendations, while demo.py is a Streamlit app that uses the model to predict dishes and display discounts based on user inputs.
3. UI 1,2 - The UI and UI 2 images show UI screens of a hotel booking system built with Streamlit. The first screen (UI) displays a booking form where users enter their details, including customer ID, name, check-in/check-out dates, and age. The second screen (UI 2) confirms the booking details and provides personalized discounts based on user data retrieved from MongoDB.
4. review_sentimentanalysisUI.py - The code performs sentiment analysis on hotel customer reviews using Together AI embeddings and Pinecone vector search. It allows users to filter reviews by rating, date, and query, providing AI-generated sentiment summaries in a Streamlit UI.
