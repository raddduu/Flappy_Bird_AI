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
        self.policy = np.zeros(self.num_states)

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
    
    def build_policy(self):
        for state in range(self.num_states):
            self.policy[state] = np.argmax(self.Q[state, :])

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

    def temporal_difference_update(self, state, action, reward, next_state):
        self.Q[state, action] = self.Q[state, action] + self.alpha * (reward + self.gamma * np.max(self.Q[next_state, :]) - self.Q[state, action])


    def temporal_difference_train(self, game, episodes, epsilon_start=1.0, epsilon_end=0.001, epsilon_decay=0.995, verbose=False):
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
            #print(tuple_state, state)

            game_over = False
            score = 0
            while not game_over:
                action = self.choose_action(state, epsilon)

                reward, score, game_over = game.play(action)

                #print(self.Q[state, action], tuple_state, state, reward)

                if score > 500:
                    game_over = True

                next_state, tuple_state = self.get_state(game)

                self.temporal_difference_update(state, action, reward, next_state)

                state = next_state

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

    
    def update_q_sarsa(self, state, action, reward, next_state, next_action):
        current_estimate = self.Q[state][action]
        next_estimate = self.Q[next_state][next_action]
        self.Q[state][action] += self.alpha * (reward + self.gamma * next_estimate - current_estimate)

    def sarsa_train(self, game, episodes, epsilon_start=1.0, epsilon_end=0.001, epsilon_decay=0.995, verbose=False):
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

            game_over = False
            score = 0
            action = self.choose_action(state, epsilon)
            while not game_over:
                reward, score, game_over = game.play(action)

                if score > 500:
                    game_over = True

                next_state, tuple_state = self.get_state(game)
                next_action = self.choose_action(next_state, epsilon)

                self.update_q_sarsa(state, action, reward, next_state, next_action)

                state, action = next_state, next_action

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


    def test_policy(self, game, episodes):
        scores = []

        for episode in range(episodes):
            game.reset()
            state, _ = self.get_state(game)

            beats_human_record = False
            game_over = False
            score = 0
            while not game_over:
                action = self.policy[state]

                _, score, game_over = game.play(action)

                if score > 10000:
                    print('episode:', episode, 'score:', score, 'human record reached')
                    game_over = True
                    beats_human_record = True

                next_state, _ = self.get_state(game)

                state = next_state

            scores.append(score)

            if not beats_human_record:
                print("Episode: " + str(episode) + " Score: " + str(score))

        print("Average score over " + str(episodes) + " episodes: " + str(np.mean(scores)))

if __name__ == "__main__":
    game = FlappyBirdGameAI()

    agent = Agent()

    # print('training temporal difference')
    # agent.temporal_difference_train(game, 10000, verbose=False)

    # print('saving policy')
    # agent.save_policy('policy.pkl')

    print('training sarsa')
    agent.sarsa_train(game, 10000, verbose=False)

    print('saving policy')
    agent.save_policy('sarsa_policy.pkl')

    print('loading policy')
    agent.load_policy('sarsa_policy.pkl')

    print('building policy')
    agent.build_policy()

    print('testing')
    agent.test_policy(game, 50)