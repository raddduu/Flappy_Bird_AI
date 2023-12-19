import pygame
import numpy as np
from flappy_bird_game_AI import FlappyBirdGameAI, Action, Point
import matplotlib.pyplot as plt
import pickle

class Agent:
    BIRD_HEIGHT_DISCRETIZATION_FACTOR = 20
    NEXT_TUBE_HEIGHT_DISCRETIZATION_FACTOR = 20
    NEXT_TUBE_DISTANCE_DISCRETIZATION_FACTOR = 20

    num_states = BIRD_HEIGHT_DISCRETIZATION_FACTOR * NEXT_TUBE_HEIGHT_DISCRETIZATION_FACTOR * NEXT_TUBE_DISTANCE_DISCRETIZATION_FACTOR
    num_actions = 3

    def __init__(self, alpha=0.1, gamma=0.995):
        self.alpha = alpha
        self.gamma = gamma
        self.Q = np.zeros((self.num_states, self.num_actions))

    def save_policy(self, file_name):
        with open(file_name, 'wb') as f:
            pickle.dump(self.Q, f)

    def load_policy(self, file_name):
        with open(file_name, 'rb') as f:
            self.Q = pickle.load(f)

    def get_state(self, game):
        bird_height_bins = np.linspace(0, game.h, self.BIRD_HEIGHT_DISCRETIZATION_FACTOR + 1)
        tube_height_bins = np.linspace(0, game.h, self.NEXT_TUBE_HEIGHT_DISCRETIZATION_FACTOR + 1)
        distance_bins = np.linspace(0, game.w, self.NEXT_TUBE_DISTANCE_DISCRETIZATION_FACTOR + 1)

        bird_height = np.digitize(game.bird.y, bird_height_bins)

        next_tube_x, next_tube_y = game.w, game.h // 2

        if len(game.tubes) > 0:
            next_tube_x = game.tubes[0].x
            next_tube_y = game.tubes[0].y

        next_tube_height = np.digitize(next_tube_y, tube_height_bins)
        next_tube_distance = np.digitize(next_tube_x - game.bird.x, distance_bins)

        return (bird_height, next_tube_height, next_tube_distance)
    
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
            state = self.get_state(game)

            game_over = False
            score = 0
            while not game_over:
                action = self.choose_action(state, epsilon)

                reward, score, game_over = game.play(action)

                if score > 0:
                    print("Episode: " + str(episode) + " Score: " + str(score))

                if score > 100:
                    game_over = True

                next_state = self.get_state(game)

                self.update(state, action, reward, next_state)

                state = next_state

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

    agent.train(game, 10000, verbose=True)

    agent.save_policy('policy.pkl')

    agent.load_policy('policy.pkl')