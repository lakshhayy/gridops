# Use slim for smaller footprint and better security
FROM python:3.11-slim

# Prevent Python from writing pyc files to disc (useless in containers)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (required for numpy/pandas extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security (standard enterprise requirement)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port
EXPOSE 8000

# Start the server using Uvicorn (ASGI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]