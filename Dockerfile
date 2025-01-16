# Use a Python base image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && pip install poetry \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the pyproject.toml and poetry.lock files (if present)
COPY pyproject.toml poetry.lock* /app/

# Install the Python dependencies defined by Poetry
RUN poetry install --no-root

# Copy the entire project into the container
COPY . /app/

# Expose the port that your service will run on
EXPOSE 8000

# Set the default command to run your service
CMD ["poetry", "run", "python", "src/app.py"]
