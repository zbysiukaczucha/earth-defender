import pygame
import asyncio
import sys
import random
import platform
import os

# --- KONFIGURACJA ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Kolory
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)  # Gracz
RED = (255, 0, 0)  # Wrogowie
BLUE = (50, 50, 255)  # Pociski gracza
YELLOW = (255, 255, 0)  # Pociski wroga

# Wykrywanie środowiska (Web vs Desktop)
IS_WEB = sys.platform == "emscripten"

asset_player = None
asset_enemy = None


def load_image(name, scale=None):
    """Ładuje obraz z folderu assets i obsługuje przezroczystość."""
    # Budujemy ścieżkę: assets/nazwa_pliku
    fullname = os.path.join('assets', name)
    try:
        image = pygame.image.load(fullname)
        # convert_alpha() jest KLUCZOWE dla wydajności i przezroczystości
        image = image.convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        return image
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku: {fullname}")
        print("Upewnij się, że folder 'assets' istnieje i zawiera pliki PNG.")
        # Tworzymy awaryjny różowy kwadrat, żeby gra się nie wywaliła
        fallback = pygame.Surface((32, 32))
        fallback.fill((255, 0, 255))
        return fallback


# --- KOMUNIKACJA Z FLASKIEM (API) ---
def send_score_to_backend(score):
    print(f"--- GAME OVER! Twój wynik: {score} ---")
    if IS_WEB:
        from platform import window
        try:
            window.send_score_to_flask("Gracz", score) # Odkomentuj po spięciu z JS
            print(f"WEB: Próba wysłania wyniku {score}")
        except Exception as e:
            print(f"WEB Error: {e}")
    else:
        print(f"[LOCAL]: Symulacja wysłania wyniku {score} do API")


# --- KLASY OBIEKTÓW ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = asset_player
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = asset_enemy
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, speed_x):
        # Wrogowie przesuwają się o zadaną prędkość roju
        self.rect.x += speed_x


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -8

    def update(self, _=None):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 5

    def update(self, _=None):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


# --- FUNKCJA TWORZENIA FALI ---
def create_wave(rows, cols, mobs_group, all_sprites_group):
    """Tworzy siatkę wrogów."""
    start_x = 50
    start_y = 50
    x_spacing = 60
    y_spacing = 50

    for row in range(rows):
        for col in range(cols):
            enemy = Enemy(start_x + col * x_spacing, start_y + row * y_spacing)
            all_sprites_group.add(enemy)
            mobs_group.add(enemy)


# --- GŁÓWNA PĘTLA GRY ---
async def main():
    global asset_player, asset_enemy

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Earth Defender")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    print("Ładowanie grafik...")
    # Możesz podać drugi parametr (szerokość, wysokość) żeby przeskalować grafikę
    asset_player = load_image("player.png", (50, 40))
    asset_enemy = load_image("enemy.png", (40, 30))
    print("Grafiki załadowane.")

    # Grupy
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    # Zmienne stanu gry
    score = 0
    lives = 3
    level = 1

    # Parametry wrogów
    base_enemy_speed = 1.5
    current_enemy_speed = base_enemy_speed

    # Tworzymy pierwszą falę
    create_wave(3, 8, mobs, all_sprites)  # 3 rzędy, 8 kolumn

    running = True
    while running:
        # 1. OBSŁUGA ZDARZEŃ
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Strzał gracza
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        # 2. LOGIKA GRY

        # A. Ruch roju (Swarm Logic)
        move_down = False
        for m in mobs:
            # Jeśli którykolwiek dotknie ściany
            if m.rect.right >= WIDTH or m.rect.left <= 0:
                move_down = True
                break

        if move_down:
            current_enemy_speed *= -1  # Zmień kierunek
            for m in mobs:
                m.rect.y += 20  # Zejdź w dół
                # Korekta, żeby nie utknęli w ścianie
                m.rect.x += current_enemy_speed

                # B. Aktualizacja wszystkich obiektów
        player.update()
        mobs.update(current_enemy_speed)
        bullets.update()
        enemy_bullets.update()

        # C. Strzelanie wrogów (Losowe)
        if mobs and random.randint(1, 60) == 1:
            shooter = random.choice(mobs.sprites())
            ebullet = EnemyBullet(shooter.rect.centerx, shooter.rect.bottom)
            all_sprites.add(ebullet)
            enemy_bullets.add(ebullet)

        # 3. KOLIZJE

        # A. Gracz trafia Wroga
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            score += 10 * level  # Więcej punktów na wyższych poziomach

        # B. Czy poziom wyczyszczony? (Nowa fala)
        if len(mobs) == 0:
            level += 1

            # Zwiększamy trudność (prędkość)
            if current_enemy_speed > 0:
                base_enemy_speed += 0.5
                current_enemy_speed = base_enemy_speed
            else:
                base_enemy_speed += 0.5
                current_enemy_speed = -base_enemy_speed

            # --- POPRAWKA: USUWANIE POCISKÓW ---
            # Musimy użyć .kill(), aby usunąć je też z all_sprites
            for b in bullets:
                b.kill()
            for eb in enemy_bullets:
                eb.kill()
            # -----------------------------------

            # Nowa fala (więcej rzędów co 2 poziomy, max 6)
            rows = min(3 + (level // 2), 6)
            create_wave(rows, 8, mobs, all_sprites)

            # Opcjonalnie: Krótka pauza, żeby gracz odetchnął (1 sekunda)
            # Wymaga importu time, ale w async lepiej nie blokować,
            # więc po prostu wypisujemy komunikat.
            print(f"Poziom {level}! Prędkość: {base_enemy_speed}")

        # C. Wróg trafia Gracza (Strata życia)
        # Sprawdzamy kolizję z pociskami wroga LUB z ciałem wroga
        hit_by_bullet = pygame.sprite.spritecollide(player, enemy_bullets, True)
        hit_by_body = pygame.sprite.spritecollide(player, mobs, True)  # Wróg też znika jak uderzy

        if hit_by_bullet or hit_by_body:
            lives -= 1
            # Reset pozycji gracza
            player.rect.centerx = WIDTH // 2
            # Czyścimy pociski wroga, żeby nie dostać 2 razy pod rząd
            for eb in enemy_bullets:
                eb.kill()

            if lives <= 0:
                running = False
                send_score_to_backend(score)
            else:
                print(f"Strata życia! Pozostało: {lives}")

        # 4. RYSOWANIE
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # UI (Interfejs)
        score_text = font.render(f"Wynik: {score}", True, WHITE)
        level_text = font.render(f"Poziom: {level}", True, WHITE)
        lives_text = font.render(f"Życia: {lives}", True, RED)

        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (WIDTH - 150, 10))
        screen.blit(lives_text, (10, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

    # Ekran końcowy (opcjonalnie, tu po prostu zamykamy)
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())