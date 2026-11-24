FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY scripts/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/requirements.txt

COPY scripts/ /app/scripts/
COPY sql/ /app/sql/
COPY tests/ /app/tests/
COPY flows/ /app/flows/
COPY powerbi/ /app/powerbi/
COPY config/ /app/config/
COPY docker-compose.yml /app/docker-compose.yml

WORKDIR /app
ENTRYPOINT ["python", "/app/scripts/ingest.py"]
