import pygame
import sys
import random


class Sprite:

    def __init__(self, image):
        self.image = image
        self.set_position(pygame.math.Vector2((0, 0)))

    def display(self, screen):
        screen.blit(self.image, self.pos)

    def set_position(self, pos):
        self.pos = pos - pygame.math.Vector2((self.image.get_width() / 2, self.image.get_height() / 2))


class Bullet:

    def __init__(self, image, pos, velocity):
        self.image = image
        self.pos = pos
        self.velocity = velocity

    def display(self, screen):
        screen.blit(self.image,
                    self.pos - pygame.math.Vector2
                    ((self.image.get_width() / 2,
                      self.image.get_height() / 2)))

    def update(self):
        self.pos += self.velocity
        if self.pos.x < -50 or self.pos.x > 1024 + 50 or self.pos.y < -50 or self.pos.y > 768 + 50:
            return False
        return True


class Monster:

    def __init__(self, image, x):
        self.image = image
        self.pos = pygame.math.Vector2((x, -40))
        self.init = x
        self.diff = 4

    def display(self, screen):
        screen.blit(self.image,
                    self.pos - pygame.math.Vector2
                    ((self.image.get_width() / 2,
                      self.image.get_height() / 2)))

    def update(self):
        self.pos.y += 2
        self.pos.x += self.diff
        if abs(self.pos.x - self.init) > 100:
            self.diff *= -1
        if self.pos.x < -50 or self.pos.x > 1024 + 50 or self.pos.y < -50 or self.pos.y > 768 + 50:
            return False
        return True


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("PySpice")

        self.running = True
        self.mainPos = pygame.math.Vector2(1024 / 2, 600)
        self.ship = Sprite(pygame.image.load("spaceship.png"))
        self.lastShoot = 0
        self.playerBullets = []
        self.bulletImage = pygame.image.load("bullet.png")
        self.bulletVelocity = pygame.math.Vector2(0, -20)
        self.monsterImage = pygame.image.load("shark.png")
        self.monsters = [Monster(self.monsterImage, 200), Monster(self.monsterImage, 500)]

    def processEvents(self):
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        # Movement
        self.mainPos += (self.get_move() / 20)
        self.mainPos.x = pygame.math.clamp(self.mainPos.x, 64, 1024 - 64)
        self.mainPos.y = pygame.math.clamp(self.mainPos.y, 64, 768 - 64)

        # Shoot
        isShooting = self.get_shoot()
        if isShooting:
            self.playerBullets.append(Bullet(self.bulletImage,
                                             self.mainPos.copy(),
                                             self.bulletVelocity))

    def get_shoot(self):
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE]:
            t = pygame.time.get_ticks()
            if t - self.lastShoot > 100:
                self.lastShoot = t
                return True
        return False

    def get_move(self):
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
        return pos

    def run(self):
        while self.running:
            # Events
            self.processEvents()
            # Clear screen
            self.screen.fill((0, 0, 40))
            # Bullets
            remBullets = []
            for playerBullet in self.playerBullets:
                if playerBullet.update():
                    playerBullet.display(self.screen)
                    remBullets.append(playerBullet)
            self.playerBullets = remBullets
            # Monsters
            remMonsters = []
            for monster in self.monsters:
                if monster.update():
                    monster.display(self.screen)
                    remMonsters.append(monster)
            self.monsters = remMonsters
            if random.randrange(1, 100, 1) == 1:
                self.monsters.append(Monster(self.monsterImage, random.randrange(50, 1024 - 50, 1)))
            # Ship
            self.ship.set_position(self.mainPos)
            self.ship.display(self.screen)
            pygame.display.update()
            # Clock
            pygame.time.Clock().tick(60)


game = Game()
game.run()
