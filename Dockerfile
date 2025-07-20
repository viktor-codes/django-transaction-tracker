FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create static directory
RUN mkdir -p /app/static

# Expose port
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]