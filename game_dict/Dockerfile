FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Systempakete, die psycopg2 benötigt
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY game_logik.py db_.py api.py ./
COPY templates ./templates
COPY static ./static

# Standard-Befehl: Script ausführen
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
