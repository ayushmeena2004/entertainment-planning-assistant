# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port (change if needed)
EXPOSE 5000

# Run your app
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]