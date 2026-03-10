from sqlalchemy import String, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import os
import time
import typing


# 2. Die Basis-Klasse für unsere Tabellen
class Base(DeclarativeBase):
    pass

class Winner_Game(Base):
    __tablename__ = "winner"
    id: Mapped[int]= mapped_column(primary_key=True)
    round_w: Mapped[str]= mapped_column(String(50))
    play_rounds: Mapped[int] = mapped_column(Integer)
    player_number: Mapped[int] = mapped_column(Integer)
    winner_health: Mapped[int] = mapped_column(Integer)

# 1. Verbindung (nutze deine funktionierende URL)
# DB-Config aus Umgebungsvariablen (mit Defaults für docker-compose)
DB_USER = os.getenv("DB_USER", "game_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "game_password")
DB_HOST = os.getenv("DB_HOST", "db")  # Hostname des DB-Containers
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "game_db")

URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(URL, echo=False)

def init_db(max_retries: int = 10, delay_seconds: int = 2) -> None:
    """Wartet auf die DB und legt Tabellen an."""
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(engine)
            print("Tabellen wurden (falls nicht vorhanden) erstellt!")
            return
        except Exception as exc:  # breit fangen, damit auch Verbindungsfehler erwischt werden
            print(
                f"DB-Verbindung fehlgeschlagen (Versuch {attempt}/{max_retries}): {exc}"
            )
            if attempt == max_retries:
                print("Gebe auf, DB ist nicht erreichbar.")
                raise
            time.sleep(delay_seconds)

def insert_into_db_(ALIVE_PLAYER, RELOAD_COUNTER, PLAYERS_NUMBER, HEALTH_REMAIN):
    with Session(engine) as session:
        new_entry = Winner_Game(
            round_w=ALIVE_PLAYER,                     
            play_rounds=RELOAD_COUNTER,             # Anzahl Nachladungen
            player_number=len(PLAYERS_NUMBER),     # Anzahl Entscheidungen/Spieler
            winner_health=HEALTH_REMAIN            # Platzhalter, bis du den Gewinner übergibst
        )

        session.add(new_entry)
        session.commit()

def list_winners() -> None:
    """Liest alle Gewinner aus der DB und gibt sie auf der Konsole aus."""
    with Session(engine) as session:
        results = session.query(Winner_Game).order_by(Winner_Game.id).all()

        if not results:
            print("\nNoch keine gespeicherten Spiele in der Datenbank.")
            return

        print("\n=== Gespeicherte Spiele ===")
        for row in results:
            print(
                f"ID: {row.id} | Gewinner: {row.round_w} | "
                f"Reloads: {row.play_rounds} | Spieler: {row.player_number} | "
                f"Rest-Health: {row.winner_health}"
            )