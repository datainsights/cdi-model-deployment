## Dockerfile

# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy code and model directory
COPY scripts/model_api.py ./scripts/model_api.py
COPY models/ ./models/
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Uvicorn
EXPOSE 8000

# Run the API with Uvicorn
CMD ["uvicorn", "scripts.model_api:app", "--host", "0.0.0.0", "--port", "8000"]