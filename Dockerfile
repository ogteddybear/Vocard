# Stage 1: Install Python dependencies
FROM python:3.12-slim-bookworm AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Run Vocard
FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .
# Vocard requires settings.json at startup; secrets are injected by Fly, not baked into this file.
COPY ["settings Example.json", "settings.json"]
CMD ["python", "-u", "main.py"]
