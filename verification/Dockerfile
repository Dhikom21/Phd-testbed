FROM python:3.12-slim

LABEL component="verification"
LABEL version="0.1.0"

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates && \
    curl -LO "https://dl.k8s.io/release/v1.30.0/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && mv kubectl /usr/local/bin/ && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py ./

EXPOSE 5000
CMD ["python3", "verification_service.py"]
