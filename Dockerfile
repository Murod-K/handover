FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Data directory for SQLite
RUN mkdir -p /data

ENV DB_PATH=/data/handover_v3.db

CMD ["python", "main.py"]
