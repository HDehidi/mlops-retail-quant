#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from google.cloud import storage
import pandas_gbq
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import joblib
import logging
import os
import yaml
import datetime


version = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

logging.basicConfig(level=logging.INFO)

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../configs/config.yaml')
with open(CONFIG_PATH, 'r') as config_file:
    config = yaml.safe_load(config_file)

# Paths from configuration

PROJECT_ID = config['gcp']['project_id']
DATASET_ID = config['gcp']['dataset_id']
TABLE_ID = config['gcp']['table_id']
BUCKET_NAME = "kmeans_model_bucket"
#DEST_FILE_NAME = f"models/kmeans/model_{version}.pkl"
DEST_FILE_NAME = "model.pkl"
SOURCE_FILE_NAME = "models/kmeans/model.pkl"


def load_data():
    logging.info("Loading data from BigQuery...")
    client = bigquery.Client(project=PROJECT_ID)
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`"
    df = client.query(query).to_dataframe()
    return df


def clean_data(df):
    logging.info("Cleaning data...")
    df = df.dropna(subset="customer_id")
    df = df[~df.invoice_no.str.contains('C', na=False)]
    df = df[df['quantity'] > 0]
    df = df[df['unit_price'] > 0]
    df = df.drop_duplicates()
    # Remove outliers from 'quantity' and 'unit_price'
    df = remove_outliers(df, 'quantity')
    df = remove_outliers(df, 'unit_price')
    return df


def remove_outliers(df, column):
    logging.info(f"Removing outliers from column: {column}...")
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]


def create_rfmt_features(df):
    logging.info("Creating RFMT features...")
    df['total'] = df['quantity'] * df['unit_price']
    latest_date = df['invoice_date'].max()
    RFM = df.groupby('customer_id').agg(
        Recency=('invoice_date', lambda x: (latest_date - x.max()).days),
        Frequency=('invoice_no', 'nunique'),
        Monetary=('total', 'sum'),
        Tenure=('invoice_date', lambda x: (x.max() - x.min()).days)
    )
    
    RFM['Interpurchase_Time'] = RFM['Tenure'] / RFM['Frequency']
    RFMT = RFM[['Recency', 'Frequency', 'Monetary', 'Interpurchase_Time']]
    return RFMT

def scale_rfmt_data(RFMT):
    logging.info("Scaling RFMT data...")
    scaler = StandardScaler()
    scaler = scaler.fit(RFMT)
    joblib.dump(scaler, 'models/kmeans/scaler.pkl')
    logging.info("Scaler saved successfully.")
    
    rfmt_scaled = scaler.transform(RFMT)
    return rfmt_scaled

def train_model(RFMT, rfmt_scaled):
    logging.info("Training clustering model...")
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(rfmt_scaled)
    RFMT['Cluster'] = kmeans.predict(rfmt_scaled)

    score = silhouette_score(rfmt_scaled, kmeans.labels_, metric='euclidean')
    logging.info(f"Silhouette Score: {score}")
    joblib.dump(kmeans, 'models/kmeans/model.pkl')

    logging.info("Model saved successfully.")


def upload_to_gcs(bucket_name, source_file_name, dest_file_name):
    logging.info("Uploading model to GCS...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(dest_file_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {bucket_name}.")
    
    
def store_to_bg(RFMT):
    logging.info("Storing RFMT data to BigQuery Table...")
    credentials = service_account.Credentials.from_service_account_file('configs/mlops-retail-quant-466be1b9ef88.json')
    dataset_table = f'{DATASET_ID}.rfmt_table'

    # Store RFMT in BigQuery
    pandas_gbq.to_gbq(RFMT, dataset_table, project_id=PROJECT_ID, if_exists='replace', credentials=credentials)

if __name__ == "__main__":
    df = load_data()
    df_cleaned = clean_data(df)
    rfmt = create_rfmt_features(df_cleaned)
    rfmt_scaled = scale_rfmt_data(rfmt)
    train_model(rfmt, rfmt_scaled)
    upload_to_gcs(BUCKET_NAME, SOURCE_FILE_NAME, DEST_FILE_NAME)
    store_to_bg(rfmt)







