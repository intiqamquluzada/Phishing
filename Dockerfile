# Dockerfile

# Use the official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the FastAPI app code
COPY . /app/

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run FastAPI server with Uvicorn
CMD ["uvicorn", "phish/main:app", "--host", "0.0.0.0", "--port", "8000"]
