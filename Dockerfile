# metaSolid in plain Docker: uv builds the venv, the runtime stage copies only the venv.
#
#   VERSION=$(python3 -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
#   docker build --build-arg VERSION=$VERSION -t metasolid:$VERSION .

ARG PYTHON_VERSION=3.13
ARG TYPST_VERSION=0.15.1

# --- builder -----------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS builder
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY metasolid/ ./metasolid/
RUN uv sync --frozen --no-dev --no-editable

FROM ghcr.io/typst/typst:${TYPST_VERSION} AS typst

# --- runtime -----------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim
ARG VERSION
LABEL org.opencontainers.image.title="metasolid" \
      org.opencontainers.image.version="${VERSION}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends pandoc \
    && rm -rf /var/lib/apt/lists/*
COPY --from=typst /bin/typst /usr/local/bin/typst

RUN useradd --system --create-home --uid 10001 metasolid
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
USER metasolid

# matplotlib writes a cache; under `docker run --user` there is no home to hold it.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib

ENTRYPOINT ["python", "-m", "metasolid"]
CMD ["--help"]
