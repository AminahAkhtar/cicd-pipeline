
FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/
