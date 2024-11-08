# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for MySQL client and other tools
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev-compat \
    libmariadb-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


COPY wait-for-it.sh /app/wait-for-it.sh

# Make it executable
RUN chmod +x /app/wait-for-it.sh

# Copy the rest of your project code into the container
COPY . /app/

# Expose the port that the app will run on
EXPOSE 8000

WORKDIR /app/my_project
# Wait for MySQL to be available, then start the Django development server
CMD ["sh", "-c", "until nc -z $DB_HOST $DB_PORT; do echo 'Waiting for MySQL...'; sleep 3; done; python /app/my_project/manage.py runserver 0.0.0.0:8000"]

 # Add the my_project directory to PYTHONPATH
ENV PYTHONPATH="/app/my_project:${PYTHONPATH}"
