FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY scripts/python scripts/python
COPY models models
EXPOSE 8000
CMD ["uvicorn", "--app-dir", "scripts/python", "05-model-api:app", "--host", "0.0.0.0", "--port", "8000"]
