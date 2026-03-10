FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app


# Requirements kopieren und installieren (falls du eine requirements.txt hast)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

# Dein Script kopieren
COPY game.py .

# Standard-Befehl: Script ausführen
CMD ["python", "game.py"]
