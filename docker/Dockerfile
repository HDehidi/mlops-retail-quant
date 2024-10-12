FROM python:3.10.15

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENV FLASK_APP=real_time_prediction.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Expose the port the app runs on
EXPOSE 8080

# Run the Flask server
CMD ["flask", "run", "--port=8080"]
