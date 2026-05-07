FROM python:3.12-slim

LABEL component="verification-mcp"
LABEL version="0.1.0"
LABEL description="MCP wrapper around the verification HTTP service"

# Non-root user for security
RUN groupadd -g 1002 mcp && useradd -m -u 1002 -g 1002 mcp

WORKDIR /app

# Install dependencies
COPY --chown=mcp:mcp requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY --chown=mcp:mcp verification_mcp.py ./

USER mcp

EXPOSE 8080

CMD ["python3", "verification_mcp.py"]
