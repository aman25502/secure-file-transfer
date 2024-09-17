# Use official Python image as base
FROM python:3.9-slim

# Create the Docker group if it doesn't exist
sudo groupadd docker

# Add your current user to the Docker group
sudo usermod -aG docker $USER

# Apply the new group membership
newgrp docker


# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt into the container at /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 8080 for the web server
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]
