# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8080 \
    ENV=dev \
    project=ihp-rpp \
    LOG_LEVEL=INFO
# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

ENV PYTHONLOGGING='{"version": 1, "handlers": {"cloud": {"class": "google.cloud.logging.handlers.CloudLoggingHandler"}}, "loggers": {"": {"handlers": ["cloud"], "level": "INFO"}}}'

# Expose port 8000 for the application
EXPOSE 8000

# Define environment variable
ENV FLASK_APP=app.py

# Run the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]