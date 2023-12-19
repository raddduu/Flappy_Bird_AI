import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.SysFont('arial.ttf', 25)

class Action(Enum):
    NOTHING = 0
    JUMP = 1
    DIVE = 2

Point = namedtuple('Point', 'x, y')

# RGB Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
BLUE = (128, 255, 255)
GREEN = (0, 200, 0)
LIGHT_GREEN = (128, 255, 128)
DARK_GREEN = (0, 64, 0)
ORANGE = (255, 128, 0)
BROWN = (128, 64, 0)

BLOCK_SIZE = 10
DETAILED_BLOCK_SIZE = 5
SPEED = 10

class FlappyBirdGameAI:

    def __init__(self, w=1280, h=800):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Flappy Bird')
        self.clock = pygame.time.Clock()

        self.reset()
        

    def reset(self):
        self.bird = Point(50, self.h // 2)
        self.score = 0
        self.tubes = []
        self.tube_timer = 0
        self.rise_timer = 0
        self.fall_timer = 0
        self.frame_count = 0


    def spaw_tube(self):
        tube = Point(self.w, random.randint(BLOCK_SIZE * 4, self.h - 4 * BLOCK_SIZE))
        self.tubes.append(tube)
 
    def move_tubes(self):
        for i, tube in enumerate(self.tubes):
            self.tubes[i] = tube._replace(x=tube.x - SPEED)

    def remove_passed_tubes(self):
        counter = 0
        for i, tube in enumerate(self.tubes):
            if tube.x < 0:
                self.tubes.pop(i)
                counter += 1

        self.score += counter

        return counter


    def draw_tubes(self):
        for tube in self.tubes:
            pygame.draw.rect(self.display, LIGHT_GREEN, (tube.x, 0, BLOCK_SIZE // 2, tube.y - BLOCK_SIZE * 5))
            pygame.draw.rect(self.display, GREEN, (tube.x + BLOCK_SIZE // 2, 0, BLOCK_SIZE * 2, tube.y - BLOCK_SIZE * 5))
            pygame.draw.rect(self.display, DARK_GREEN, (tube.x + BLOCK_SIZE * 2.5, 0, BLOCK_SIZE // 2, tube.y - BLOCK_SIZE * 5))

            pygame.draw.rect(self.display, LIGHT_GREEN, (tube.x - BLOCK_SIZE // 2, tube.y - BLOCK_SIZE * 5, BLOCK_SIZE // 2, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREEN, (tube.x, tube.y - BLOCK_SIZE * 5, BLOCK_SIZE * 3, BLOCK_SIZE))
            pygame.draw.rect(self.display, DARK_GREEN, (tube.x + BLOCK_SIZE * 3, tube.y - BLOCK_SIZE * 5, BLOCK_SIZE // 2, BLOCK_SIZE))


            pygame.draw.rect(self.display, LIGHT_GREEN, (tube.x - BLOCK_SIZE // 2, tube.y + BLOCK_SIZE * 5, BLOCK_SIZE // 2, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREEN, (tube.x, tube.y + BLOCK_SIZE * 5, BLOCK_SIZE * 3, BLOCK_SIZE))
            pygame.draw.rect(self.display, DARK_GREEN, (tube.x + BLOCK_SIZE * 3, tube.y + BLOCK_SIZE * 5, BLOCK_SIZE // 2, BLOCK_SIZE))

            pygame.draw.rect(self.display, LIGHT_GREEN, (tube.x, tube.y + BLOCK_SIZE * 6, BLOCK_SIZE // 2, self.h))
            pygame.draw.rect(self.display, GREEN, (tube.x + BLOCK_SIZE // 2, tube.y + BLOCK_SIZE * 6, BLOCK_SIZE * 2, self.h))
            pygame.draw.rect(self.display, DARK_GREEN, (tube.x + BLOCK_SIZE * 2.5, tube.y + BLOCK_SIZE * 6, BLOCK_SIZE // 2, self.h))

    def draw_bird(self, mode="simple"):
        if mode == "simple":
            pygame.draw.rect(self.display, ORANGE, (self.bird.x, self.bird.y - DETAILED_BLOCK_SIZE, 3 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, ORANGE, (self.bird.x, self.bird.y, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, WHITE, (self.bird.x + DETAILED_BLOCK_SIZE, self.bird.y, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, BLACK, (self.bird.x + 2 * DETAILED_BLOCK_SIZE, self.bird.y, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, ORANGE, (self.bird.x - 2 * DETAILED_BLOCK_SIZE, self.bird.y + DETAILED_BLOCK_SIZE, 5 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, RED, (self.bird.x + 3 * DETAILED_BLOCK_SIZE, self.bird.y + DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, ORANGE, (self.bird.x - 3 * DETAILED_BLOCK_SIZE, self.bird.y + 2 * DETAILED_BLOCK_SIZE, 6 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, ORANGE, (self.bird.x - 2 * DETAILED_BLOCK_SIZE, self.bird.y + 3 * DETAILED_BLOCK_SIZE, 4 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, ORANGE, (self.bird.x - DETAILED_BLOCK_SIZE, self.bird.y + 4 * DETAILED_BLOCK_SIZE, 2 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

        if mode == "up":
            pygame.draw.rect(self.display, ORANGE, (self.bird.x, self.bird.y - DETAILED_BLOCK_SIZE, 3 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, BROWN, (self.bird.x - 3 * DETAILED_BLOCK_SIZE, self.bird.y - DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, ORANGE, (self.bird.x, self.bird.y, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, WHITE, (self.bird.x + DETAILED_BLOCK_SIZE, self.bird.y, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, BLACK, (self.bird.x + 2 * DETAILED_BLOCK_SIZE, self.bird.y, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, BROWN, (self.bird.x - 3 * DETAILED_BLOCK_SIZE, self.bird.y, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, BROWN, (self.bird.x - 3 * DETAILED_BLOCK_SIZE, self.bird.y + DETAILED_BLOCK_SIZE, 2 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, ORANGE, (self.bird.x, self.bird.y + DETAILED_BLOCK_SIZE, 3 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, RED, (self.bird.x + 3 * DETAILED_BLOCK_SIZE, self.bird.y + DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, BROWN, (self.bird.x - 3 * DETAILED_BLOCK_SIZE, self.bird.y + 2 * DETAILED_BLOCK_SIZE, 3 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, ORANGE, (self.bird.x, self.bird.y + 2 * DETAILED_BLOCK_SIZE, 3 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, BROWN, (self.bird.x - 2 * DETAILED_BLOCK_SIZE, self.bird.y + 3 * DETAILED_BLOCK_SIZE, 2 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, ORANGE, (self.bird.x, self.bird.y + 3 * DETAILED_BLOCK_SIZE, 2 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, ORANGE, (self.bird.x - DETAILED_BLOCK_SIZE, self.bird.y + 4 * DETAILED_BLOCK_SIZE, 2 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

        if mode == "down":
            pygame.draw.rect(self.display, BROWN, (self.bird.x - 3 * DETAILED_BLOCK_SIZE, self.bird.y - DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, BROWN, (self.bird.x - 3 * DETAILED_BLOCK_SIZE, self.bird.y, 2 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, BROWN, (self.bird.x - 2 * DETAILED_BLOCK_SIZE, self.bird.y + DETAILED_BLOCK_SIZE, 2 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, BROWN, (self.bird.x - 2 * DETAILED_BLOCK_SIZE, self.bird.y + 2 * DETAILED_BLOCK_SIZE, 2 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, ORANGE, (self.bird.x, self.bird.y + 2 * DETAILED_BLOCK_SIZE, 3 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, ORANGE, (self.bird.x - 2 * DETAILED_BLOCK_SIZE, self.bird.y + 3 * DETAILED_BLOCK_SIZE, 3 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, WHITE, (self.bird.x + DETAILED_BLOCK_SIZE, self.bird.y + 3 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, BLACK, (self.bird.x + 2 * DETAILED_BLOCK_SIZE, self.bird.y + 3 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))

            pygame.draw.rect(self.display, ORANGE, (self.bird.x - 1 * DETAILED_BLOCK_SIZE, self.bird.y + 4 * DETAILED_BLOCK_SIZE, 4 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))
            pygame.draw.rect(self.display, RED, (self.bird.x + 3 * DETAILED_BLOCK_SIZE, self.bird.y + 4 * DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE, DETAILED_BLOCK_SIZE))


    def _update_ui(self, mode="simple"):
        self.display.fill(BLUE)

        self.draw_bird(mode=mode)

        self.draw_tubes()

        text = "Score: " + str(self.score)

        label = font.render(text, 1, BLACK)
        self.display.blit(label, (10, 10))


    def check_collision(self):
        if len(self.tubes) == 0:
            return False
        
        closest_tube = self.tubes[0]

        if self.bird.x + BLOCK_SIZE >= closest_tube.x and self.bird.x <= closest_tube.x + BLOCK_SIZE * 3:
            if self.bird.y <= closest_tube.y - BLOCK_SIZE * 5 or self.bird.y + BLOCK_SIZE >= closest_tube.y + BLOCK_SIZE * 5:
                return True

        if not 0 <= self.bird.y <= self.h - BLOCK_SIZE:
            return True

        return False
    
    def _move_bird(self, action):
        #print("ACTION" + str(action))
        if action == Action.JUMP.value:
            #print("JUMP")
            self.bird = self.bird._replace(y= self.bird.y - BLOCK_SIZE)
            self.rise_timer = 6
            self.fall_timer = 0
        elif action == Action.DIVE.value:
            #print("DIVE")
            self.bird = self.bird._replace(y= self.bird.y + BLOCK_SIZE)
            self.fall_timer = 6
            self.rise_timer = 0

        #print("NO ACTION")
        if self.rise_timer > 0:
            self.bird = self.bird._replace(y= self.bird.y - BLOCK_SIZE)
        elif self.fall_timer > 0:
            self.bird = self.bird._replace(y= self.bird.y + BLOCK_SIZE)
        else:
            self.bird = self.bird._replace(y= self.bird.y + BLOCK_SIZE // 2)

    def play(self, action):
        self.frame_count += 1
        self.tube_timer += 1
        self.rise_timer -= 1
        self.fall_timer -= 1

        if self.tube_timer == 50:
            self.spaw_tube()
            self.tube_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move_bird(action)

        reward = 0
        game_over = False
        if self.check_collision():
            game_over = True
            reward = -10
            return reward, self.score, game_over
        
        self.move_tubes()
        reward = 10 * self.remove_passed_tubes()

        self.display.fill(BLACK)

        mode = "simple"

        if self.rise_timer > 0:
            mode = "up"
        elif self.fall_timer > 0:
            mode = "down"

        self._update_ui(mode=mode)
        self.clock.tick(SPEED * 2)
        pygame.display.update()
        return reward, self.score, game_over