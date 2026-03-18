import pygame
import sys
import random
import math
from enum import Enum, auto


class GameState(Enum):
    PLAY = auto()
    GAME_OVER = auto()
    QUIT = auto()


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


class Present(Entity):

    def __init__(self, image, group):
        super().__init__(image, group, (random.randrange(50, 1024 - 50, 1), -40))
        self.velocity = pygame.math.Vector2(0, 2)

    def update(self):
        self.rect.center = self.rect.center + self.velocity
        super().update()


class Shark(Entity):

    def __init__(self, image, group):
        self.x = random.randrange(50, 1024 - 50, 1)
        super().__init__(image, group, (self.x, -40))
        self.amplitude = random.randrange(20, 200, 1)
        self.speed = random.randrange(1, 10, 1) / 100
        self.counter = 0

    def update(self):
        self.rect.center = (self.x + self.amplitude * math.cos(self.counter), self.rect.centery + 1)
        self.counter += self.speed
        super().update()


class Octopus(Entity):

    def __init__(self, image, group, fireImage):
        self.x = random.randrange(50, 1024 - 50, 1)
        super().__init__(image, group, (self.x, -40))
        self.counter = 0
        self.fireImage = fireImage

    def update(self):
        self.rect.center = self.rect.center + pygame.math.Vector2(0, 5)
        super().update()
        self.counter += 1
        if (self.counter % 15 == 0):
            Bullet(self.fireImage,
                   self.group,
                   self.rect.center,
                   pygame.math.Vector2(10 * math.sin(self.counter / 10), 10 * math.cos(self.counter / 10)))


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


class Player(pygame.sprite.Sprite):

    def __init__(self, image, bulletImage, bulletGroup):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(1024 / 2, 600))
        self.mask = pygame.mask.from_surface(self.image)
        self.bulletImage = bulletImage
        self.bulletGroup = bulletGroup
        self.shootingRate = 600
        self.speed = 5
        self.gunCount = 1

    def shoot(self):
        for i in range(1, self.gunCount + 1):
            angle = i * 2 * math.pi / self.gunCount + math.pi
            velocity = pygame.math.Vector2(20 * math.sin(angle), 20 * math.cos(angle))
            Bullet(self.bulletImage,
                   self.bulletGroup,
                   self.rect.center,
                   velocity)

    def levelUp(self):
        rand = random.randrange(1, 4, 1)
        if rand == 1:
            print("Speed boost")
            self.speed += 1
        if rand == 2:
            print("Rate boost")
            self.shootingRate *= 0.9;
        if rand == 3:
            print("Additional guns")
            self.gunCount += 1

    def update(self):
        pos = pygame.math.Vector2(0, 0)
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            pos.x -= self.speed
        if keystate[pygame.K_RIGHT]:
            pos.x += self.speed
        if keystate[pygame.K_UP]:
            pos.y -= self.speed
        if keystate[pygame.K_DOWN]:
            pos.y += self.speed
        self.rect.center = self.rect.center + pos
        self.rect.centerx = pygame.math.clamp(self.rect.centerx, 64, 1024 - 64)
        self.rect.centery = pygame.math.clamp(self.rect.centery, 64, 768 - 64)


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("PySpice")

        self.difficulty = 0
        self.state = GameState.PLAY
        # Bullets
        self.playerBulletsGroup = pygame.sprite.Group()
        # Player
        self.player = Player(pygame.image.load("spaceship.png"),
                             pygame.image.load("bullet.png"),
                             self.playerBulletsGroup)
        self.playerGroup = pygame.sprite.Group()
        self.playerGroup.add(self.player)
        self.lastShoot = 0
        # Monsters
        self.monstersGroup = pygame.sprite.Group()
        self.sharkImage = pygame.image.load("shark.png")
        self.octopusImage = pygame.image.load("octopus.png")
        self.fireImage = pygame.image.load("fireball.png")
        # Presents
        self.presentsGroup = pygame.sprite.Group()
        self.presentImage = pygame.image.load("present.png")
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
            self.player.shoot()

    def get_shoot(self):
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE]:
            t = pygame.time.get_ticks()
            if t - self.lastShoot > self.player.shootingRate:
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
            self.presentsGroup.update()

            rand = random.randrange(1, 200 - self.difficulty, 1)
            if rand == 1:
                Shark(self.sharkImage, self.monstersGroup)
            if rand == 2:
                Octopus(self.octopusImage, self.monstersGroup, self.fireImage)

            rand = random.randrange(1, 100)
            if rand == 1:
                Present(self.presentImage, self.presentsGroup)

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
            # Player can catch presents
            if pygame.sprite.groupcollide(self.presentsGroup,
                                          self.playerGroup,
                                          True,
                                          False,
                                          pygame.sprite.collide_mask):
                self.player.levelUp()
                self.difficulty = min(self.difficulty + 10, 180)
            # Display everything
            self.screen.fill((0, 0, 40))
            self.playerBulletsGroup.draw(self.screen)
            self.monstersGroup.draw(self.screen)
            self.presentsGroup.draw(self.screen)
            self.playerGroup.draw(self.screen)
            self.score.draw(self.screen)
            if self.state == GameState.GAME_OVER:
                self.message.draw(self.screen)
            pygame.display.update()
            # Clock
            pygame.time.Clock().tick(60)


game = Game()
game.run()
