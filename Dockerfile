FROM python:3.12-slim-bookworm

# Install uv (from official binary), nodejs, npm, and git
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm via NodeSource 
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Confirm npm and node versions (optional debugging info)
RUN node -v && npm -v

# Create app user for security
RUN groupadd -r mcpo && useradd -r -g mcpo mcpo

# Copy your mcpo source code (assuming in src/mcpo)
COPY . /app
WORKDIR /app

# Create virtual environment explicitly in known location
ENV VIRTUAL_ENV=/app/.venv
RUN uv venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install mcpo (assuming pyproject.toml is properly configured)
RUN uv pip install . && rm -rf ~/.cache

# Verify mcpo installed correctly
RUN which mcpo

# Create config directory with proper permissions
RUN mkdir -p /app/config && \
    chown -R mcpo:mcpo /app && \
    chmod 755 /app/config && \
    chmod 664 /app/config.json 2>/dev/null || true

# Create entrypoint script to handle permissions
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo '# Fix ownership of mounted config files/directories' >> /app/entrypoint.sh && \
    echo 'if [ -f /app/config.json ]; then' >> /app/entrypoint.sh && \
    echo '    chown mcpo:mcpo /app/config.json 2>/dev/null || true' >> /app/entrypoint.sh && \
    echo '    chmod 664 /app/config.json 2>/dev/null || true' >> /app/entrypoint.sh && \
    echo 'fi' >> /app/entrypoint.sh && \
    echo 'if [ -d /app/config ]; then' >> /app/entrypoint.sh && \
    echo '    chown -R mcpo:mcpo /app/config 2>/dev/null || true' >> /app/entrypoint.sh && \
    echo '    find /app/config -type f -name "*.json" -exec chmod 664 {} \; 2>/dev/null || true' >> /app/entrypoint.sh && \
    echo 'fi' >> /app/entrypoint.sh && \
    echo '# Switch to mcpo user and execute command' >> /app/entrypoint.sh && \
    echo 'if [ "$(id -u)" = "0" ]; then' >> /app/entrypoint.sh && \
    echo '    exec su-exec mcpo "$@"' >> /app/entrypoint.sh && \
    echo 'else' >> /app/entrypoint.sh && \
    echo '    exec "$@"' >> /app/entrypoint.sh && \
    echo 'fi' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Install su-exec for secure user switching
RUN apt-get update && apt-get install -y --no-install-recommends su-exec && rm -rf /var/lib/apt/lists/*

# Keep as root for entrypoint to fix permissions, then su-exec to mcpo
# USER mcpo  # Commented out - entrypoint will switch to mcpo

# Expose port (optional but common default)
EXPOSE 8000

# Entrypoint set for easy container invocation
ENTRYPOINT ["/app/entrypoint.sh", "mcpo"]

# Default help CMD (can override at runtime)
CMD ["--help"]