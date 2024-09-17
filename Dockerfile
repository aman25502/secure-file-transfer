# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables to avoid buffering
ENV PYTHONUNBUFFERED=1

# Create and set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose port 8080 to the outside world
EXPOSE 8080

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask application
#CMD ["python", "run", "--host=0.0.0.0", "--port=8080"]
CMD ["python", "app.py"]
