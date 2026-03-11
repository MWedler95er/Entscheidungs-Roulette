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
COPY game.py db_.py .

# Standard-Befehl: Script ausführen
CMD ["python", "game.py"]
