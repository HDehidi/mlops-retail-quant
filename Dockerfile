FROM python:3.10.15

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/real_time_prediction.py /app/
COPY models/kmeans/model.pkl /app/model.pkl
COPY models/kmeans/scaler.pkl /app/scaler.pkl

ENV FLASK_APP=real_time_prediction.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

CMD exec flask run --host=$FLASK_RUN_HOST --port=$PORT
