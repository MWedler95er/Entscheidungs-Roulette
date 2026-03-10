from sqlalchemy import String, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
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
URL = "postgresql://mwedl95er:Plyxpl.yx95@localhost:5432/game_db"
engine = create_engine(URL)
Base.metadata.create_all(engine)

print("Tabellen wurde (falls nicht vorhanden) erstellt!")

def insert_into_db_(ALIVE_PLAYER, RELOAD_COUNTER, PLAYERS_NUMBER, HEALTH_REMAIN):
    with Session(engine) as session:
        new_entry = Winner_Game(
            round_w=ALIVE_PLAYER,                     
            play_rounds=RELOAD_COUNTER,               # Anzahl Nachladungen
            player_number=len(PLAYERS_NUMBER),     # Anzahl Entscheidungen/Spieler
            winner_health=HEALTH_REMAIN            # Platzhalter, bis du den Gewinner übergibst
        )

        session.add(new_entry)
        session.commit()

#todo 
# gewinner der runde in db (+ spielrer anzahl, playtime, end health)
# neuen menue punkt -> db auslesen 
# db kill wen spiel beendet / für übung auch mal einstellen das db bleibt

