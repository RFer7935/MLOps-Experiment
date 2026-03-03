# ============================================================
# Dockerfile — Tobacco Risk Classification
# Image: Python 3.10 slim + dependencies
# Runs: Streamlit dashboard on port 8501
# ============================================================

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY Monitoring_dan_Logging/app.py ./app.py
COPY Workflow-CI/MLProject/tobacco_preprocessed ./tobacco_preprocessed

# Copy trained model (produced by the training job and downloaded before docker build)
COPY Workflow-CI/MLProject/outputs/rf_model.pkl ./rf_model.pkl

# Expose Streamlit port and Prometheus metrics port
EXPOSE 8501
EXPOSE 8000

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
