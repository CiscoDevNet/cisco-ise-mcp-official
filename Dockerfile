# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved
#
# Build:
#   docker build -t ise-mcp-server .
#
# Run:
#   docker run -p 5000:5000 --env-file .env ise-mcp-server

FROM python:3.12-slim
ARG DEV=false
ARG DEBUG=false

### BES Requirements
# 1) Dump security-relevant apt settings (expect empty or "false")
RUN apt-config dump | grep -iE \
'AllowUnauthenticated|AllowInsecure|AllowDowngrade|AllowWeak|Untrusted' \
|| echo "OK: no insecure apt overrides in apt-config dump"
# 2) Scan apt config fragments
RUN grep -rniE \
'AllowUnauthenticated|AllowInsecure|AllowDowngrade|trusted=yes|\[trusted' \
/etc/apt/apt.conf /etc/apt/apt.conf.d/ 2>/dev/null \
|| echo "OK: no insecure directives in apt.conf.d"
# 3) Scan sources (trusted=yes bypasses signature verification)
RUN grep -rniE 'trusted=yes|\[trusted' \
/etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null \
|| echo "OK: no trusted=yes in sources"
# 4) Show key material is present (Ubuntu/Debian base)
RUN ls -la /etc/apt/trusted.gpg.d/ /usr/share/keyrings/ 2>/dev/null; \
apt-key list 2>/dev/null || true

# Set working directory
WORKDIR /app


# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy shared libs
COPY shared_libs/ ./shared_libs/

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies based on mode
RUN if [ "$DEV" = "true" ]; then \
        uv sync --frozen --group dev; \
    else \
        uv sync --frozen --no-dev; \
    fi

# Copy application source after dependencies to leverage Docker cache
COPY . .

# Set environment variables (can be overridden at runtime)
ENV HOST=0.0.0.0
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Prevent `uv run` from doing an implicit sync (and any network access) at
# container start time. Dependencies are already installed into /app/.venv
# during the build step above, so the runtime must not try to fetch packages
# from PyPI. Required for air-gapped / offline installs (image loaded from
# tarball on a host without internet).
ENV UV_NO_SYNC=1
ENV UV_OFFLINE=1
ENV UV_FROZEN=1

# Expose ports (5000 for app, 5678 for debugpy in debug mode)
EXPOSE 5000 5678

# Conditional CMD based on DEBUG arg
ENV DEBUG=${DEBUG}

# `--no-sync` is set explicitly as well, in case UV_NO_SYNC is overridden.
CMD if [ "$DEBUG" = "true" ]; then \
        exec uv run --no-sync python -m debugpy --listen 0.0.0.0:5678 --wait-for-client server.py; \
    else \
        exec uv run --no-sync server.py; \
    fi
