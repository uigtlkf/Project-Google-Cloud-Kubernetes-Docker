# Use official Python image
FROM python:3.8

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

RUN apt-get update && apt-get install -y bind9-dnsutils curl net-tools


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 80

# Run the application
CMD ["python", "collector_service.py"]
