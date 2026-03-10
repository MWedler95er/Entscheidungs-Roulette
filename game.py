# pylint: skip-file
import dataclasses
import random
import db_


PLAYERS_NUMBER = [] 
HEALTH_REMAIN = 0
RELOAD_COUNTER = 0
ALIVE_PLAYER = ""



@dataclasses.dataclass
class Player:
    name: str
    health: int = 3
    krit_chance: float = 0.2


class RussischRollette:
    def __init__(self):
        self.stapel = []
        self.reload_counter = 0

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
        global RELOAD_COUNTER
        self.stapel = [random.randint(0, 1) for _ in range(10)]
        self.reload_counter += 1
        RELOAD_COUNTER = self.reload_counter

        if players:
            for p in players:
                # Krit-Chance pro Nachladen um 0.1 erhöhen, maximal 1.0
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

    
    def game_start(self):
        global ALIVE_PLAYER
        global HEALTH_REMAIN
        global PLAYERS_NUMBER
        if not self.player_counter:
            raise ValueError("Mindestens ein Spieler ist erforderlich!")

        round_num = 0

        # Solange mehr als ein Spieler lebt, geht das Spiel weiter
        while True:
            alive_players = [p for p in self.player_counter.values() if p.health > 0]
            if len(alive_players) <= 1:
                # Gewinner ermitteln
                if alive_players:
                    print("\n" + "=" * 50)
                    print(f"🎉 GEWINNER: {alive_players[0].name}!")
                    ALIVE_PLAYER = str(alive_players[0].name)
                    HEALTH_REMAIN = alive_players[0].health
                    #print(ALIVE_PLAYER,HEALTH_REMAIN,RELOAD_COUNTER)
                    print("=" * 50)

                    # Gewinner in eine Textdatei schreiben (z. B. für Docker-Übungen)
                    try:
                        db_.insert_into_db_(ALIVE_PLAYER,RELOAD_COUNTER,PLAYERS_NUMBER,HEALTH_REMAIN)
                    except OSError as e:
                        print(f"Fehler beim Schreiben in 'db': {e}")
                else:
                    print("\nNiemand hat überlebt. 😵")
                    try:
                        with open("winner.txt", "a", encoding="utf-8") as f:
                            f.write("Niemand hat überlebt.\n")
                    except OSError as e:
                        print(f"Fehler beim Schreiben in 'winner.txt': {e}")
                return

            round_num += 1
            print(f"\n--- Runde {round_num} ---")

            # Wenn Magazin leer ist, neu laden
            if not self.stapel:
                print("\nMagazin leer wird neu geladen...")
                self.load_bullet(players=alive_players)

            for player in alive_players:
                # Falls Magazin im Verlauf der Runde leer wird, neu laden
                if not self.stapel:
                    print("\nMagazin leer wird neu geladen...")
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
            print("5) Beenden")
            choice = input("Bitte wähle (1-4): ").strip()

            if choice == "1":
                print(
                    "\nEntscheidungen eingeben und mit Enter bestätigen."
                    "\nDu kannst mehrere hintereinander eingeben."
                    "\nUm fertig zu werden, einfach nur Enter ohne Text drücken.\n"
                )
                while True:
                    name = input("Entscheidung: ").strip()
                    if not name:
                        # Leere Eingabe -> zurück ins Hauptmenü
                        print("Eingabe beendet, zurück zum Menü.")
                        break
                    PLAYERS_NUMBER.append(Player(name=name, health=5))

            elif choice == "2":
                if not PLAYERS_NUMBER:
                    print("\nNoch keine Entscheidungen vorhanden.")
                else:
                    print("\nAktuelle Entscheidungen:")
                    for idx, p in enumerate(PLAYERS_NUMBER, start=1):
                        print(f"{idx}) {p.name} (Health: {p.health})")

            elif choice == "3":
                if len(PLAYERS_NUMBER) < 2:
                    print("Mindestens 2 Entscheidungen werden benötigt, um zu starten.")
                    continue

                # Magazin laden und erste Krit-Erhöhung anwenden
                self.load_bullet(players=PLAYERS_NUMBER)
                print("\n🔫 Russisches Entscheidungs-Roulette startet!\n")

                # Spieler/Entscheidungen in kwargs-Form übergeben
                self.player_counter = {
                    f"PL{idx}": p for idx, p in enumerate(PLAYERS_NUMBER, start=1)
                }
                print(self.player_counter)
                self.game_start()

                # Nach dem Spiel alles zurücksetzen
                PLAYERS_NUMBER.clear()

                # Warten, bis der Spieler Enter drückt, bevor das Menü wieder erscheint
                while True:
                    eingabe = input("\nDrücke die Enter, um zum Menü zurückzukehren: ")
                    if eingabe == "":
                        break
                    print("Bitte nur Enter drücken, ohne Text.")
            
            elif choice == "4":
                break
                #
                #
                #
                #

            elif choice == "5":
                print("Programm wird beendet.")
                break
            else:
                print("Ungültige Eingabe, bitte 1-4 wählen.")


if __name__ == "__main__":
    print("Trage deine Entscheidungen ein, die das Roulette entscheiden soll.")
    game = RussischRollette()
    game.menu()
