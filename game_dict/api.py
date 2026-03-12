# pylint: disable=missing-module-docstring
import typing

import db_
import fastapi
import fastapi.responses
import fastapi.staticfiles
import fastapi.templating
import game_logik
import pydantic
import sqlalchemy.orm

# Game & db
game_instanz = game_logik.DecisionRoulette()
templates = fastapi.templating.Jinja2Templates(directory="templates")
db_.init_db()


class PlayerOut(pydantic.BaseModel):
    """Output schema representing a single player in API responses.

    This model describes the public fields of a
    player that are sent back to clients.
    """

    name: str
    health: int


class PlayerIn(pydantic.BaseModel):
    """Input schema representing data required to create a new player.

    This model captures the user-provided name for
    a decision that will be added as a player.
    """

    name: str


class GameState(pydantic.BaseModel):
    """Response model representing the outcome of a game round.

    This model exposes the number of reloads performed and
    the final winning player, if any.
    """

    reload_counter: int
    winner: PlayerOut | None


# API Start
app = fastapi.FastAPI(title="Entscheidungs-Roulette API")
app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")


@app.get("/", response_class=fastapi.responses.HTMLResponse)
def index(request: fastapi.Request):
    """simpel HTML-UI for the Decision-Roulette."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "players": game_instanz.players,
        },
    )


@app.get("/test")
def test():
    """Return a simple health-check response for the API.

    This endpoint can be used to verify that the service is running and reachable.

    Returns:
        dict: A small JSON object indicating test status.
    """
    return {"test": "ok"}


@app.get("/players", response_model=typing.List[PlayerOut])
def list_player():
    """Return the list of all currently added players.

    This endpoint exposes the in-memory collection of
    players so that clients can display the current decisions.
    """
    return [
        PlayerOut(
            name=p.name,
            health=p.health,
        )
        for p in game_instanz.players
    ]


@app.post("/add_players", response_model=PlayerOut, status_code=201)
def add_player(player_in: PlayerIn):
    """Create and register a new player from the provided decision name.

    This endpoint stores the decision in the database and adds a
    corresponding player to the current in-memory game state.

    Args:
        player_in: Input payload containing the name of the decision to add as a player.

    Returns:
        PlayerOut: The created player, as it will appear in subsequent API responses.

    Raises:
        fastapi.HTTPException: If the provided name is empty or only whitespace.
    """
    name = player_in.name.strip()

    if not name:
        raise fastapi.HTTPException(
            status_code=400, detail="Name darf nicht leer sein."
        )

    # Entscheidung in der DB speichern
    db_.insert_decision_into_db_(decision_name=name)

    # Player im aktuellen Spielzustand anlegen
    player = game_logik.Player(name=name, health=5)
    game_instanz.players.append(player)

    return PlayerOut(
        name=player.name,
        health=player.health,
    )


@app.post("/game/start", response_model=GameState)
def start_game():
    """Run a full game round and return the resulting winner.

    This endpoint consumes the currently added players,
    executes the roulette logic, and responds with the winner and reload count.

    Returns:
        GameState: The final game state containing the reload counter and the winning player,
        or None if no one survived.

    Raises:
        fastapi.HTTPException: If fewer than two players have been added before starting the game.
    """
    # 1. Sicherstellen, dass genug Spieler da sind
    if len(game_instanz.players) < 2:
        raise fastapi.HTTPException(
            status_code=400,
            detail="Mindestens 2 Entscheidungen werden benötigt, um zu starten.",
        )

    # 2. Magazin laden
    game_instanz.load_bullet(players=game_instanz.players)

    # 3. player_counter der Instanz füllen (so wie in _handle_start_game)
    game_instanz.player_counter = {
        f"PL{idx}": p for idx, p in enumerate(game_instanz.players, start=1)
    }

    # 4. Spiel starten – liefert Gewinner oder None zurück
    winner = game_instanz.game_start()

    # 5. players-Liste nach Spielende leeren
    game_instanz.players.clear()

    # 6. Response aufbauen: nur Gewinner + Reload-Counter
    if winner is None:
        winner_out: PlayerOut | None = None
    else:
        winner_out = PlayerOut(name=winner.name, health=winner.health)

    return GameState(
        reload_counter=game_instanz.reload_counter,
        winner=winner_out,
    )


@app.get("/winners")
def list_winners():
    """
    Return all stored game winners from the database as JSON records.

    This endpoint exposes the historical winner statistics
    so clients can display past game outcomes.
    """
    results_json = []
    with sqlalchemy.orm.Session(db_.engine) as session:
        results = session.query(db_.WinnerGame).order_by(db_.WinnerGame.id).all()
        for row in results:
            results_json.append(
                {
                    "id": row.id,
                    "winner": row.round_w,
                    "reloads": row.play_rounds,
                    "player_count": row.player_number,
                    "winner_health": row.winner_health,
                }
            )
    return results_json
