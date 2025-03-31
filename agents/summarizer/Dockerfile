# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .


# Install Git and any other necessary packages
RUN apt-get update && apt-get install -y git sudo curl

# Install the dependencies
RUN pip install -r requirements.txt

# Configure Git to add the safe directory
RUN git config --global --add safe.directory /app

# Copy the rest of your application code into the container
COPY . .

ENV MIDDLE_SERVER_URL=https://builder247.api.koii.network

# Configure logging and output
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color
ENV FORCE_COLOR=1

# Add this environment variable after other ENV declarations
ENV DATABASE_PATH=/data/database.db

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Set the command to run your application
CMD ["gunicorn", \
    "--log-level=error", \
    "--error-logfile=-", \
    "--capture-output", \
    "--enable-stdio-inheritance", \
    "--logger-class=gunicorn.glogging.Logger", \
    "--timeout", "600", \
    "--graceful-timeout", "600", \
    "--keep-alive", "5", \
    "-w", "1", \
    "-b", "0.0.0.0:8080", \
    "main:app"]
