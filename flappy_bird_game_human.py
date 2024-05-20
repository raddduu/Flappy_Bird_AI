import pygame
import random
from enum import Enum
from collections import namedtuple
from agent import Agent
from flappy_bird_game_AI import FlappyBirdGameAI

pygame.init()
font = pygame.font.SysFont('arial.ttf', 25)

Point = namedtuple('Point', 'x, y')

# RGB Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
BLUE = (128, 255, 255)
LB = (128, 255, 128)
GREEN = (0, 200, 0)
LIGHT_GREEN = (128, 255, 128)
DARK_GREEN = (0, 64, 0)
ORANGE = (255, 128, 0)
BROWN = (128, 64, 0)

BLOCK_SIZE = 10
DETAILED_BLOCK_SIZE = 5
SPEED = 15
IMAGE_SIZE = (20, 20)

AI_DATA_PATH = 'td_policy.pkl'

class Action(Enum):
    NOTHING = 0
    JUMP = 1
    DIVE = 2

class PowerUpManager:
    def __init__(self, w, h, probability, bird, image_path):
        self.probability = probability
        self.instances = []
        self.inventory = 0
        self.bird = bird
        self.w = w
        self.h = h
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, IMAGE_SIZE)

    def spawn(self):
        if random.randint(0, 100) < self.probability:
            instance = Point(self.w, random.randint(BLOCK_SIZE * 4, self.h - 4 * BLOCK_SIZE))
            self.instances.append(instance)

    def draw(self, display):
        for instance in self.instances:
            display.blit(self.image, (instance.x, instance.y))

    def move(self):
        for i, instance in enumerate(self.instances):
            self.instances[i] = instance._replace(x=instance.x - SPEED)

    def handle_collision(self, *args):
        pass

    def check_collision(self, bird):
        for i, instance in enumerate(self.instances):
            if bird.x + BLOCK_SIZE * 1.5 >= instance.x and bird.x <= instance.x + BLOCK_SIZE * 1.5:
                if bird.y + BLOCK_SIZE * 1.5 >= instance.y and bird.y <= instance.y + BLOCK_SIZE * 1.5:
                    self.handle_collision(i)
                    break
    
    def remove_passed(self):
        self.instances = [instance for instance in self.instances if instance.x > 0]

    def update_bird_position(self, bird):
        self.bird = bird

    def handle_game_step(self, bird):
        self.update_bird_position(bird)
        self.spawn()
        self.move()
        self.check_collision(self.bird)
        self.remove_passed()


class StackablePowerUpManager(PowerUpManager):
    def __init__(self, w, h, probability, bird, image_path, max_capacity=3):
        super().__init__(w, h, probability, bird, image_path)
        self.max_capacity = max_capacity


    def handle_collision(self, i):
        self.instances.pop(i)
        self.inventory += 1
        self.inventory = min(self.inventory, self.max_capacity)


class InstantUsePowerUpManager(PowerUpManager):
    def __init__(self, w, h, probability, bird, image_path, effect_duration):
        super().__init__(w, h, probability, bird, image_path)
        self.effect_duration = effect_duration
        self.effect_time = 0
        self.previous_time = None

    def handle_collision(self, *args):
        self.effect_time += self.effect_duration
        self.previous_time = pygame.time.get_ticks()   

    def handle_game_step(self, bird):
        if self.previous_time is not None:
            self.effect_time = max(0, self.effect_time - (pygame.time.get_ticks() - self.previous_time))
            self.previous_time = pygame.time.get_ticks()
        if self.effect_time <= 0:
            self.effect_time = 0
            self.previous_time = None
        super().handle_game_step(bird)

class Game:
    def __init__(self, bird, w, h, tubes):
        self.bird = bird
        self.w = w
        self.h = h
        self.tubes = tubes

class AIControlManager(InstantUsePowerUpManager):
    def __init__(self, w, h, probability, bird, image_path, effect_duration, tubes, ai_data_path=AI_DATA_PATH):
        super().__init__(w, h, probability, bird, image_path, effect_duration)
        self.agent = Agent()
        self.agent.load_policy(ai_data_path)
        self.agent.build_policy()
        self.game = Game(bird, w, h, tubes)

    def handle_game_step(self, bird, tubes):
        self.game.bird = bird
        self.game.tubes = tubes
        super().handle_game_step(bird)

class BombsManager(StackablePowerUpManager):
    def __init__(self, w, h, probability, bird, image_path, max_capacity=3):
        super().__init__(w, h, probability, bird, image_path, max_capacity)


class FlappyBirdGame:
    def __init__(self, w=1280, h=800):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Flappy Bird')
        self.clock = pygame.time.Clock()

        self.bird = Point(50, self.h // 2)
        self.score = 0
        self.tubes = []
        self.tube_timer = 0
        self.rise_timer = 0
        self.fall_timer = 0
        self.bombs = []
        self.bomb_inventory = 0
        self.font = pygame.font.Font(None, 36)

        self.bombs_manager = BombsManager(self.w, self.h, 0.005, self.bird, 'bomb_image.png')
        self.ai_manager = AIControlManager(self.w, self.h, 0.005, self.bird, 'brain_image2.png', 9000, self.tubes)

    def destroy_tube(self):
        if self.bombs_manager.inventory > 0 and self.tubes:
            self.tubes.pop(0)
            self.bombs_manager.inventory -= 1

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

        self.bombs_manager.draw(self.display)
        self.ai_manager.draw(self.display)

        self.draw_bomb_counter()
        self.draw_ai_counter()

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
    
    def draw_bomb_counter(self):
        text = self.font.render(f'Bombs: {self.bombs_manager.inventory}', True, BLACK ) 
        self.display.blit(text, (10, self.h - 40))

    def draw_ai_counter(self):
        if self.ai_manager.effect_time > 0:
            text = self.font.render(f'AI time remaining: {round(self.ai_manager.effect_time / 1000, 1)} s', True, BLACK ) 
            self.display.blit(text, (10, self.h - 80))

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

    def play(self):
        self.tube_timer += 1
        self.rise_timer -= 1
        self.fall_timer -= 1

        if self.tube_timer == 50:
            self.spaw_tube()
            self.tube_timer = 0

        self.bombs_manager.handle_game_step(self.bird)
        self.ai_manager.handle_game_step(self.bird, self.tubes)

        if self.ai_manager.effect_time == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.bird = self.bird._replace(y= self.bird.y - BLOCK_SIZE)
                        self.rise_timer = 6
                        self.fall_timer = 0
                    if event.key == pygame.K_DOWN:
                        self.bird = self.bird._replace(y= self.bird.y + BLOCK_SIZE)
                        self.fall_timer = 6
                        self.rise_timer = 0
                    if event.key == pygame.K_SPACE:
                        self.destroy_tube()

            if self.rise_timer > 0:
                self.bird = self.bird._replace(y= self.bird.y - BLOCK_SIZE)
            elif self.fall_timer > 0:
                self.bird = self.bird._replace(y= self.bird.y + BLOCK_SIZE)
            else:
                self.bird = self.bird._replace(y= self.bird.y + BLOCK_SIZE // 2)
        else:
            state, _ = self.ai_manager.agent.get_state(self.ai_manager.game)
            action = self.ai_manager.agent.policy[state]
            self._move_bird(action)

        game_over = False
        if self.check_collision():
            game_over = True
            return self.score, game_over
            
        self.move_tubes()
        self.remove_passed_tubes()

        self.display.fill(BLACK)

        mode = "simple"

        if self.rise_timer > 0:
            mode = "up"
        elif self.fall_timer > 0:
            mode = "down"

        self._update_ui(mode=mode)

        if self.ai_manager.effect_time > 0:
            self.clock.tick(SPEED * 3)
        else:
            self.clock.tick(SPEED * 2)
        
        return self.score, game_over


if __name__ == '__main__':
    game = FlappyBirdGame()
    
    while True:
        score, game_over = game.play()

        if game_over:
            print("Score: ", score)
            break

        pygame.display.update()