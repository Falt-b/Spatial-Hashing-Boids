import pygame
import numpy as np
from sys import exit
from random import randint

WIDTH = 400
HEIGHT = 400
FRAME_CAP = 60
BG_COLOR = (20, 20, 20)
PALLETTE = [
    (174, 167, 209),
    (225, 194, 217),
    (251, 249, 226),
    (215, 235, 209),
    (177, 216, 207),
]
BOIDS = 70
CAPTION = "Boids with pygame"
ORIGIN = pygame.Vector2(0, 0)


class HashMap:
    def __init__(self, container_size: int) -> None:
        self.container_size = container_size
        self.conversion_factor = 1 / container_size
        self.width = np.ceil(WIDTH / container_size)
        self.items = {}

    def add_item(self, item: object, hash: int) -> int:
        if hash in self.items:
            self.items[hash] = np.append(self.items[hash], item)
            return self.items[hash].size() - 1
        self.items.setdefault(hash, np.array([item], object))
        return 0

    def remove_item(self, item: object):
        self.items[item.hash] = np.delete(self.items[item.hash], item.index)
        self.update_indexes(item.hash, item.index, -1)

    def update_indexes(self, hash: int, index: int, amount: int):
        for item in self.items[hash][index + 1 :]:
            item.index += amount

    def query(self, hash: int):
        if hash in self.items:
            return self.items[hash]
        return None

    def query_item(self, item: object):
        return np.delete(self.items[item.hash], item.index)

    def query_rect(self, max: np.array, min: np.array):
        pass


class Boid(pygame.sprite.Sprite):
    def __init__(
        self, color: tuple, x: int, y: int, id: int = 0, fill: int = 0
    ) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.image = pygame.surface.Surface((24, 10)).convert()
        self.image.fill(BG_COLOR)
        pygame.draw.polygon(
            self.image,
            self.color,
            [(0, 1), (6, 5), (15, 0), (24, 5), (15, 10), (6, 5), (0, 9)],
            fill,
        )
        self.original_image = self.image.copy().convert()
        self.original_image.set_colorkey((0, 0, 0))
        self.half_width = 12
        self.half_height = 8
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.pos = np.array([x, y], float)
        self.vel = np.array([0, 0], float)
        self.accel = np.array([0, 0], float)
        self.view_range = 100
        self.hash = 0
        self.index = 0
        self.id = id

    def hash(self, table_width: int, container_size: int):
        return (
            int(self.pos[0] / container_size)
            + int(self.pos[1] / container_size) * table_width
        )

    def get_values(self, boids: np.array):
        if boids.size() < 1:
            return 0, 0, 0

        pos = np.array([], float)
        vel = np.array([], float)
        dist = np.array([], float)
        for boid in boids:
            d = ((self.pos[0] - boid.pos[0]) * (self.pos[0] - boid.pos[0])) + (
                (self.pos[1] - boid.pos[1]) * (self.pos[1] - boid.pos[1])
            )
            if boid != self and d <= 10000:
                dist = np.append(dist, d)
                if boid.id == self.id:
                    pos = np.append(pos, boid.pos)
                    vel = np.append(vel, boid.vel)
        smallest_dist = np.argsort(dist)[0]
        sum_pos = np.sum(np.reshape(pos, (-1, 2)))
        sum_vel = np.sum(np.reshape(vel, (-1, 2)))
        return (
            smallest_dist,
            np.divide(sum_pos, boids.size()),
            np.divide(sum_vel, boids.size()),
        )

    def update(self) -> None:

        # rotating and update the image
        angle = ORIGIN.angle_to(self.vel)
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.pos)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()
    t = 0
    dt = 0
    last_frame = 0
    running = True

    b1 = Boid(PALLETTE[0], 200, 200)
    boids = pygame.sprite.Group()
    boids.add(b1)
    a = 0

    while running:
        clock.tick(FRAME_CAP)
        t = pygame.time.get_ticks()
        dt = (t - last_frame) / 1000
        last_frame = t
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        screen.fill(BG_COLOR)

        if a > 360:
            a = 0
        a += 2

        boids.update(a)
        boids.draw(screen)
        pygame.draw.circle(screen, (255, 0, 0), b1.pos, 2)

        pygame.display.update()


if __name__ == "__main__":
    main()
    pygame.quit()
    exit()
