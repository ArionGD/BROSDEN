# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Install system dependencies for Tesseract OCR and Psycopg2
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libpq-dev \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code
COPY . /app/

# Create staticfiles and media directories
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
# We use a dummy secret key if not provided during build
RUN python manage.py collectstatic --noinput --settings=config.settings

# Expose the port
EXPOSE 8080

# Use gunicorn to run the application
# We'll run migrations at startup (optional but convenient for first-time setup)
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
