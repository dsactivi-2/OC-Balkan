FROM python:3.12-slim-bookworm

WORKDIR /app

# Install Docker CLI (for openclaw tools that use docker exec)
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg openssh-client && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update -qq && \
    apt-get install -y --no-install-recommends docker-ce-cli && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Python dependencies (context is project root)
COPY agents_runtime/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY agents_runtime/ ./agents_runtime/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:8000/health || exit 1

CMD ["uvicorn", "agents_runtime.server:app", "--host", "0.0.0.0", "--port", "8000"]
