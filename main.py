import pygame
import random
import sys
import math

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

GAME_STATE_START = 1
GAME_STATE_MAIN_GAME = 2
GAME_STATE_REACTION_SHOOT = 3
GAME_STATE_REACTION_DODGE = 4
GAME_STATE_REACTION_CATCH = 5
GAME_STATE_BOSS_FIGHT = 6
GAME_STATE_GAME_OVER = 7
GAME_STATE_STORY = 8

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Магический Квест")
clock = pygame.time.Clock()

# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.speed = 5
        self.score = 0
        self.lives = 3
        self.magic_power = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        self.rect.clamp_ip(screen.get_rect())

# Класс для отображения сюжетных вставок с текстом и таймингом
class StoryScene:
    def __init__(self):
        self.texts = [
            "В древнем королевстве магии появилась темная сила...",
            "Вы - последний маг, способный остановить надвигающуюся тьму.",
            "Соберите магическую энергию, тренируя свои рефлексы...",
            "И сразитесь с Темным Лордом, пока не стало слишком поздно!"
        ]
        self.current_text = 0
        self.text_timer = 0
        self.text_delay = 3000

    def update(self, current_time):
        if current_time - self.text_timer > self.text_delay:
            self.current_text += 1
            self.text_timer = current_time
        return self.current_text < len(self.texts)

    def draw(self, screen, font):
        if self.current_text < len(self.texts):
            text = font.render(self.texts[self.current_text], True, WHITE)
            screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2))

# Мини-игра на стрельбу по движущимся целям
class ReactionShootGame:
    def __init__(self):
        self.targets = []
        self.time_left = 15
        self.score = 0
        self.last_time = pygame.time.get_ticks()
        self.spawn_timer = 0
        self.required_score = 10

    def spawn_target(self):
        target = {
            'rect': pygame.Rect(random.randint(0, WINDOW_WIDTH - 30), 
                              random.randint(0, WINDOW_HEIGHT - 30), 30, 30),
            'speed': random.randint(2, 5),
            'direction': random.uniform(0, 2 * math.pi)
        }
        self.targets.append(target)

    def update(self, events):
        current_time = pygame.time.get_ticks()
        self.time_left -= (current_time - self.last_time) / 1000
        self.last_time = current_time

        if current_time - self.spawn_timer > 1000:
            self.spawn_target()
            self.spawn_timer = current_time

        for target in self.targets:
            target['rect'].x += math.cos(target['direction']) * target['speed']
            target['rect'].y += math.sin(target['direction']) * target['speed']
            
            if target['rect'].left < 0 or target['rect'].right > WINDOW_WIDTH:
                target['direction'] = math.pi - target['direction']
            if target['rect'].top < 0 or target['rect'].bottom > WINDOW_HEIGHT:
                target['direction'] = -target['direction']

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for target in self.targets[:]:
                    if target['rect'].collidepoint(pos):
                        self.targets.remove(target)
                        self.score += 1

        return self.time_left > 0 and self.score < self.required_score

    def draw(self, screen):
        for target in self.targets:
            pygame.draw.rect(screen, RED, target['rect'])
        
        font = pygame.font.Font(None, 36)
        time_text = font.render(f"Время: {self.time_left:.1f}", True, WHITE)
        score_text = font.render(f"Цели: {self.score}/{self.required_score}", True, WHITE)
        screen.blit(time_text, (10, 10))
        screen.blit(score_text, (10, 50))

# Мини-игра на уклонение от падающих сверху снарядов
class ReactionDodgeGame:
    def __init__(self):
        self.player_rect = pygame.Rect(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50, 40, 40)
        self.projectiles = []
        self.time_left = 15
        self.last_time = pygame.time.get_ticks()
        self.spawn_timer = 0
        self.survived = True

    def spawn_projectile(self):
        projectile = {
            'rect': pygame.Rect(random.randint(0, WINDOW_WIDTH - 20), -20, 20, 20),
            'speed': random.randint(5, 8)
        }
        self.projectiles.append(projectile)

    def update(self, events):
        current_time = pygame.time.get_ticks()
        self.time_left -= (current_time - self.last_time) / 1000
        self.last_time = current_time

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_rect.x -= 7
        if keys[pygame.K_RIGHT]:
            self.player_rect.x += 7

        self.player_rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

        if current_time - self.spawn_timer > 500:
            self.spawn_projectile()
            self.spawn_timer = current_time

        for projectile in self.projectiles[:]:
            projectile['rect'].y += projectile['speed']
            if projectile['rect'].top > WINDOW_HEIGHT:
                self.projectiles.remove(projectile)
            elif projectile['rect'].colliderect(self.player_rect):
                self.survived = False
                return False

        return self.time_left > 0 and self.survived

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.player_rect)
        for projectile in self.projectiles:
            pygame.draw.rect(screen, RED, projectile['rect'])
        
        font = pygame.font.Font(None, 36)
        time_text = font.render(f"Выживите: {self.time_left:.1f}", True, WHITE)
        screen.blit(time_text, (10, 10))

# Мини-игра на быстрое нажатие по появляющимся целям
class ReactionCatchGame:
    def __init__(self):
        self.target_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 50, 100, 100)
        self.time_left = 15
        self.score = 0
        self.last_time = pygame.time.get_ticks()
        self.target_timer = pygame.time.get_ticks()
        self.target_visible = False
        self.target_delay = 1000
        self.required_score = 8
        self.can_click = False

    def update(self, events):
        current_time = pygame.time.get_ticks()
        self.time_left -= (current_time - self.last_time) / 1000
        self.last_time = current_time

        if current_time - self.target_timer > self.target_delay:
            self.target_visible = True
            self.can_click = True
            self.target_rect.x = random.randint(50, WINDOW_WIDTH - 150)
            self.target_rect.y = random.randint(50, WINDOW_HEIGHT - 150)
            self.target_timer = current_time

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and self.target_visible and self.can_click:
                if self.target_rect.collidepoint(event.pos):
                    self.score += 1
                    self.target_visible = False
                    self.can_click = False
                    self.target_delay = max(500, self.target_delay - 50)
                else:
                    self.score -= 1

        if current_time - self.target_timer > 800 and self.target_visible:
            self.target_visible = False
            self.can_click = False

        return self.time_left > 0 and self.score < self.required_score

    def draw(self, screen):
        if self.target_visible:
            pygame.draw.rect(screen, GREEN, self.target_rect)
        
        font = pygame.font.Font(None, 36)
        time_text = font.render(f"Время: {self.time_left:.1f}", True, WHITE)
        score_text = font.render(f"Очки: {self.score}/{self.required_score}", True, WHITE)
        screen.blit(time_text, (10, 10))
        screen.blit(score_text, (10, 50))

# Финальная битва с боссом, включающая различные паттерны атак и механики стрельбы
class BossFight:
    def __init__(self):
        self.boss_health = 100
        self.boss_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, 50, 100, 100)
        self.player_rect = pygame.Rect(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50, 40, 40)
        self.boss_projectiles = []
        self.player_projectiles = []
        self.attack_pattern = 0
        self.pattern_timer = pygame.time.get_ticks()
        self.shoot_timer = 0

    def update(self, events):
        current_time = pygame.time.get_ticks()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_rect.x -= 7
        if keys[pygame.K_RIGHT]:
            self.player_rect.x += 7

        if current_time - self.shoot_timer > 500:
            if keys[pygame.K_SPACE]:
                self.player_projectiles.append(
                    pygame.Rect(self.player_rect.centerx - 5, 
                              self.player_rect.top, 10, 10)
                )
                self.shoot_timer = current_time

        if current_time - self.pattern_timer > 3000:
            self.attack_pattern = (self.attack_pattern + 1) % 3
            self.pattern_timer = current_time

        if self.attack_pattern == 0:
            if current_time - self.shoot_timer > 300:
                self.boss_projectiles.append(
                    pygame.Rect(self.boss_rect.centerx - 5,
                              self.boss_rect.bottom, 10, 10)
                )
        elif self.attack_pattern == 1:
            if current_time - self.shoot_timer > 200:
                for angle in [-0.2, 0, 0.2]:
                    self.boss_projectiles.append({
                        'rect': pygame.Rect(self.boss_rect.centerx - 5,
                                          self.boss_rect.bottom, 10, 10),
                        'angle': angle
                    })
        
        for proj in self.player_projectiles[:]:
            proj.y -= 10
            if proj.bottom < 0:
                self.player_projectiles.remove(proj)
            elif proj.colliderect(self.boss_rect):
                self.boss_health -= 5
                self.player_projectiles.remove(proj)

        for proj in self.boss_projectiles[:]:
            if isinstance(proj, pygame.Rect):
                proj.y += 7
                if proj.top > WINDOW_HEIGHT:
                    self.boss_projectiles.remove(proj)
                elif proj.colliderect(self.player_rect):
                    return False
            else:
                proj['rect'].x += math.sin(proj['angle']) * 5
                proj['rect'].y += 7
                if proj['rect'].top > WINDOW_HEIGHT:
                    self.boss_projectiles.remove(proj)
                elif proj['rect'].colliderect(self.player_rect):
                    return False

        return self.boss_health > 0

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.boss_rect)
        
        pygame.draw.rect(screen, BLUE, self.player_rect)
        
        for proj in self.player_projectiles:
            pygame.draw.rect(screen, GREEN, proj)
        
        for proj in self.boss_projectiles:
            if isinstance(proj, pygame.Rect):
                pygame.draw.rect(screen, PURPLE, proj)
            else:
                pygame.draw.rect(screen, PURPLE, proj['rect'])

        health_bar = pygame.Rect(50, 20, self.boss_health * 2, 20)
        pygame.draw.rect(screen, RED, health_bar)
        
        font = pygame.font.Font(None, 36)
        health_text = font.render(f"Здоровье босса: {self.boss_health}", True, WHITE)
        screen.blit(health_text, (50, 50))

# Основной класс игры, управляющий всеми игровыми состояниями и логикой
class Game:
    def __init__(self):
        self.state = GAME_STATE_START
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.font = pygame.font.Font(None, 36)
        self.reaction_shoot = None
        self.reaction_dodge = None
        self.reaction_catch = None
        self.boss_fight = None
        self.story = StoryScene()
        self.minigame_result = None
        self.story_started = pygame.time.get_ticks()

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == GAME_STATE_START:
                        self.state = GAME_STATE_STORY
                        self.story_started = pygame.time.get_ticks()
                    elif self.state == GAME_STATE_GAME_OVER:
                        self.__init__()
                if event.key == pygame.K_1 and self.state == GAME_STATE_MAIN_GAME:
                    self.state = GAME_STATE_REACTION_SHOOT
                    self.reaction_shoot = ReactionShootGame()
                if event.key == pygame.K_2 and self.state == GAME_STATE_MAIN_GAME:
                    self.state = GAME_STATE_REACTION_DODGE
                    self.reaction_dodge = ReactionDodgeGame()
                if event.key == pygame.K_3 and self.state == GAME_STATE_MAIN_GAME:
                    self.state = GAME_STATE_REACTION_CATCH
                    self.reaction_catch = ReactionCatchGame()
                if event.key == pygame.K_4 and self.state == GAME_STATE_MAIN_GAME:
                    if self.player.magic_power >= 100:
                        self.state = GAME_STATE_BOSS_FIGHT
                        self.boss_fight = BossFight()
                    
        if self.state == GAME_STATE_STORY:
            if not self.story.update(pygame.time.get_ticks()):
                self.state = GAME_STATE_MAIN_GAME

        if self.state == GAME_STATE_REACTION_SHOOT and self.reaction_shoot:
            if not self.reaction_shoot.update(events):
                self.minigame_result = self.reaction_shoot.score >= self.reaction_shoot.required_score
                self.state = GAME_STATE_MAIN_GAME
                if self.minigame_result:
                    self.player.score += 100
                    self.player.magic_power += 20
                else:
                    self.player.lives -= 1

        if self.state == GAME_STATE_REACTION_DODGE and self.reaction_dodge:
            if not self.reaction_dodge.update(events):
                self.minigame_result = self.reaction_dodge.survived
                self.state = GAME_STATE_MAIN_GAME
                if self.minigame_result:
                    self.player.score += 150
                    self.player.magic_power += 30
                else:
                    self.player.lives -= 1

        if self.state == GAME_STATE_REACTION_CATCH and self.reaction_catch:
            if not self.reaction_catch.update(events):
                self.minigame_result = self.reaction_catch.score >= self.reaction_catch.required_score
                self.state = GAME_STATE_MAIN_GAME
                if self.minigame_result:
                    self.player.score += 120
                    self.player.magic_power += 25
                else:
                    self.player.lives -= 1

        if self.state == GAME_STATE_BOSS_FIGHT and self.boss_fight:
            if not self.boss_fight.update(events):
                self.state = GAME_STATE_GAME_OVER
            
        if self.player.lives <= 0:
            self.state = GAME_STATE_GAME_OVER

        return True

    def update(self):
        if self.state == GAME_STATE_MAIN_GAME:
            self.all_sprites.update()

    def draw(self):
        screen.fill(BLACK)

        if self.state == GAME_STATE_START:
            self.draw_start_screen()
        elif self.state == GAME_STATE_STORY:
            self.story.draw(screen, self.font)
        elif self.state == GAME_STATE_MAIN_GAME:
            self.draw_main_game()
        elif self.state == GAME_STATE_REACTION_SHOOT and self.reaction_shoot:
            self.reaction_shoot.draw(screen)
        elif self.state == GAME_STATE_REACTION_DODGE and self.reaction_dodge:
            self.reaction_dodge.draw(screen)
        elif self.state == GAME_STATE_REACTION_CATCH and self.reaction_catch: 
            self.reaction_catch.draw(screen)
        elif self.state == GAME_STATE_BOSS_FIGHT and self.boss_fight:
            self.boss_fight.draw(screen)
        elif self.state == GAME_STATE_GAME_OVER:
            self.draw_game_over_screen()

        pygame.display.flip()
    def draw_start_screen(self):
        title = self.font.render("Магический Квест", True, WHITE)
        start_text = self.font.render("Нажмите ПРОБЕЛ для начала", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
        screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, 300))

    def draw_main_game(self):
        self.all_sprites.draw(screen)
        
        score_text = self.font.render(f"Очки: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"Жизни: {self.player.lives}", True, WHITE)
        magic_text = self.font.render(f"Магия: {self.player.magic_power}/100", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(magic_text, (10, 70))

        instructions = [
            "1 - Тренировка стрельбы",
            "2 - Тренировка уклонения",
            "3 - Тренировка реакции",
            "4 - Битва с боссом (требуется 100 магии)"
        ]
        for i, text in enumerate(instructions):
            instruction_text = self.font.render(text, True, WHITE)
            screen.blit(instruction_text, (10, WINDOW_HEIGHT - 120 + i * 30))

    def draw_story_screen(self):
        self.story.draw(screen, self.font)

    def draw_game_over_screen(self):
            instruction_text = self.font.render(text, True, WHITE)
            screen.blit(instruction_text, (10, WINDOW_HEIGHT - 120 + i * 30))

    def draw_game_over_screen(self):
        game_over_text = self.font.render("ИГРА ОКОНЧЕНА", True, WHITE)
        score_text = self.font.render(f"Финальный счёт: {self.player.score}", True, WHITE)
        restart_text = self.font.render("Нажмите ПРОБЕЛ для перезапуска", True, WHITE)
        
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 200))
        screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 250))
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 300))

def main():
    game = Game()
    running = True
    
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()    