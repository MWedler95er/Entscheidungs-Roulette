# Entscheidungs-Roulette (Docker Edition)

Ein kleines Konsolen-Spiel, bei dem du mehrere **Entscheidungen** eingibst und das Programm per „russischem Roulette“ eine davon als Gewinner auswählt.  
Jede Entscheidung hat Lebenspunkte und eine kritische Trefferchance, die mit jedem Nachladen steigt.  
Die Ergebnisse (Gewinner + Metadaten) werden in einer **PostgreSQL-Datenbank** gespeichert.

---

## 1. Was das Spiel macht

Beim Start (im Container) siehst du ein Menü:

1. **Entscheidung hinzufügen**  
   - Du gibst beliebig viele Entscheidungen ein (eine pro Zeile).  
   - Leere Eingabe (nur Enter) beendet die Eingabe.

2. **Entscheidungen anzeigen**  
   - Listet alle aktuell eingetragenen Entscheidungen mit ihren Lebenspunkten.

3. **Spiel starten**  
   - Es werden mindestens 2 Entscheidungen benötigt.  
   - Es wird ein Magazin mit 0/1 gefüllt (zufällige Kugeln).  
   - Reihum „schießen“ die Entscheidungen:
     - `1` im Magazin = Treffer (`BANG!`)  
     - mit Wahrscheinlichkeit `krit_chance` = kritischer Treffer (`-2 HP`), sonst `-1 HP`  
   - Ist das Magazin leer, wird **neu geladen**:
     - dabei erhöht sich die kritische Trefferchance aller noch lebenden Entscheidungen um `+0.1` (max. `1.0`).
   - Das Spiel läuft, bis nur noch eine Entscheidung > 0 HP hat:
     - Diese wird als **Gewinner** ausgegeben.
     - Der Gewinner wird in die Datenbank geschrieben.

4. **Gewinner anzeigen**  
   - Liest alle gespeicherten Spiele aus der DB und zeigt sie in der Konsole an.

5. **Beenden**  
   - Beendet das Programm im Container.

---

## 2. Datenbank-Aufbau und Einträge

Es wird eine PostgreSQL-Datenbank im Container betrieben.  
Die Verbindung wird über Umgebungsvariablen gesetzt (siehe `docker-compose.yml`):

- `DB_USER` = `game_user`
- `DB_PASSWORD` = `game_password`
- `DB_HOST` = `db` (Name des DB-Services im Compose)
- `DB_PORT` = `5432`
- `DB_NAME` = `game_db`

Beim Start des Spiels (in `game.py`) wird `db_.init_db()` aufgerufen:

- Verbindet sich zur DB (mit Retry-Logik).
- Legt bei Bedarf die Tabelle `winner` an.

### Tabelle `winner`

Definiert in `db_.py`:

```python
class Winner_Game(Base):
    __tablename__ = "winner"
    id: Mapped[int] = mapped_column(primary_key=True)
    round_w: Mapped[str] = mapped_column(String(50))
    play_rounds: Mapped[int] = mapped_column(Integer)
    player_number: Mapped[int] = mapped_column(Integer)
    winner_health: Mapped[int] = mapped_column(Integer)
