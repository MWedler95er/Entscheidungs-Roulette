# pylint: disable=missing-module-docstring
import dataclasses
import random

import db_


@dataclasses.dataclass
class Player:
    """Represent a single player participating in the decision roulette game.

    This model tracks the player's name, remaining health,
    and chance for critical hits.
    """

    name: str
    health: int = 3
    krit_chance: float = 0.2


class DecisionRoulette:
    """Encapsulate the core game flow for the decision roulette application.

    This class coordinates player management, magazine handling, shooting rounds,
    and winner persistence across both CLI and API usage.
    """

    def __init__(self):
        self.stapel = []
        self.reload_counter = 0
        self.players: list[Player] = []
        self.player_counter: dict[str, Player] = {}

    def push(self, item):
        """Add a new item to the top of the internal bullet stack.

        This method is used to grow the magazine or stack
        by appending elements in LIFO order.
        """
        self.stapel.append(item)

    def pop(self):
        """Remove and return the top item from the internal bullet stack.

        This method retrieves the most recently added
        element and fails if the stack is empty.
        """
        if not self.stapel:
            raise IndexError("Stapel ist leer")
        return self.stapel.pop()

    def peek(self):
        """Return the top item from the internal
        bullet stack without removing it.

        This method allows inspection of the next element that would
        be popped and fails if the stack is empty.
        """
        if not self.stapel:
            raise IndexError("Stapel ist leer")
        return self.stapel[-1]

    def load_bullet(self, players=None):
        """Reload the magazine with a new sequence of bullets.

        This method increases the reload counter and optionally
        boosts the critical hit chance of all players.
        """
        self.stapel = [random.randint(0, 1) for _ in range(10)]
        self.reload_counter += 1

        if players:
            for p in players:
                # Crit chance increases by 0.1 on each reload
                p.krit_chance = min(p.krit_chance + 0.1, 1.0)
            print(
                f"\nNachladen #{self.reload_counter}: "
                f"Kritische Trefferchance aller Spieler wurde um 0.1 erhöht."
            )

    def shoot(self, player):
        """Simulate a single shot at the given player and update their health.

        This method determines whether the shot is a miss, a normal hit,
        or a critical hit and returns a descriptive message.

        Args:
            player: The player who is being shot at and whose health may be reduced.

        Returns:
            str: A message describing the outcome of the shot.
        """
        bullet = self.pop()

        if bullet == 1:
            if random.random() < player.krit_chance:
                player.health -= 2
                return "Kritischer Treffer! BANG!"
            player.health -= 1
            return "BANG!"
        return "Klick! Glück gehabt."

    def _wait_for_enter(self) -> None:
        """Pause execution until the user confirms by pressing Enter.

        This helper method loops until only a bare Enter key
        press is received, ignoring any other input.
        """
        while True:
            eingabe = input("\nDrücke Enter, um zum Menü zurückzukehren: ")
            if eingabe == "":
                break
            print("Bitte nur Enter drücken, ohne Text.")

    def _get_alive_players(self) -> list[Player]:
        """Return the subset of players who are still alive in the current round.

        A player is considered alive if their health is greater than zero
        and they remain eligible to continue in the game.
        """
        return [p for p in self.player_counter.values() if p.health > 0]

    def _handle_no_survivors(self) -> None:
        """Handle the situation where all players have been eliminated.

        This method prints a summary message indicating that no one survived the game.
        """
        print("\nNiemand hat überlebt. 😵")

    def _handle_winner(self, winner: Player, initial_player_count: int) -> None:
        """Handle the winner of the game by reporting and persisting the result.

        This method announces the winning player to the console and records the
        game statistics for that winner in the database.
        """
        print("\n" + "=" * 50)
        print(f"🎉 GEWINNER: {winner.name}!")
        print("=" * 50)
        try:
            db_.insert_winner_into_db_(
                winner.name,
                self.reload_counter,
                range(initial_player_count),
                winner.health,
            )
            print("Speichern erfolgreich.")
        except OSError as e:
            print(f"Fehler beim Schreiben in 'db': {e}")

    def _ensure_magazine_loaded(self, alive_players: list[Player]) -> None:
        """Ensure the magazine is loaded before the next shot in the round.

        If the internal bullet stack is empty, this helper method reloads it and
        adjusts player critical hit chances based on the new reload.
        """
        if not self.stapel:
            print("\nMagazin leer, wird neu geladen...")
            self.load_bullet(players=alive_players)

    def _player_shoots(self, player: Player, alive_players: list[Player]) -> None:
        """Let a single player shoot once and handle elimination output."""
        if player.health <= 0:
            return

        self._ensure_magazine_loaded(alive_players)
        result = self.shoot(player)
        print(f"{player.name} schießt: {result} (Health: {player.health})")

        if player.health <= 0:
            print("\n" + "=" * 50)
            print(f"{player.name} ist ausgeschieden!")
            print("=" * 50)

    def game_start(self) -> Player | None:
        """Main game loop that runs the decision roulette.

        Runs the roulette rounds until either no
        players survive or a single winner remains.
        Returns the winning Player instance, or None if no one survived.
        """
        if not self.player_counter:
            raise ValueError("Nicht genügend 'Spieler'!")

        round_num = 0
        # initial alive player count
        initial_player_count = len(self.player_counter)
        play = True

        while play:
            alive_players = self._get_alive_players()

            if not alive_players:
                self._handle_no_survivors()
                play = False
                break

            if len(alive_players) == 1:
                self._handle_winner(alive_players[0], initial_player_count)
                play = False
                break

            round_num += 1
            print(f"\n--- Runde {round_num} ---")

            # Magazine empty -> reload
            self._ensure_magazine_loaded(alive_players)

            # every alive player shoots
            for player in alive_players:
                self._player_shoots(player, alive_players)

        return alive_players[0]

    def _print_menu(self) -> None:
        """Show the main menu"""
        print("\n==== Entscheidungs-Roulette Menü ====")
        print("1) Entscheidung hinzufügen")
        print("2) Entscheidungen anzeigen")
        print("3) Spiel starten")
        print("4) Gewinner anzeigen")
        print("5) Beenden")

    def _handle_add_decisions(self) -> None:
        """insert new decisions (Players)."""
        print(
            "\nEntscheidungen eingeben und mit Enter bestätigen."
            "\nDu kannst mehrere hintereinander eingeben."
            "\nUm fertig zu werden, einfach nur Enter ohne Text drücken.\n"
        )
        while True:
            name = input("Entscheidung: ").strip()
            if not name:
                print("Eingabe beendet, zurück zum Menü.")
                break
            self.players.append(Player(name=name, health=5))

    def _handle_list_decisions(self) -> None:
        """List of all added decisions"""
        if not self.players:
            print("\nNoch keine Entscheidungen vorhanden.")
            return

        print("\nAktuelle Entscheidungen:")
        for idx, p in enumerate(self.players, start=1):
            print(f"{idx}) {p.name} (Health: {p.health})")

    def _handle_start_game(self) -> None:
        """Start the game if there are enough decisions."""
        if len(self.players) < 2:
            print("Mindestens 2 Entscheidungen werden benötigt, um zu starten.")
            return

        self.load_bullet(players=self.players)
        print("\n🔫 Russisches Entscheidungs-Roulette startet!\n")

        self.player_counter = {
            f"PL{idx}": p for idx, p in enumerate(self.players, start=1)
        }
        print(self.player_counter)

        # start he game
        self.game_start()

        # clear the decision list after the game
        self.players.clear()

        # wait until Enter is pressed
        self._wait_for_enter()

    def _handle_show_winners(self) -> None:
        """Show the winners stored in the database."""
        db_.list_winners()

    def menu(self) -> None:
        """Main menu of the application."""
        while True:
            self._print_menu()
            choice = input("Bitte wähle (1-5): ").strip()

            if choice == "1":
                self._handle_add_decisions()
            elif choice == "2":
                self._handle_list_decisions()
            elif choice == "3":
                self._handle_start_game()
            elif choice == "4":
                self._handle_show_winners()
            elif choice == "5":
                print("Programm wird beendet.")
                break
            else:
                print("Ungültige Eingabe, bitte 1-5 wählen.")
