FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Expose both ports (8000 and 8080)
EXPOSE 8000
EXPOSE 8080

# Use uvicorn to run the app and bind to all interfaces
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]