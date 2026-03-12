"""Database models and helper functions for the decision roulette game."""

import os

from sqlalchemy import Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """Base declarative class for all ORM models."""


class WinnerGame(Base):  # pylint: disable=too-few-public-methods
    """ORM model representing a single finished game (winner statistics)."""

    __tablename__ = "winner"
    id: Mapped[int] = mapped_column(primary_key=True)
    round_w: Mapped[str] = mapped_column(String(50))
    play_rounds: Mapped[int] = mapped_column(Integer)
    player_number: Mapped[int] = mapped_column(Integer)
    winner_health: Mapped[int] = mapped_column(Integer)


class Decisions(Base):  # pylint: disable=too-few-public-methods
    """ORM model representing a single stored decision entry.

    This class maps individual decision names to the `decisions` database table for persistence.
    """

    __tablename__ = "decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


# Defaults for docker-compose
DB_USER = os.getenv("DB_USER", "game_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "game_password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "game_db")

URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(URL, echo=False)


def init_db() -> None:
    """Initialise the database by creating all tables if they do not exist."""
    Base.metadata.create_all(engine)
    print("Tabellen wurden (falls nicht vorhanden) erstellt!")


def insert_winner_into_db_(
    alive_player: str,
    reload_counter: int,
    player_number: list,
    health_remain: int,
) -> None:
    """Insert a finished game (winner information) into the database."""
    with Session(engine) as session:
        new_entry = WinnerGame(
            round_w=alive_player,
            play_rounds=reload_counter,
            player_number=len(player_number),
            winner_health=health_remain,
        )
        session.add(new_entry)
        session.commit()


def insert_decision_into_db_(decision_name: str) -> None:
    """Insert a single decision entry into the database.

    This helper function persists the provided decision
    name as a row in the decisions table.

    Args:
        decision_name: The textual name of the decision to store.
    """
    with Session(engine) as session:
        new_entry = Decisions(
            name=decision_name,
        )
        session.add(new_entry)
        session.commit()


def list_winners() -> None:
    """Read all winners from the DB and print them to the console."""
    with Session(engine) as session:
        results = session.query(WinnerGame).order_by(WinnerGame.id).all()

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
