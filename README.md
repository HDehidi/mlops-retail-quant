
---

# Clustering Project with KMeans on GCP

The project performs customer clustering using KMeans, deployed on GCP. It involves building data pipeline to ingest data from cloud SQL into BigQuery, clustering notebook, Cloud Build for CI/CD and serving real-time predictions via an API hosted on Cloud Run.

---
## Project Overview

The primary goal of this project is to implement a customer clustering model using KMeans on transaction data. 

#### Data Pipeline with Cloud Composer (Airflow):

1. **Data Extraction**: Data is extractedd from a cloud SQL Postgres database.
2. **Data Loading**: The data is stored in GCS.
3. **Data Transforming**: The data is transferred from GCS to BigQuery for further processing and analysis.

#### Model Training, Experiment Tracking, & Model Registry 

1. **Model Training**: Clustering models (KMeans) are trained, and the resulting models are stored in a model registry.
2. **Experiment Tracking**: The training process and experiments are tracked for continuous improvement and model versioning.

#### CI/CD Pipeline with Cloud Build

The pipeline is configured to trigger on push requests to the `main` branch of the GitHub repository.

### Pipeline Workflow

1. **Trigger**: Any push to the `main` branch automatically initiates the build process.

2. **Docker Image Creation**:
   - Cloud Build reads the `cloudbuild.yaml` file.
   - The Docker image for the Flask API is built using the `Dockerfile`.
   - The built image is pushed to **Google Container Registry**.

3. **Deployment to Cloud Run**:
   - The newly built Docker image is deployed to **Google Cloud Run**, which hosts the Flask API for real-time predictions.

4. **Model Registration**:
   - The model is automatically registered in **Vertex AI Model Registry**

---
## File Structure

```
.
├── configs/
│   ├── notebooks/
│   │   ├── clustering.ipynb       # KMeans clustering
│   │   ├── DBSCAN_clustering.ipynb # DBSCAN clustering
│   │   ├── arima_forecasting.ipynb # ARIMA forecasting
│   │   └── prophet_forecasting.ipynb # Prophet forecasting
├── scripts/
│   ├── run_prediction.sh          # Script to run real-time prediction
│   └── run_training.sh            # Script to run the model training pipeline
├── src/
│   ├── real_time_prediction.py    # Script handling real-time predictions
│   └── train_pipeline.py          # Script handling the model training pipeline
├── Dockerfile                     # Docker setup for the project
├── cloudbuild.yaml                # GCP Cloud Build configuration
├── requirements.txt               # Project dependencies
└── README.md                      # Project documentation
```
---
## Requirements

The following Python dependencies are required and are listed in the `requirements.txt` file:

```
Flask
joblib
pandas
scikit-learn
google-cloud-bigquery
google-auth
pandas-gbq
google-api-python-client
```
---
## Setup Instructions

### Prerequisites

- GCP account with the following IAM roles:
  - BigQuery Admin
  - Cloud Build Editor
  - Cloud Build Service Account
  - Cloud Run Admin
  - Cloud SQL Admin
  - Composer Administrator
  - Service Account User
  - Storage Admin
  - Vertex AI Administrator
- Cloud SQl Postgres database for data storage.

---
### Local Development

1. Clone the repository:

   ```bash
   git clone mlops-retail-quant
   cd mlops-retail-quant
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Build and run the Docker image locally:

   ```bash
   docker build -t retail-prediction-api .
   docker run -p 5000:5000 retail-prediction-api
   ```

4. Test real-time predictions by running the following script:

   ```bash
   ./scripts/run_prediction.sh
   ```

5. Send a POST request to test the API:

   ```bash
   curl -X POST http://127.0.0.1:5000/predict \
   -H "Content-Type: application/json" \
   -d '{
       "latest_date": "2011-12-11",
       "transactions": [
           {
               "customer_id": "12347",
               "invoice_no": "536365",
               "invoice_date": "2011-12-08",
               "quantity": 6,
               "unit_price": 2.55
           },
           {
               "customer_id": "12347",
               "invoice_no": "536366",
               "invoice_date": "2011-12-09",
               "quantity": 3,
               "unit_price": 3.39
           },
           {
               "customer_id": "12347",
               "invoice_no": "536367",
               "invoice_date": "2011-12-10",
               "quantity": 9,
               "unit_price": 4.99
           }
       ]
   }'
   ```

6. Expected API Response:

   ```json
   {
       "Predicted Cluster": 4
   }
   ```
---
### Deploying to GCP

1. Commit changes to GitHub repository.
2. Cloud Build will automatically trigger:
   - Build a new Docker image.
   - Store it in GCP Container Registry.
   - Deploy the application to Cloud Run.
   - Load the trained model into Vertex AI Model Registry.

---
## Usage

- **Training**: Run the following script to trigger model training:

  ```bash
  ./scripts/run_training.sh
  ```

- **Prediction**: Use the API to send transaction data and retrieve the predicted customer cluster.

---
## ToDO

- Terraform file, to reproduce the infrastructure.
- Complete ARIMA & Prophet experiments
- Complete DBSCAN experiment