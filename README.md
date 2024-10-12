
### Testing the Real-Time Prediction API
**Send a POST Request**
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

**Response**

   ```json
   {
       "Predicted Cluster": 4
   }
   ```
   
### Docker:

**Build the Image**

```bash
docker build -t rfmt-prediction-api .
```

**Tag the Image**

```bash
docker tag rfmt-prediction-api gcr.io/mlops-retail-quant/rfmt-prediction-api
```

**Tag the Image**

```bash
docker push gcr.io/mlops-retail-quant/rfmt-prediction-api
```

**Deploy the Image**

```bash
gcloud run deploy rfmt-prediction-api \
--image gcr.io/mlops-retail-quant/rfmt-prediction-api \
--platform managed \
--region me-central1 \
--allow-unauthenticated
```

**Test the cloud run (Docker Container)**

```bash
curl -X POST https://rfmt-prediction-api-456146517905.me-central1.run.app/predict \
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