# ============================================================
# Stage 1: Build Rust native module (structural_core_rs)
# ============================================================
FROM rust:1.82-slim-bookworm AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev \
    libblas-dev liblapack-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY structural_core_rs/ /build/structural_core_rs/

RUN pip install maturin --quiet \
    && cd structural_core_rs \
    && PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 maturin build --release --out /build/wheels \
    && ls -lh /build/wheels/

# ============================================================
# Stage 2: Runtime image
# ============================================================
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libblas3 liblapack3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Rust wheel from builder stage
COPY --from=builder /build/wheels/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Copy application code
COPY . .

# Create runtime directories
RUN mkdir -p logs output_api

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
