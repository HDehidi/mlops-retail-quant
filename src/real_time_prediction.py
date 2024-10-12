#!/usr/bin/env python
# coding: utf-8
     
from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load the scaler and model
scaler_model = joblib.load('models/scaler_model.pkl')
kmeans_model = joblib.load('models/kmeans_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data from the POST request
        data = request.get_json()  # Parses the incoming JSON to a dictionary or list of dictionaries

        if not data:
            raise ValueError("No input data provided or invalid JSON format.")

        # Extract the latest date from the JSON data
        latest_date_str = data.get('latest_date', None)
        if not latest_date_str:
            raise ValueError("Missing 'latest_date' field in input JSON.")
        
        # Parse the latest date
        latest_date = pd.to_datetime(latest_date_str)

        # Extract transactions from the input data
        transactions = data.get('transactions', [])
        if not transactions:
            raise ValueError("Missing 'transactions' data in input JSON.")

        # Convert the transactions JSON into a DataFrame
        df = pd.DataFrame(transactions)

        # Validate the required columns exist
        required_columns = ['customer_id', 'invoice_no', 'invoice_date', 'quantity', 'unit_price']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Convert the 'invoice_date' column to datetime
        df['invoice_date'] = pd.to_datetime(df['invoice_date'])

        # Compute RFMT Features for the provided customer data using the user-defined latest date
        rfmt = compute_rfmt_features(df, latest_date)

        # Standardize the RFMT features using the loaded scaler
        rfmt_scaled = scaler_model.transform(rfmt)

        # Predict the cluster using the trained KMeans model
        cluster = kmeans_model.predict(rfmt_scaled)

        # Return the predicted cluster
        response = {'Predicted Cluster': int(cluster[0])}
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error occurred during prediction: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Function to compute RFMT features from raw transaction data
def compute_rfmt_features(df, latest_date):
    # Create RFMT features for the given customer
    rfmt = df.groupby('customer_id').agg(
        Recency=('invoice_date', lambda x: (latest_date - x.max()).days),
        Frequency=('invoice_no', 'nunique'),
        Monetary=('quantity', lambda x: (x * df.loc[x.index, 'unit_price']).sum()),
        Tenure=('invoice_date', lambda x: (x.max() - x.min()).days)
    )

    rfmt['Interpurchase_Time'] = rfmt['Tenure'] / rfmt['Frequency']

    # Return only the RFMT values for the given customer, resetting the index for standardization
    return rfmt[['Recency', 'Frequency', 'Monetary', 'Interpurchase_Time']].reset_index(drop=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
