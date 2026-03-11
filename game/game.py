# pylint: skip-file
import dataclasses
import random
import db_


@dataclasses.dataclass
class Player:
    name: str
    health: int = 3
    krit_chance: float = 0.2


class DecisionRoulette:
    def __init__(self):
        self.stapel = []
        self.reload_counter = 0
        self.players: list[Player] = []
        self.player_counter: dict[str, Player] = {}
        

    def push(self, item):
        self.stapel.append(item)


    def pop(self):
        if not self.stapel:
            raise IndexError("Stapel ist leer")
        return self.stapel.pop()


    def peek(self):
        if not self.stapel:
            raise IndexError("Stapel ist leer")
        return self.stapel[-1]


    def load_bullet(self, players=None):
        self.stapel = [random.randint(0, 1) for _ in range(10)]
        self.reload_counter += 1

        if players:
            for p in players:
                # Krit-Chance increase by reload +0.1
                p.krit_chance = min(p.krit_chance + 0.1, 1.0)
            print(
                f"\nNachladen #{self.reload_counter}: "
                f"Kritische Trefferchance aller Spieler wurde um 0.1 erhöht."
            )


    def shoot(self, player):
        bullet = self.pop()

        if bullet == 1:
            if random.random() < player.krit_chance:
                player.health -= 2
                return "Kritischer Treffer! BANG!"
            player.health -= 1
            return "BANG!"
        return "Klick! Glück gehabt."

    
    def _wait_for_enter(self) -> None:
        while True:
            eingabe = input("\nDrücke Enter, um zum Menü zurückzukehren: ")
            if eingabe == "":
                break
            print("Bitte nur Enter drücken, ohne Text.")


    def game_start(self):
        if not self.player_counter:
            raise ValueError("Nicht genügend 'Spieler'!")

        round_num = 0
        # initial Alive-Liste
        initial_player_count = len(self.player_counter)
        play = True

        while play:
            alive_players = [p for p in self.player_counter.values() if p.health > 0]
            if not alive_players:
                print("\nNiemand hat überlebt. 😵")
                play = False
                break

            if len(alive_players) == 1:
                winner = alive_players[0]
                print("\n" + "=" * 50)
                print(f"🎉 GEWINNER: {winner.name}!")
                print("=" * 50)
                try:
                    db_.insert_into_db_(winner.name, self.reload_counter, range(initial_player_count), winner.health)
                    print("Speichern erfolgreich.")

                except OSError as e:
                    print(f"Fehler beim Schreiben in 'db': {e}")
                play = False
                break

            round_num += 1
            print(f"\n--- Runde {round_num} ---")

            # Magazine empty -> reload
            if not self.stapel:
                print("\nMagazin leer, wird neu geladen...")
                self.load_bullet(players=alive_players)

            # every alive player shoot
            for player in alive_players:
                if player.health <= 0:
                    continue  

                if not self.stapel:
                    print("\nMagazin leer, wird neu geladen...")
                    self.load_bullet(players=alive_players)

                result = self.shoot(player)
                print(f"{player.name} schießt: {result} (Health: {player.health})")

                if player.health <= 0:
                    print("\n" + "=" * 50)
                    print(f"{player.name} ist ausgeschieden!")
                    print("=" * 50)


    def menu(self):

        while True:
            print("\n==== Entscheidungs-Roulette Menü ====")
            print("1) Entscheidung hinzufügen")
            print("2) Entscheidungen anzeigen")
            print("3) Spiel starten")
            print("4) Gewinner anzeigen")
            print("5) Beenden")
            choice = input("Bitte wähle (1-5): ").strip()

            if choice == "1":
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
                    # neue Entscheidung in die Liste aufnehmen
                    self.players.append(Player(name=name, health=5))

            elif choice == "2":
                if not self.players:
                    print("\nNoch keine Entscheidungen vorhanden.")
                else:
                    print("\nAktuelle Entscheidungen:")
                    for idx, p in enumerate(self.players, start=1):
                        print(f"{idx}) {p.name} (Health: {p.health})")

            elif choice == "3":
                if len(self.players) < 2:
                    print("Mindestens 2 Entscheidungen werden benötigt, um zu starten.")
                    continue

                self.load_bullet(players=self.players)
                print("\n🔫 Russisches Entscheidungs-Roulette startet!\n")

                self.player_counter = {
                    f"PL{idx}": p for idx, p in enumerate(self.players, start=1)
                }
                print(self.player_counter)
                self.game_start()

                # after game clear list
                self.players.clear()

                # wait until player presses 'Enter' before the menue reappears
                while True:
                    eingabe = input("\nDrücke die Enter, um zum Menü zurückzukehren: ")
                    if eingabe == "":
                        break
                    print("Bitte nur Enter drücken, ohne Text.")
            
            elif choice == "4":
                # last winner's print from db 
                db_.list_winners()

            elif choice == "5":
                print("Programm wird beendet.")
                break
            else:
                print("Ungültige Eingabe, bitte 1-5 wählen.")


if __name__ == "__main__":
    print("Warte auf Datenbank und initialisiere Tabellen ...")
    db_.init_db()
    print("Datenbank bereit.")

    print("Trage deine Entscheidungen ein, die das Roulette entscheiden soll.")
    game = DecisionRoulette()
    game.menu()