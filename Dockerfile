# syntax=docker/dockerfile:1

FROM node:20-slim AS scribe-build

WORKDIR /build/scribe

COPY scribe/package*.json ./
RUN npm ci

COPY scribe/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        gnupg \
        tini \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Gardener dependencies
WORKDIR /app/gardener
COPY gardener/pyproject.toml gardener/uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy Gardener application code
COPY gardener/ ./

# Copy Scribe runtime assets
WORKDIR /app/scribe
COPY --from=scribe-build /build/scribe/dist ./dist
COPY --from=scribe-build /build/scribe/node_modules ./node_modules
COPY scribe/package*.json ./

# Entrypoint
WORKDIR /app
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 3000 8000

ENTRYPOINT ["tini", "--"]
CMD ["/app/docker/entrypoint.sh"]
