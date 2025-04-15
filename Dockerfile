# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run the Flask app with Gunicorn
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
