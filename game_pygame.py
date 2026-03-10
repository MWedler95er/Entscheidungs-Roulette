#pylint: skip-file
import pygame
import sys
import dataclasses
import random
import typing


# ---- deine Logik (leicht angepasst, ohne input/print im Menü) ----

@dataclasses.dataclass
class Player:
    name: str
    health: int = 3
    krit_chance: float = 0.2


class RussischRollette:
    def __init__(self):
        self.stapel = []
        self.reload_count = 0

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
        self.reload_count += 1

        if players:
            for p in players:
                p.krit_chance = min(p.krit_chance + 0.1, 1.0)

    def shoot(self, player):
        bullet = self.pop()
        if bullet == 1:
            if random.random() < player.krit_chance:
                player.health -= 2
                return "Kritischer Treffer! BANG!"
            player.health -= 1
            return "BANG!"
        return "Klick! Glück gehabt."

    def game_step(self, players):
        """
        Führt eine komplette Runde durch und gibt:
        - log_lines: Liste von Texten, die angezeigt werden sollen
        - finished: True, wenn das Spiel vorbei ist
        - winner_name: Name des Gewinners oder None
        """
        log_lines = []
        alive_players = [p for p in players if p.health > 0]
        if len(alive_players) <= 1:
            if alive_players:
                winner = alive_players[0].name
                log_lines.append(f"GEWINNER: {winner}!")
                return log_lines, True, winner
            log_lines.append("Niemand hat überlebt.")
            return log_lines, True, None

        if not self.stapel:
            log_lines.append("Magazin leer – wird neu geladen...")
            self.load_bullet(players=alive_players)

        for player in alive_players:
            if not self.stapel:
                log_lines.append("Magazin leer – wird neu geladen...")
                self.load_bullet(players=alive_players)

            result = self.shoot(player)
            log_lines.append(
                f"{player.name} schießt: {result} (Health: {player.health})"
            )
            if player.health <= 0:
                log_lines.append(f"{player.name} ist ausgeschieden!")

        return log_lines, False, None


# ---- Pygame GUI ----

WIDTH, HEIGHT = 800, 600
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (230, 230, 230)
BUTTON_COLOR = (70, 70, 150)
BUTTON_HOVER = (100, 100, 200)
INPUT_BG = (50, 50, 50)


class Button:
    def __init__(self, rect, text, font, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback

    def draw(self, surface, mouse_pos):
        color = BUTTON_HOVER if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()


class TextInput:
    def __init__(self, rect, font):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text = ""
        self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=5)
        border_color = (200, 200, 200) if self.active else (120, 120, 120)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=5)
        txt_surf = self.font.render(self.text, True, TEXT_COLOR)
        surface.blit(txt_surf, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                entered = self.text
                self.text = ""
                return entered
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 20 and event.unicode.isprintable():
                    self.text += event.unicode
        return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Entscheidungs-Roulette (Pygame)")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont(None, 24)
    font_medium = pygame.font.SysFont(None, 32)
    font_large = pygame.font.SysFont(None, 40)

    input_name = TextInput((20, 20, 300, 32), font_small)

    players: typing.List[Player] = []
    game = RussischRollette()
    log_lines: typing.List[str] = []
    auto_mode = False
    auto_interval_ms = 800
    last_auto_step = 0
    game_running = False
    winner_name = None

    def add_player():
        nonlocal players
        entered = input_name.text.strip()
        if entered:
            players.append(Player(name=entered, health=5))
            input_name.text = ""

    def start_game_manual():
        """Spiel starten, aber nur manuell per Button/Runde weiter."""
        nonlocal game_running, log_lines, winner_name, auto_mode
        if len(players) < 2:
            log_lines.append("Mindestens 2 Entscheidungen nötig, um zu starten.")
            return
        for p in players:
            p.health = 5
            p.krit_chance = 0.2
        game.stapel = []
        game.reload_count = 0
        log_lines.append("Spiel startet (manuell)...")
        game_running = True
        auto_mode = False
        winner_name = None

    def start_game_auto():
        """Spiel starten, das automatisch durchläuft."""
        nonlocal game_running, log_lines, winner_name, auto_mode, last_auto_step
        if len(players) < 2:
            log_lines.append("Mindestens 2 Entscheidungen nötig, um zu starten.")
            return
        for p in players:
            p.health = 5
            p.krit_chance = 0.2
        game.stapel = []
        game.reload_count = 0
        log_lines.append("Spiel startet (automatisch)...")
        game_running = True
        auto_mode = True
        winner_name = None
        last_auto_step = pygame.time.get_ticks()

    def step_game():
        """Eine Spielrunde ausführen (für manuellen Modus oder Auto-Modus)."""
        nonlocal game_running, log_lines, winner_name, auto_mode
        if not game_running:
            return
        step_logs, finished, winner = game.game_step(players)
        log_lines.extend(step_logs)
        if finished:
            game_running = False
            auto_mode = False
            winner_name = winner

    def reset_game():
        nonlocal players, log_lines, game_running, winner_name, auto_mode
        players = []
        log_lines = []
        game_running = False
        winner_name = None
        auto_mode = False
        game.stapel = []
        game.reload_count = 0

    btn_add = Button((340, 20, 150, 32), "Hinzufügen", font_small, add_player)
    btn_start = Button((20, 70, 150, 32), "Spiel starten", font_small, start_game_manual)
    btn_step = Button((180, 70, 150, 32), "Nächste Runde", font_small, step_game)
    btn_auto = Button((340, 70, 150, 32), "Auto-Spiel", font_small, start_game_auto)
    btn_reset = Button((500, 70, 150, 32), "Reset", font_small, reset_game)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            input_result = input_name.handle_event(event)
            if input_result is not None:
                if input_result.strip():
                    players.append(Player(name=input_result.strip(), health=5))
            btn_add.handle_event(event)
            btn_start.handle_event(event)
            btn_step.handle_event(event)
            btn_auto.handle_event(event)
            btn_reset.handle_event(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # AUTO-MODUS: alle X ms automatisch eine Runde
        if game_running and auto_mode:
            now = pygame.time.get_ticks()
            if now - last_auto_step >= auto_interval_ms:
                step_game()
                last_auto_step = now

        screen.fill(BG_COLOR)

        title_surf = font_large.render("Entscheidungs-Roulette", True, TEXT_COLOR)
        screen.blit(title_surf, (20, 120))

        input_name.draw(screen)
        btn_add.draw(screen, mouse_pos)
        btn_start.draw(screen, mouse_pos)
        btn_step.draw(screen, mouse_pos)
        btn_auto.draw(screen, mouse_pos)
        btn_reset.draw(screen, mouse_pos)

        y = 170
        screen.blit(font_medium.render("Entscheidungen:", True, TEXT_COLOR), (20, y))
        y += 30
        for p in players:
            txt = f"{p.name} (Health: {p.health}, Krit: {p.krit_chance:.1f})"
            screen.blit(font_small.render(txt, True, TEXT_COLOR), (40, y))
            y += 24

        log_area_rect = pygame.Rect(420, 170, 360, 380)
        pygame.draw.rect(screen, (40, 40, 40), log_area_rect)
        pygame.draw.rect(screen, (100, 100, 100), log_area_rect, 2)
        screen.blit(font_medium.render("Log:", True, TEXT_COLOR), (430, 175))

        max_lines = 14
        visible_lines = log_lines[-max_lines:]
        y = 205
        for line in visible_lines:
            screen.blit(font_small.render(line, True, TEXT_COLOR), (430, y))
            y += 22

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
