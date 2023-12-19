import pygame
import numpy as np
from flappy_bird_game_AI import FlappyBirdGameAI, Action, Point, BLOCK_SIZE
import matplotlib.pyplot as plt
import pickle

class Agent:
    NEXT_TUBE_DISTANCE_DISCRETIZATION_FACTOR = 20

    num_states = 3 * 4 * NEXT_TUBE_DISTANCE_DISCRETIZATION_FACTOR
    num_actions = 3

    def __init__(self, alpha=0.1, gamma=0.995):
        self.alpha = alpha
        self.gamma = gamma
        self.states_dictionary = self.get_dictionary_for_tuple_to_index_conversion()
        self.Q = np.zeros((self.num_states, self.num_actions))

    def get_dictionary_for_tuple_to_index_conversion(self):
        dictionary = {}
        index = 0
        for i in range(3):
            for j in range(4):
                for k in range(20):
                    dictionary[(i, j, k)] = index
                    index += 1
        return dictionary

    def save_policy(self, file_name):
        with open(file_name, 'wb') as f:
            pickle.dump(self.Q, f)

    def load_policy(self, file_name):
        with open(file_name, 'rb') as f:
            self.Q = pickle.load(f)

    def get_state(self, game):
        distance_bins = np.linspace(0, game.w, self.NEXT_TUBE_DISTANCE_DISCRETIZATION_FACTOR)

        bird_height = game.bird.y

        # non-collision, upper-collision, lower-collision
        bird_collision_case = 0

        if bird_height < 2 * BLOCK_SIZE:
            bird_collision_case = 1
        elif bird_height > game.h - 2 * BLOCK_SIZE:
            bird_collision_case = 2

        next_tube_x, next_tube_y = game.w, game.h // 2

        if len(game.tubes) > 0:
            next_tube_x = game.tubes[0].x
            next_tube_y = game.tubes[0].y

        bird_tube_height_difference = bird_height - next_tube_y
        bird_tube_height_case = 0

        # above or upper
        if bird_tube_height_difference >= 0:
            # upper
            if np.abs(bird_tube_height_difference) <= 5 * BLOCK_SIZE:
                bird_tube_height_case = 0
            # above
            else:
                bird_tube_height_case = 1
        # below or lower
        else:
            # lower
            if np.abs(bird_tube_height_difference) <= 5 * BLOCK_SIZE:
                bird_tube_height_case = 2
            # below
            else:
                bird_tube_height_case = 3

        next_tube_distance_class = np.digitize(next_tube_x - game.bird.x, distance_bins)

        return self.states_dictionary[(bird_collision_case, bird_tube_height_case, next_tube_distance_class)], (bird_collision_case, bird_tube_height_case, next_tube_distance_class)
    
    def policy(self, state):
        return np.argmax(self.Q[state, :])

    def choose_action(self, state, epsilon):
        if np.random.uniform(0, 1) < epsilon:
            action = np.random.choice(self.num_actions)
        else:
            action = np.argmax(self.Q[state, :])

        if action < 0:
            action = 0
        elif action >= self.num_actions:
            action = self.num_actions - 1

        return action

    def update(self, state, action, reward, next_state):
        self.Q[state, action] = self.Q[state, action] + self.alpha * (reward + self.gamma * np.max(self.Q[next_state, :]) - self.Q[state, action])


    def train(self, game, episodes, epsilon_start=1.0, epsilon_end=0.001, epsilon_decay=0.995, verbose=False):
        epsilon = epsilon_start
        scores = []

        if verbose:
            plt.ion()
            fig = plt.figure()
            ax = fig.add_subplot(111)
            line1, = ax.plot(scores)
            plt.show()

        for episode in range(episodes):
            game.reset()
            state, tuple_state = self.get_state(game)
            print(tuple_state, state)

            game_over = False
            score = 0
            while not game_over:
                action = self.choose_action(state, epsilon)

                reward, score, game_over = game.play(action)

                print(self.Q[state, action], tuple_state, state, reward)

                if score > 100:
                    game_over = True

                next_state, tuple_state = self.get_state(game)

                self.update(state, action, reward, next_state)

                state = next_state

            if score > 0:
                    print("Episode: " + str(episode) + " Score: " + str(score))

            scores.append(score)

            if epsilon > epsilon_end:
                epsilon *= epsilon_decay

            if verbose:
                line1.set_ydata(scores)
                line1.set_xdata(range(len(scores)))
                ax.relim()
                ax.autoscale_view(True,True,True)
                plt.draw()
                plt.pause(0.01)

        if verbose:
            plt.ioff()
            plt.show()

if __name__ == "__main__":
    game = FlappyBirdGameAI()

    agent = Agent()

    agent.train(game, 1000, verbose=True)

    agent.save_policy('policy.pkl')

    agent.load_policy('policy.pkl')