import pygame
import sys
import random
from enum import Enum, auto


class GameState(Enum):
    PLAY = auto()
    GAME_OVER = auto()
    QUIT = auto()


class Player(pygame.sprite.Sprite):

    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(1024 / 2, 600))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        pos = pygame.math.Vector2(0, 0)
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            pos.x -= 100
        if keystate[pygame.K_RIGHT]:
            pos.x += 100
        if keystate[pygame.K_UP]:
            pos.y -= 100
        if keystate[pygame.K_DOWN]:
            pos.y += 100
        self.rect.center = self.rect.center + pos / 20
        self.rect.centerx = pygame.math.clamp(self.rect.centerx, 64, 1024 - 64)
        self.rect.centery = pygame.math.clamp(self.rect.centery, 64, 768 - 64)


class Entity(pygame.sprite.Sprite):

    def __init__(self, image, group, pos):
        super().__init__()
        self.image = image
        self.group = group
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.group.add(self)

    def update(self):
        if self.rect.centerx < -50 or self.rect.centerx > 1024 + 50 or self.rect.centery < -50 or self.rect.centery > 768 + 50:
            self.destroy()

    def destroy(self):
        self.valid = False
        self.group.remove(self)


class Bullet(Entity):

    def __init__(self, image, group, pos, velocity):
        super().__init__(image, group, pos)
        self.velocity = velocity

    def update(self):
        self.rect.center = self.rect.center + self.velocity
        super().update()


class Monster(Entity):

    def __init__(self, image, group, x):
        super().__init__(image, group, (x, -40))
        self.orig = x
        self.diff = 4

    def update(self):
        self.rect.center = self.rect.center + pygame.math.Vector2(self.diff, 2)
        if abs(self.rect.centerx - self.orig) > 100:
            self.diff *= -1
        super().update()


class Score:

    def __init__(self):
        self.font = pygame.font.Font(None, 100)
        self.score = 0
        self.flash = 0
        self.update(0)

    def update(self, count):
        if count > 0:
            self.score += count
            self.flash = 255
        self.score_text = self.font.render(f"{self.score}",
                                           True,
                                           (self.flash,
                                            0,
                                            255 - self.flash))
        self.flash = max(0, self.flash - 5)

    def draw(self, screen):
        screen.blit(self.score_text, (10, 10))


class Message:

    def __init__(self):
        self.font = pygame.font.Font(None, 80)
        self.text = self.font.render("Game over", True, (100, 255, 255))

    def draw(self, screen):
        screen.blit(self.text, (1024 / 2 - self.text.get_width() / 2, 300))


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("PySpice")

        self.state = GameState.PLAY
        # Player
        self.player = Player(pygame.image.load("spaceship.png"))
        self.playerGroup = pygame.sprite.Group()
        self.playerGroup.add(self.player)
        self.lastShoot = 0
        # Bullets
        self.playerBulletsGroup = pygame.sprite.Group()
        self.bulletImage = pygame.image.load("bullet.png")
        self.bulletVelocity = pygame.math.Vector2(0, -20)
        # Monsters
        self.monstersGroup = pygame.sprite.Group()
        self.monsterImage = pygame.image.load("shark.png")
        # UI
        self.score = Score()
        self.message = Message()

    def processEvents(self):
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = GameState.QUIT

        # Shoot
        isShooting = self.get_shoot()
        if isShooting and self.state == GameState.PLAY:
            Bullet(self.bulletImage,
                   self.playerBulletsGroup,
                   self.player.rect.center,
                   self.bulletVelocity)

    def get_shoot(self):
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE]:
            t = pygame.time.get_ticks()
            if t - self.lastShoot > 100:
                self.lastShoot = t
                return True
        return False

    def run(self):
        while self.state != GameState.QUIT:
            # Events
            self.processEvents()
            # Bullets
            self.playerBulletsGroup.update()
            self.monstersGroup.update()

            if random.randrange(1, 100, 1) == 1:
                Monster(self.monsterImage,
                        self.monstersGroup,
                        random.randrange(50, 1024 - 50, 1))
            # Player
            if self.state == GameState.PLAY:
                self.player.update()
            # Bullets destroy monsters
            bang = pygame.sprite.groupcollide(self.playerBulletsGroup,
                                              self.monstersGroup,
                                              True,
                                              True,
                                              pygame.sprite.collide_mask)
            self.score.update(len(bang))
            # Monsters destroy player
            if pygame.sprite.groupcollide(self.monstersGroup,
                                          self.playerGroup,
                                          True,
                                          True,
                                          pygame.sprite.collide_mask):
                self.state = GameState.GAME_OVER
            # Display everythinvg
            self.screen.fill((0, 0, 40))
            self.playerBulletsGroup.draw(self.screen)
            self.monstersGroup.draw(self.screen)
            self.playerGroup.draw(self.screen)
            self.score.draw(self.screen)
            if self.state == GameState.GAME_OVER:
                self.message.draw(self.screen)
            pygame.display.update()
            # Clock
            pygame.time.Clock().tick(60)


game = Game()
game.run()
