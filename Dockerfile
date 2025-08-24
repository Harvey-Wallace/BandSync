# Multi-stage build for BandSync
# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

# Accept build-time arguments for React environment variables
ARG REACT_APP_GOOGLE_MAPS_API_KEY
ARG REACT_APP_API_URL
ARG BUILD_HASH=default

# Set environment variables for the build
ENV REACT_APP_GOOGLE_MAPS_API_KEY=$REACT_APP_GOOGLE_MAPS_API_KEY
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Debug: Print environment variables during build
RUN echo "🔍 Build-time environment variables:" && \
    echo "REACT_APP_API_URL: $REACT_APP_API_URL" && \
    echo "REACT_APP_GOOGLE_MAPS_API_KEY: ${REACT_APP_GOOGLE_MAPS_API_KEY:0:20}..." && \
    echo "📦 Starting frontend build (force rebuild)..."

# Force cache invalidation with a comment - Build 2025-08-24-16:40
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
# Force rebuild with timestamp to bust Docker cache
RUN echo "BUILD_HASH: $BUILD_HASH" && echo "Forcing frontend rebuild at $(date)" && BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') && echo "Build triggered at $BUILD_DATE" && npm run build

# Stage 2: Setup backend
FROM python:3.11-slim AS backend

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy migration scripts and startup script
COPY railway_rsvp_visibility_migration.py ./
COPY add_rsvp_visibility_setting.py ./
COPY railway_startup.sh ./

# Make startup script executable
RUN chmod +x railway_startup.sh

# Clean the static directory before copying the new build
RUN rm -rf /app/static
# Copy built frontend - ensure clean copy
COPY --from=frontend-builder /app/frontend/build/ ./static/

# Create uploads directory
RUN mkdir -p uploads/attachments

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application with migration via startup script
CMD ["./railway_startup.sh"]
