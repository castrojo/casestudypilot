# syntax=docker/dockerfile:1.4

# =============================================================================
# CaseStudyPilot - Containerized CNCF Case Study Generator
# Using Chainguard Python for minimal, secure container images
# =============================================================================

# =============================================================================
# Stage 1: Builder - Install dependencies
# =============================================================================
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

# Create virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY casestudypilot/ casestudypilot/
COPY templates/ templates/
COPY .github/ .github/
COPY pyproject.toml .

# Install the application
RUN pip install --no-cache-dir --no-deps -e .

# =============================================================================
# Stage 2: Runtime - Minimal production image
# =============================================================================
FROM cgr.dev/chainguard/python:latest AS runtime

WORKDIR /app

# Copy virtual environment and code from builder
COPY --from=builder /app/venv /app/venv
COPY --from=builder /app/casestudypilot /app/casestudypilot
COPY --from=builder /app/templates /app/templates
COPY --from=builder /app/.github /app/.github
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Environment variables
ENV PATH="/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create output directories
USER root
RUN mkdir -p /output/case-studies /output/data && \
    chown -R nonroot:nonroot /output
USER nonroot

# OCI labels for GHCR metadata
LABEL org.opencontainers.image.title="CaseStudyPilot" \
      org.opencontainers.image.description="Skill-driven LLM automation framework for CNCF case studies" \
      org.opencontainers.image.version="2.2.0" \
      org.opencontainers.image.authors="Jorge Castro" \
      org.opencontainers.image.url="https://github.com/castrojo/casestudypilot" \
      org.opencontainers.image.source="https://github.com/castrojo/casestudypilot" \
      org.opencontainers.image.vendor="CNCF" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.base.name="cgr.dev/chainguard/python:latest"

# Set entrypoint
ENTRYPOINT ["python", "-m", "casestudypilot"]
CMD ["--help"]
