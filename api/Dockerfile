# API Service Dockerfile - Optimized for China
# Build context: project root
FROM python:3.11-slim

WORKDIR /app

# Use Aliyun mirror for apt
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Use Tsinghua mirror for pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Copy requirements from project root
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from api directory
COPY api/ .

# Copy scripts directory from project root
COPY scripts/ ./scripts/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
