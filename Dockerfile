# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools
RUN pip install --no-cache-dir build

# Copy project metadata and source
COPY pyproject.toml README.md ./
COPY src/ src/

# Build a wheel
RUN python -m build --wheel --outdir /dist

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="MRIF"
LABEL org.opencontainers.image.description="Meta-Recursive Intelligence Framework"
LABEL org.opencontainers.image.version="0.1.0"

WORKDIR /app

# Install the wheel (no dev deps)
COPY --from=builder /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Create non-root user
RUN useradd -m -u 1000 mrif
USER mrif

# Persist DB outside the container
VOLUME ["/data"]
ENV MRIF_DB_URL="sqlite:////data/mrif.db"

ENTRYPOINT ["mrif"]
CMD ["status"]
