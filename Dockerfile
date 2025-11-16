# Multi-stage build for optimized image size and reproducible dependencies
# Stage 1: Build dependencies with uv (ensures exact version locking)
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using locked versions
# --frozen: Use exact versions from uv.lock (fail if lock file is outdated)
# --no-dev: Skip development dependencies
# --no-install-project: Only install dependencies, not the project itself
RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime image (smaller, only what's needed)
FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY models/base_simple_model_v0.pkl ./models/base_simple_model_v0.pkl

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
