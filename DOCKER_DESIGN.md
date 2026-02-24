# Docker Architecture Design for NavigationApp

This document outlines the Docker configuration for the NavigationApp, including the backend (FastAPI), frontend (Vite/React), and orchestration (Docker Compose).

## 1. Backend Dockerfile (`backend/Dockerfile`)

The backend uses a Python 3.11 slim image. It installs dependencies and runs the FastAPI application using Uvicorn.

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY src/ ./src/

# Create directory for skyfield data
RUN mkdir -p /app/skyfield_data

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 2. Frontend Dockerfile (`frontend/Dockerfile`)

The frontend uses a multi-stage build to keep the final image small.

```dockerfile
# Stage 1: Build
FROM node:20-slim AS build-stage

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:stable-alpine AS production-stage

# Copy build output from build-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 3. Nginx Configuration (`frontend/nginx.conf`)

This configuration serves the static frontend files and proxies API requests to the backend service.

```nginx
server {
    listen 80;
    server_name localhost;

    # Frontend static files
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to the backend service
    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

## 4. Docker Compose (`docker-compose.yml`)

Orchestrates the backend and frontend services.

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: navigation-backend
    volumes:
      - skyfield_data:/app/skyfield_data
    environment:
      - ENV=production
    networks:
      - navigation-network
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: navigation-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - navigation-network
    restart: always

networks:
  navigation-network:
    driver: bridge

volumes:
  skyfield_data:
```

## Summary of File Paths

| Component | File Path |
|-----------|-----------|
| Backend Dockerfile | `backend/Dockerfile` |
| Frontend Dockerfile | `frontend/Dockerfile` |
| Nginx Config | `frontend/nginx.conf` |
| Docker Compose | `docker-compose.yml` |
