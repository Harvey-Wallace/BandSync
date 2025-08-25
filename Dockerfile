# Multi-stage build for BandSync - UNIQUE BUILD 1756105149
# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

# Accept build-time arguments for React environment variables
ARG REACT_APP_GOOGLE_MAPS_API_KEY
ARG REACT_APP_API_URL
ARG BUILD_HASH=unique-build-1756105149
ARG CACHE_BUST=1756105149

# Set environment variables for the build
ENV REACT_APP_GOOGLE_MAPS_API_KEY=$REACT_APP_GOOGLE_MAPS_API_KEY
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV CACHE_BUST=$CACHE_BUST

# Debug: Print environment variables during build
RUN echo "🔍 Build-time environment variables (UNIQUE BUILD 1756105149):" && \
    echo "REACT_APP_API_URL: $REACT_APP_API_URL" && \
    echo "REACT_APP_GOOGLE_MAPS_API_KEY: ${REACT_APP_GOOGLE_MAPS_API_KEY:0:20}..." && \
    echo "CACHE_BUST: $CACHE_BUST" && \
    echo "📦 Starting frontend build (UNIQUE BUILD)..."

# Force cache invalidation - UNIQUE BUILD 1756105149
WORKDIR /app/frontend
COPY frontend/package*.json ./
# Complete cache invalidation with unique timestamp
RUN echo "CACHE_BUST: $CACHE_BUST" && npm cache clean --force && rm -rf node_modules && npm install --only=production

COPY frontend/ ./
# UNIQUE BUILD: Complete rebuild with unique cache busting
RUN echo "BUILD_HASH: $BUILD_HASH - UNIQUE BUILD 1756105148" && echo "Unique build triggered at $(date)" && BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') && echo "Unique rebuild at $BUILD_DATE with CACHE_BUST=$CACHE_BUST" && npm run build

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
