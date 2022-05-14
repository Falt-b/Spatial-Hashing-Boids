import pygame
import numpy as np
from sys import exit
from random import randint

WIDTH = 1920
HEIGHT = 600
FRAME_CAP = 60
BG_COLOR = (20, 20, 20)
PALLETTE = [
    (174, 167, 209),
    (225, 194, 217),
    (251, 249, 226),
    (215, 235, 209),
    (177, 216, 207),
]
BOIDS = 400
CAPTION = "Boids with pygame"
ORIGIN = pygame.Vector2(0, 0)
TURNING_FORCE = 0.5


def normalize_vector(vector: np.array):
    return np.sqrt(np.einsum("...i, ...i", vector, vector))


class HashMap:
    def __init__(self, container_size: int) -> None:
        self.container_size = container_size
        self.conversion_factor = 1 / self.container_size
        self.width = np.ceil(WIDTH / self.container_size)
        self.hashes = {}

    def add_item(self, item: object, hash: int) -> int:
        # checks if key already exists and returns index of element in array
        if hash in self.hashes:
            self.hashes[hash] = np.append(self.hashes[hash], item)
            return self.hashes[hash].size() - 1

        # creates key that contains an array with the item
        self.hashes.setdefault(hash, np.array([item], object))
        return 0

    def remove_item(self, item: object):
        # remove element from array by index
        self.hashes[item.hash] = np.delete(self.hashes[item.hash], item.index)

        # if array has nothing left delete it
        if self.hashes[item.hash].size() == 0:
            del self.hashes[item.hash]
            return

        # otherwise update indexes of all other items
        self.update_indexes(item.hash, item.index, -1)

    def update_indexes(self, hash: int, index: int, amount: int):
        for item in self.hashes[hash][index + 1 :]:
            item.index += amount

    def query(self, hash: int):
        if hash in self.hashes:
            return self.hashes[hash]
        return None

    def query_item(self, item: object):
        return np.delete(self.hashes[item.hash], item.index)

    def query_rect(self, max: np.array, min: np.array):
        pass


class Boid(pygame.sprite.Sprite):
    def __init__(
        self, color: tuple, x: int, y: int, id: int = 0, fill: int = 0
    ) -> None:
        # initialize sprite and create image
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
        # create copy of image to be used for rotations
        self.original_image = self.image.copy().convert()
        self.original_image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # initialize values for Boid to keep track of
        self.pos = np.array([x, y], float)
        self.vel = np.array([0, 0], float)
        self.accel = np.array([0, 0], float)
        self.view_range = 100
        self.view_squared = self.view_range * self.view_range
        self.id = id

        self.hash_key = 0
        self.index = 0

    def hash(self, table_width: int, container_size: int):
        return int(
            int(self.pos[0] / container_size)
            + int(self.pos[1] / container_size) * table_width
        )

    def update(self, boid_list: np.array = None, dt: float = 1) -> None:
        # get values for behaviors
        """total_vel = np.array([0, 0], float)
        total_pos = np.array([0, 0], float)
        num_boids = 0
        dist = np.array([], float)
        for boid in boid_list:
            dist = (boid.pos[0] * boid.pos[0]) + (boid.pos[1] * boid.pos[1])
            if boid != self and dist <= self.view_squared:
                total_vel += boid.vel
                total_pos += boid.pos
                dist_arr = np.append(dist_arr, dist)
                num_boids += 1
        dist = np.argsort(dist)
        center = np.divide(total_pos, num_boids) - self.vel - self.pos
        align = np.divide(total_vel, num_boids)
        avoidance = dist * (self.view_range - np.sqrt(dist))

        self.accel += center + align + avoidance"""

        # edge avoidance
        if 0 + self.pos[0] < 50:
            self.vel[0] += TURNING_FORCE
        if WIDTH - self.pos[0] < 50:
            self.vel[0] -= TURNING_FORCE
        if 0 + self.pos[1] < 50:
            self.vel[1] += TURNING_FORCE
        if HEIGHT - self.pos[1] < 50:
            self.vel[1] -= TURNING_FORCE

        # add values
        self.vel += self.accel
        self.pos += self.vel

        # new rotation for boid
        # angle = ORIGIN.angle_to(self.vel)
        # self.image = pygame.transform.rotate(self.original_image, -1 * angle)
        self.rect = self.image.get_rect(center=self.pos)

        # limit speed
        n = normalize_vector(self.vel)
        if n > 5:
            self.vel = np.multiply(np.divide(self.vel, n), 5)
        self.accel = np.array([0, 0], np.float16)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()
    t = 0
    dt = 0
    last_frame = 0
    running = True

    boids_group = pygame.sprite.Group()
    all_boids = np.array([], object)

    for i in range(BOIDS):
        b = Boid((255, 0, 0), randint(0, WIDTH), randint(0, HEIGHT))
        b.vel = np.array([randint(-500, 500) * 0.1, randint(-500, 500) * 0.1])
        boids_group.add(b)
        # all_boids = np.append(all_boids, b)

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

        boids_group.update()
        boids_group.draw(screen)

        pygame.display.update()


if __name__ == "__main__":
    main()
    pygame.quit()
    exit()
