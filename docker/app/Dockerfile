# docker/app/Dockerfile
FROM python:3.13-slim-trixie
EXPOSE 8080

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# create non-privileged user and fix permissions later
RUN useradd --create-home --no-log-init appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn

# Copy project
COPY sportsclub/ .

# ensure application files belong to the non-root user
RUN chown -R appuser:appuser /app

# Collect static files (needed when serving through a reverse proxy)
RUN python manage.py collectstatic --noinput

# switch to unprivileged user before running
USER appuser

# Run uvicorn
CMD ["uvicorn", "sportsclub.asgi:application", "--host", "0.0.0.0", "--port", "8080"]
