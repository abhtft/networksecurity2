FROM python:3.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories for the application
RUN mkdir -p \
    prediction_output \
    final_model \
    templates \
    Artifacts \
    saved_models \
    Artifacts/data_ingestion/feature_store \
    Artifacts/data_ingestion/ingested \
    Artifacts/data_validation/validated \
    Artifacts/data_validation/invalid \
    Artifacts/data_validation/drift_report \
    Artifacts/data_transformation/transformed \
    Artifacts/data_transformation/transformed_object \
    Artifacts/model_trainer/trained_model && \
    chmod -R 777 /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8000

# Start the application with proper logging
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]