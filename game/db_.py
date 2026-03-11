from sqlalchemy import String, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import os
import time
import typing


class Base(DeclarativeBase):
    pass

class Winner_Game(Base):
    __tablename__ = "winner"
    id: Mapped[int]= mapped_column(primary_key=True)
    round_w: Mapped[str]= mapped_column(String(50))
    play_rounds: Mapped[int] = mapped_column(Integer)
    player_number: Mapped[int] = mapped_column(Integer)
    winner_health: Mapped[int] = mapped_column(Integer)

# Defaults for docker-compose
DB_USER = os.getenv("DB_USER", "game_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "game_password")
DB_HOST = os.getenv("DB_HOST", "db")  
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "game_db")

URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(URL, echo=False)

def init_db() -> None:
    # Create tables -> fail fast if the DB is not reachable.
    Base.metadata.create_all(engine)
    print("Tabellen wurden (falls nicht vorhanden) erstellt!")


def insert_into_db_(ALIVE_PLAYER, RELOAD_COUNTER, PLAYERS_NUMBER, HEALTH_REMAIN)-> None:
    with Session(engine) as session:
        new_entry = Winner_Game(
            round_w=ALIVE_PLAYER,
            play_rounds=RELOAD_COUNTER,
            player_number=len(PLAYERS_NUMBER),
            winner_health=HEALTH_REMAIN,
        )
        session.add(new_entry)
        session.commit()

def list_winners() -> None:
    """Read all winners from the DB and print them to the console."""
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