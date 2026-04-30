FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Increased timeout to handle large downloads
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

COPY . .

EXPOSE 5000

HEALTHCHECK CMD curl --fail http://localhost:5000/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]