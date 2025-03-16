from pymongo import MongoClient
import pandas as pd
import xgboost as xgb

client = MongoClient("mongodb+srv://gatikavinnivarma:uuQoNnIJECtLqyrq@cluster0.y0un9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client["hotel_guests"]

collection = db["dining_info"]

df_from_mongo = pd.DataFrame(list(collection.find()))

df = df_from_mongo.copy()

df['check_in_date'] = pd.to_datetime(df['check_in_date'])
df['check_out_date'] = pd.to_datetime(df['check_out_date'])
df['order_time'] = pd.to_datetime(df['order_time'])

df['check_in_day'] = df['check_in_date'].dt.dayofweek  # Monday=0, Sunday=6
df['check_out_day'] = df['check_out_date'].dt.dayofweek
df['check_in_month'] = df['check_in_date'].dt.month
df['check_out_month'] = df['check_out_date'].dt.month
df['stay_duration'] = (df['check_out_date'] - df['check_in_date']).dt.days

df[['booked_through_points','price_for_1']].groupby('booked_through_points').mean()

features_df = df[df['order_time']<'2024-01-01']

# I can direct features
train_df = df[(df['order_time']>='2024-01-01')&(df['order_time']<='2024-10-01')]

test_df = df[(df['order_time']>'2024-10-01')] # - pseudo prediction dataset

customer_features = features_df.groupby('customer_id').agg(
    total_orders_per_customer=('transaction_id', 'count'),
    avg_spend_per_customer=('price_for_1', 'mean'),
    total_qty_per_customer=('Qty', 'sum'),
    avg_stay_per_customer=('stay_duration', 'mean')
).reset_index()

customer_features.to_excel('customer_features.xlsx',index=False)



# Get most frequent cuisine & dish per customer

customer_dish = features_df.groupby('customer_id').agg(
    most_frequent_dish=('dish', lambda x: x.mode()[0])
).reset_index()

customer_dish.to_excel('customer_dish.xlsx',index=False)

# 🌟 Cuisine-Level Aggregations
cuisine_features = features_df.groupby('Preferred Cusine').agg(
    avg_price_per_cuisine=('price_for_1', 'mean'),
    total_orders_per_cuisine=('transaction_id', 'count')
).reset_index()

cuisine_features.to_excel('cuisine_features.xlsx',index=False)

# Most popular dish per cuisine
cuisine_dish = features_df.groupby('Preferred Cusine').agg(
    cuisine_popular_dish=('dish', lambda x: x.mode()[0])
).reset_index()

cuisine_dish.to_excel('cuisine_dish.xlsx',index=False)



train_df = train_df.merge(customer_features, on='customer_id', how='left')
train_df = train_df.merge(cuisine_features, on='Preferred Cusine', how='left')
train_df = train_df.merge(customer_dish, on='customer_id', how='left')
train_df = train_df.merge(cuisine_dish, on='Preferred Cusine', how='left')


train_df.drop(['_id','transaction_id','customer_id','price_for_1',
               'Qty','order_time','check_in_date','check_out_date'],axis=1,inplace=True)

from sklearn.preprocessing import OneHotEncoder
import pandas as pd

# Select categorical columns for one-hot encoding
categorical_cols = ['Preferred Cusine', 'most_frequent_dish','cuisine_popular_dish']

# Initialize OneHotEncoder
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')


# Apply transformation
encoded_array = encoder.fit_transform(train_df[categorical_cols])

print(encoded_array)

# Convert to DataFrame
encoded_df = pd.DataFrame(encoded_array, columns=encoder.get_feature_names_out(categorical_cols))

import joblib

# Store the encoder
joblib.dump(encoder, 'encoder.pkl')

# Load the encoder when needed
loaded_encoder = joblib.load('encoder.pkl')


# Concatenate with the original DataFrame
train_df = pd.concat([train_df.drop(columns=categorical_cols), encoded_df], axis=1)

train_df.columns

test_df = test_df.merge(customer_features, on='customer_id', how='left')
test_df = test_df.merge(cuisine_features, on='Preferred Cusine', how='left')
test_df = test_df.merge(customer_dish, on='customer_id', how='left')
test_df = test_df.merge(cuisine_dish, on='Preferred Cusine', how='left')

test_df.drop(['_id','transaction_id','customer_id','price_for_1',
               'Qty','order_time','check_in_date','check_out_date'],axis=1,inplace=True)


encoded_test = encoder.transform(test_df[categorical_cols])

# Convert to DataFrame
encoded_test_df = pd.DataFrame(encoded_test, columns=encoder.get_feature_names_out(categorical_cols))

# Concatenate with test_df
test_df = pd.concat([test_df.drop(columns=categorical_cols), encoded_test_df], axis=1)

train_df

train_df = train_df.dropna(subset=['dish'])

# Encode the target column 'dish' using LabelEncoder
from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()
train_df['dish'] = label_encoder.fit_transform(train_df['dish'])

joblib.dump(label_encoder, 'label_encoder.pkl')

# Split into features (X) and target (y)
X_train = train_df.drop(columns=['dish'])  # Features
y_train = train_df['dish']

test_df = test_df.dropna(subset=['dish'])

# Encode 'dish' using the SAME LabelEncoder from training
test_df['dish'] = label_encoder.transform(test_df['dish']) 

from sklearn.metrics import accuracy_score, log_loss

X_test = test_df.drop(columns=['dish'])  # Features
y_test = test_df['dish']

xgb_model = xgb.XGBClassifier(
    objective="multi:softmax",  # Multi-class classification
    eval_metric="mlogloss",  # Multi-class log loss
    learning_rate=0.1,
    max_depth=1,
    n_estimators=100,
    subsample=1,
    colsample_bytree=1,
    random_state=42
)

# Train the model
xgb_model.fit(X_train, y_train)

joblib.dump(xgb_model, 'xgb_model_dining.pkl')
pd.DataFrame(X_train.columns).to_excel('features.xlsx')