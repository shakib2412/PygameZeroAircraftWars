import pgzrun
import random
import time
import math

WIDTH = 480
HEIGHT = 700
TITLE = '124-Shakib\'s Aircraft'

# Game states
MENU = 'menu'
PLAYING = 'playing'
GAME_OVER = 'game_over'
PAUSED = 'paused'

# Game variables
score = 0
high_score = 0
level = 1
game_state = MENU
scroll_speed = 1
enemy_spawn_timer = 0
powerup_spawn_timer = 0
explosion_particles = []
score_particles = []
fade_alpha = 0  # For fade effect
game_over_time = 0

# Initialize game objects
background1 = Actor('background')
background1.x = WIDTH / 2
background1.y = 852 / 2
background2 = Actor('background')
background2.x = WIDTH / 2
background2.y = -852 / 2

hero = Actor('hero')
hero.x = WIDTH / 2
hero.y = HEIGHT * 2 / 3
hero.health = 100
hero.invulnerable = False
hero.invulnerable_timer = 0

enemies = []
bullets = []
powerups = []
particles = []

# UI elements
start_button = Actor('button1')
start_button.x = WIDTH / 2
start_button.y = HEIGHT / 2 + 100

restart_button = Actor('button1')
restart_button.x = WIDTH / 2
restart_button.y = HEIGHT - 100


# Score popup animation class
class ScorePopup:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.life = 1.0
        self.dy = -2
        self.scale = 1.5


def create_score_popup(x, y, value):
    score_particles.append(ScorePopup(x, y, value))


def create_enemy():

    enemy = Actor('enemy')
    # Start enemy at a random x position at the top of the screen
    enemy.x = random.randint(50, WIDTH - 50)
    enemy.y = -50  # Start above the screen

    # Set enemy properties
    enemy.health = 1  # Takes 2 hits to destroy
    enemy.speed = random.uniform(2, 4)  # Random speed between 2 and 4

    return enemy

def create_particle(x, y, color, speed=1):
    return {
        'x': x,
        'y': y,
        'dx': random.uniform(-2, 2) * speed,
        'dy': random.uniform(-2, 2) * speed,
        'life': 1.0,
        'color': color,
        'size': random.uniform(2, 4)
    }


def create_explosion(x, y, intensity=1):
    colors = ['orange', 'yellow', 'red']
    for _ in range(int(30 * intensity)):
        color = random.choice(colors)
        particles.append(create_particle(x, y, color, speed=intensity))


def draw():
    background1.draw()
    background2.draw()

    # Draw particles
    for particle in particles:
        screen.draw.filled_circle(
            (particle['x'], particle['y']),
            particle['size'] * particle['life'],
            particle['color']
        )

    # Draw score popups
    for popup in score_particles:
        color = 'yellow'
        alpha = int(255 * popup.life)
        size = int(20 * popup.scale)
        screen.draw.text(
            f"+{popup.value}",
            center=(popup.x, popup.y),
            fontsize=size,
            color=color,
            shadow=(1, 1),
            alpha=alpha
        )

    if game_state == MENU:
        screen.draw.text("124-Shakib's Aircraft",
                         center=(WIDTH / 2, HEIGHT / 3),
                         fontsize=40,
                         color='blue',
                         shadow=(2, 2))
        screen.draw.text("Click Start to Play!",
                         center=(WIDTH / 2, HEIGHT / 2 - 50),
                         fontsize=30,
                         color=(50, 150, 255),
                         shadow=(1, 1))
        screen.draw.text(f"High Score: {high_score}",
                         center=(WIDTH / 2, HEIGHT / 2 - 10),
                         fontsize=25,
                         color='gold',
                         shadow=(1, 1))
        start_button.draw()

    elif game_state in [PLAYING, PAUSED]:
        if hero.invulnerable:
            screen.draw.circle((hero.x, hero.y), 30, 'blue')

        hero.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw()
        for powerup in powerups:
            powerup.draw()

        # Draw HUD with enhanced visuals
        screen.draw.text(f"Score: {score}",
                         (20, 20),
                         fontsize=30,
                         color='white',
                         shadow=(1, 1))
        screen.draw.text(f"High Score: {high_score}",
                         (20, 50),
                         fontsize=20,
                         color='gold',
                         shadow=(1, 1))
        screen.draw.text(f"Level {level}",
                         (WIDTH - 100, 20),
                         fontsize=30,
                         color=(50, 200, 50),
                         shadow=(1, 1))

        # Enhanced health bar
        bar_width = 120
        health_width = (hero.health / 100) * bar_width
        screen.draw.filled_rect(Rect((20, HEIGHT - 30), (bar_width, 15)), (100, 0, 0))
        screen.draw.filled_rect(Rect((20, HEIGHT - 30), (health_width, 15)), (50, 200, 50))
        screen.draw.rect(Rect((20, HEIGHT - 30), (bar_width, 15)), 'white')

        if game_state == PAUSED:
            # Semi-transparent overlay
            screen.draw.filled_rect(Rect((0, 0), (WIDTH, HEIGHT)), (0, 0, 0, 128))
            screen.draw.text("PAUSED",
                             center=(WIDTH / 2, HEIGHT / 2),
                             fontsize=60,
                             color='white',
                             shadow=(2, 2))

    elif game_state == GAME_OVER:
        # Draw game over screen with fade effect
        fade = min(1.0, (time.time() - game_over_time) / 1.5)
        alpha = int(fade * 128)
        screen.draw.filled_rect(Rect((0, 0), (WIDTH, HEIGHT)), (0, 0, 0, alpha))

        # Draw explosion particles
        for particle in explosion_particles:
            screen.draw.filled_circle(
                (particle['x'], particle['y']),
                particle['size'] * particle['life'],
                particle['color']
            )

        # Draw hero (blownup)
        hero.draw()

        # Animated text with shadow
        title_scale = 1 + math.sin(time.time() * 4) * 0.05
        screen.draw.text("Game Over!",
                         center=(WIDTH / 2, HEIGHT / 3),
                         fontsize=int(60 * title_scale),
                         color='red',
                         shadow=(3, 3))

        # Score display with glow effect
        glow = math.sin(time.time() * 2) * 0.3 + 0.7
        screen.draw.text(f"Final Score: {score}",
                         center=(WIDTH / 2, HEIGHT / 2),
                         fontsize=40,
                         color=(255, int(200 * glow), 0),
                         shadow=(2, 2))

        if score >= high_score:
            screen.draw.text("New High Score!",
                             center=(WIDTH / 2, HEIGHT / 2 + 50),
                             fontsize=35,
                             color='gold',
                             shadow=(2, 2))
        else:
            screen.draw.text(f"High Score: {high_score}",
                             center=(WIDTH / 2, HEIGHT / 2 + 50),
                             fontsize=30,
                             color='white',
                             shadow=(1, 1))

        restart_button.draw()


def update():
    global score, game_state, high_score, level, scroll_speed
    global enemy_spawn_timer, powerup_spawn_timer, fade_alpha

    # Update score popups
    for popup in score_particles[:]:
        popup.y += popup.dy
        popup.life -= 0.02
        popup.scale -= 0.01
        if popup.life <= 0:
            score_particles.remove(popup)

    # Update particles
    for particle in particles[:]:
        particle['x'] += particle['dx']
        particle['y'] += particle['dy']
        particle['life'] -= 0.02
        if particle['life'] <= 0:
            particles.remove(particle)

    if game_state == PAUSED:
        return

    if game_state != PLAYING:
        return

    # Update background scroll
    background1.y += scroll_speed
    background2.y += scroll_speed
    if background1.y > 852 * 1.5:
        background1.y = -852 / 2
    if background2.y > 852 * 1.5:
        background2.y = -852 / 2

    # Update invulnerability
    if hero.invulnerable:
        hero.invulnerable_timer -= 1
        if hero.invulnerable_timer <= 0:
            hero.invulnerable = False

    # Spawn enemies
    enemy_spawn_timer -= 1
    if enemy_spawn_timer <= 0:
        enemies.append(create_enemy())
        enemy_spawn_timer = max(20, 60 - level * 5)  # Spawn faster as level increases

    # Update bullets
    for bullet in bullets[:]:
        bullet.y -= 10
        if bullet.y < -50:
            bullets.remove(bullet)
        else:
            for enemy in enemies[:]:
                if bullet.colliderect(enemy):
                    create_explosion(enemy.x, enemy.y)
                    create_score_popup(enemy.x, enemy.y, 10)
                    enemies.remove(enemy)
                    score += 10
                    if score > high_score:
                        high_score = score
                        create_particle(WIDTH / 2, HEIGHT / 2, 'gold', 2)
                    if score % 100 == 0:
                        level += 1
                        scroll_speed += 0.5
                    bullets.remove(bullet)
                    break

    # Update enemies
    for enemy in enemies[:]:
        enemy.y += enemy.speed
        if enemy.y > HEIGHT + 50:
            enemies.remove(enemy)
        elif not hero.invulnerable and hero.colliderect(enemy):
            hero.health -= 20
            create_explosion(hero.x, hero.y, 0.5)
            if hero.health <= 0:
                game_over()
            else:
                hero.invulnerable = True
                hero.invulnerable_timer = 60


def on_mouse_move(pos, rel, buttons):
    if game_state == PLAYING:
        hero.x = pos[0]
        hero.y = pos[1]
    elif game_state == MENU:
        if start_button.collidepoint(pos):
            start_button.image = 'button2'
        else:
            start_button.image = 'button1'
    elif game_state == GAME_OVER:
        if restart_button.collidepoint(pos):
            restart_button.image = 'button2'
        else:
            restart_button.image = 'button1'


def on_mouse_down(pos):
    global game_state

    if game_state == MENU:
        if start_button.collidepoint(pos):
            game_state = PLAYING
            reset_game()
    elif game_state == PLAYING:
        sounds.gun.play()
        new_bullet = Actor('bullet')
        new_bullet.x = hero.x
        new_bullet.y = hero.y - 70
        bullets.append(new_bullet)
    elif game_state == GAME_OVER:
        if restart_button.collidepoint(pos):
            reset_game()
            game_state = PLAYING


def on_key_down(key):
    global game_state
    if key == keys.ESCAPE:
        if game_state == PLAYING:
            game_state = PAUSED
        elif game_state == PAUSED:
            game_state = PLAYING


def game_over():
    global game_state, game_over_time
    sounds.explode.play()
    hero.image = 'hero_blowup'
    game_state = GAME_OVER
    game_over_time = time.time()

    # Create big explosion
    for _ in range(50):
        explosion_particles.append(create_particle(
            hero.x + random.uniform(-20, 20),
            hero.y + random.uniform(-20, 20),
            random.choice(['red', 'orange', 'yellow']),
            2
        ))


def reset_game():
    global score, level, scroll_speed, enemy_spawn_timer, powerup_spawn_timer
    score = 0
    level = 1
    scroll_speed = 1
    enemy_spawn_timer = 0
    powerup_spawn_timer = 0

    hero.image = 'hero'
    hero.x = WIDTH / 2
    hero.y = HEIGHT * 2 / 3
    hero.health = 100
    hero.invulnerable = False

    enemies.clear()
    bullets.clear()
    powerups.clear()
    particles.clear()
    explosion_particles.clear()
    score_particles.clear()


# Start background music
sounds.game_music.play(-1)

pgzrun.go()