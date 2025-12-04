import random
import math
import pickle
import os
import numpy as np
import tensorflow as tf
from collections import deque

class Player():
    """A class that represents a player in the game"""
    
    def __init__(self, coin_type):
        """
        Initialize a player with their coin type
        """
        self.coin_type = coin_type
        
    def complete_move(self):
        """
        A method to make a move and update any learning parameters if any
        """
        pass
    
    def get_coin_type(self):
        """
        Return the coin type of the player
        """
        return self.coin_type
    
    def set_coin_type(self, coin_type):
        """
        Set the coin type of a player
        """
        self.coin_type = coin_type
    
    
class HumanPlayer(Player):
    """A class that represents a human player in the game"""
    
    def __init__(self, coin_type):
        """
        Initialize a human player with their coin type
        """
        Player.__init__(self, coin_type)
        
        
class ComputerPlayer(Player):
    """A class that represents an AI player in the game"""
    
    def __init__(self, coin_type, player_type, mode='learning', file_path="RL/q_data1.pkl", q_table=None):
        """
        Initialize an AI with the proper type which are one of Random and 
        Q-learner currently
        """
        if (player_type == "random"):
            self.player = RandomPlayer(coin_type)
        elif (player_type == "minimax"):
            self.player = MinimaxPlayer(coin_type)
        elif (player_type == "rl" or player_type == "qlearner"):
            self.player = QLearningPlayer(coin_type, mode=mode, file_path=file_path, q_table=q_table)
        elif (player_type == "dqn"):
             self.player = DQNPlayer(coin_type, mode=mode, file_path=file_path, model=q_table)
        else:
            self.player = RandomPlayer(coin_type)
        
    def complete_move(self, coin, board, game_logic, background):
        """
        Move the coin and decide which slot to drop it in and learn from the
        chosen move
        """
        actions = board.get_available_actions()
        state = board.get_state()
        chosen_action = self.choose_action(state, actions)
        
        # Learn from the *previous* move based on the current state (before this new move)
        # We pass the current state because for the *previous* move, this is the "result state"
        self.player.learn(state, actions, chosen_action, False, game_logic)
        
        coin.move_right(background, chosen_action)
        coin.set_column(chosen_action)
        game_over = board.insert_coin(coin, background, game_logic)
        
        # If this move won the game, we need to learn immediately
        if game_over:
             self.player.learn(state, actions, chosen_action, True, game_logic)
        
        return game_over
    
    def get_coin_type(self):
        """
        Return the coin type of the AI player
        """
        return self.player.get_coin_type()
    
    def choose_action(self, state, actions):
        """
        Choose an action (which slot to drop in) based on the state of the
        board
        """
        return self.player.choose_action(state, actions)
    
    def set_mode(self, mode):
        """
        Set the mode of the AI player
        """
        if hasattr(self.player, 'set_mode'):
            self.player.set_mode(mode)
    
    
class RandomPlayer(Player):
    """A class that represents a computer that selects random moves based on the moves available"""
    
    def __init__(self, coin_type):
        """
        Initialize the computer player
        """
        Player.__init__(self, coin_type)
        
    def choose_action(self, state, actions):
        """
        Choose a random action based on the available actions
        """
        return random.choice(actions)

    def set_mode(self, mode):
        """
        Random player doesn't have modes, but method is needed for compatibility
        """
        pass
                
    def learn(self, board, actions, action, game_over, game_logic):
        """
        The random player does not learn from its actions
        """
        pass
       
class QLearningPlayer(Player):
    """A class that represents a Q-learning AI player in the game"""

    def __init__(self, coin_type, mode='learning', epsilon=0.2, alpha=0.3, gamma=0.9, file_path="RL/q_data1.pkl", q_table=None):
        """
        Initialize a Q-learner with parameters epsilon, alpha and gamma
        and its coin type
        """
        Player.__init__(self, coin_type)
        if q_table is not None:
            self.q = q_table
        else:
            self.q = {}
        self.epsilon = epsilon # e-greedy chance of random exploration
        self.alpha = alpha # learning rate
        self.gamma = gamma # discount factor for future rewards 
        self.mode = mode
        self.file_path = file_path
        
        self.mode = mode
        self.file_path = file_path
        
        self.last_state = None
        self.last_action = None
        
        if self.mode == 'playing':
            if q_table is None:
                self.load_data()
            self.epsilon = 0

    def set_mode(self, mode):
        """
        Set the mode of the player (learning or playing)
        """
        self.mode = mode
        if self.mode == 'playing':
            self.epsilon = 0
        else:
            self.epsilon = 0.2 # Reset to default exploration or pass as arg? Using default for now.

    def getQ(self, state, action):
        """
        Return the Q-value for the given state-action pair.
        Defaults to 0 if the pair has not been seen.
        """
        return self.q.get((state, action), 0.0)

    def choose_action(self, state, actions):
        """
        Choose an action (which slot to drop in) based on the state of the
        board using an epsilon-greedy policy.
        """
        if random.random() < self.epsilon:
            return random.choice(actions)
        else:
            q_values = [self.getQ(state, a) for a in actions]
            max_q = max(q_values)
            
            # In case of tie, choose randomly among actions with max Q-value
            best_actions = [actions[i] for i, q_val in enumerate(q_values) if q_val == max_q]
            return random.choice(best_actions)
                
    def learn(self, current_state, actions, chosen_action, game_over, game_logic):
        """
        Update Q-values.
        If game_over is True, it means the current move won the game.
        If game_over is False, we update the Q-value for the *previous* move using the current state.
        """
        if self.mode == 'playing':
            return

        if game_over:
            # Game ended. Determine reward based on outcome.
            winner = game_logic.get_winner()
            if winner == self.coin_type:
                reward = 50
            elif winner == 0: # Tie
                reward = 0.5
            else:
                reward = -50 # Should not strictly happen if I just moved, but good fallback

            prev = self.getQ(current_state, chosen_action)
            maxqnew = 0 # Terminal state
            self.q[(current_state, chosen_action)] = prev + self.alpha * ((reward + self.gamma * maxqnew) - prev)
            self.save_data()
            # Reset last state/action as the episode is over
            self.last_state = None
            self.last_action = None
        else:
            # Delayed update: Update the *previous* move based on the current state (which is the result of prev move + opponent move)
            if self.last_state is not None and self.last_action is not None:
                reward = 0 # No immediate reward for intermediate steps (or small penalty if desired)
                prev = self.getQ(self.last_state, self.last_action)
                
                # maxQ for the current state
                q_values = [self.getQ(current_state, a) for a in actions]
                maxqnew = max(q_values) if q_values else 0
                
                self.q[(self.last_state, self.last_action)] = prev + self.alpha * ((reward + self.gamma * maxqnew) - prev)
            
            # Store current state/action for the next update
            self.last_state = current_state
            self.last_action = chosen_action

    def learn_terminal(self, reward):
        """
        Update the last move with a terminal reward (e.g. loss or draw).
        This is called externally when the game ends and it's not this player's turn.
        """
        if self.mode == 'playing':
            return
            
        if self.last_state is not None and self.last_action is not None:
            prev = self.getQ(self.last_state, self.last_action)
            maxqnew = 0 # Terminal state
            self.q[(self.last_state, self.last_action)] = prev + self.alpha * ((reward + self.gamma * maxqnew) - prev)
            self.save_data()
            
        self.last_state = None
        self.last_action = None

    def save_data(self):
        """
        Save the Q-table to a file
        """
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        try:
            with open(self.file_path, 'wb') as f:
                pickle.dump(self.q, f)
            # print("Q-data saved successfully.") # Optional: for debugging
        except Exception as e:
            print(f"Error saving Q-data: {e}")

    def load_data(self):
        """
        Load the Q-table from a file
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'rb') as f:
                    self.q = pickle.load(f)
                print("Q-data loaded successfully.")
            except Exception as e:
                print(f"Error loading Q-data: {e}")
        else:
            print("No existing Q-data found. Starting with empty Q-table.")


class MinimaxPlayer(Player):
    """placeholder for minimax player"""
    
    def __init__(self, coin_type):
        """
        Initialize the computer player
        """
        Player.__init__(self, coin_type)
        
    def choose_action(self, state, actions):
        """
        placeholder for minimax player
        """
        return random.choice(actions)
                
    def learn(self, board, actions, action, game_over, game_logic):
        """
        placeholder for minimax player
        """
        pass

class DQNPlayer(Player):
    """A class that represents a Deep Q-Network AI player"""

    def __init__(self, coin_type, mode='learning', epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, alpha=0.001, gamma=0.99, file_path="RL/dqn_model.keras", model=None):
        Player.__init__(self, coin_type)
        self.state_size = 42 # 6 rows * 7 cols
        self.action_size = 7
        self.memory = deque(maxlen=2000)
        self.gamma = gamma    # discount rate
        self.epsilon = epsilon  # exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = alpha
        self.mode = mode
        self.file_path = file_path
        
        self.last_state = None
        self.last_action = None
        
        if model is not None:
            self.model = model
        else:
            self.model = self._build_model()
            
        if self.mode == 'playing':
            self.load_data()
            self.epsilon = 0

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Input(shape=(self.state_size,)))
        model.add(tf.keras.layers.Dense(24, activation='relu'))
        model.add(tf.keras.layers.Dense(24, activation='relu'))
        model.add(tf.keras.layers.Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate))
        return model

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == 'playing':
            self.epsilon = 0
        else:
            self.epsilon = 1.0 # Reset or keep?

    def _preprocess_state(self, state):
        # Flatten the 2D board state into a 1D array
        # State is a tuple of tuples, need to convert to numpy array
        flat_state = np.array(state).flatten()
        # Normalize? 0, 1, 2 -> maybe map to 0, 1, -1 or just keep as is.
        # Let's map 0->0, 1->1, 2->-1 if we are player 1, else flip.
        # For now, simple flatten.
        return np.reshape(flat_state, [1, self.state_size])

    def choose_action(self, state, actions):
        if np.random.rand() <= self.epsilon:
            return random.choice(actions)
        
        processed_state = self._preprocess_state(state)
        act_values = self.model.predict(processed_state, verbose=0)
        
        # Filter out invalid actions
        # Set Q-values of invalid actions to -infinity so they are not chosen
        q_values = act_values[0]
        for i in range(self.action_size):
            if i not in actions:
                q_values[i] = -np.inf
                
        return np.argmax(q_values)

    def learn(self, current_state, actions, chosen_action, game_over, game_logic):
        if self.mode == 'playing':
            return

        # We need to store (state, action, reward, next_state, done)
        # But learn() is called *after* the move.
        # So 'current_state' passed here is actually the state *before* the move?
        # Let's check ComputerPlayer.complete_move:
        # state = board.get_state() (State BEFORE move)
        # chosen_action = ...
        # self.player.learn(state, actions, chosen_action, False, game_logic) (Learn called with State BEFORE move)
        
        # Wait, the original Q-learning implementation had a delayed update.
        # "Learn from the *previous* move based on the current state"
        
        # For DQN, we usually store transitions (s, a, r, s', done) in memory and replay.
        
        # If game_over is True:
        # We just made a winning move.
        # Transition: (last_state, last_action, REWARD, current_state(terminal), True)
        # But wait, if we win, there is no next state effectively.
        
        # Let's adapt to the existing call structure.
        
        # If game_over:
        # This move won.
        # We can store (current_state, chosen_action, reward, None, True)
        winner = game_logic.get_winner()
        if winner == self.coin_type:
            reward = 1.0
        elif winner == 0:
            reward = 0.5
        else:
            reward = -1.0
            
        if game_over:
             processed_state = self._preprocess_state(current_state)
             self.remember(processed_state, chosen_action, reward, None, True)
             self.replay(32)
             self.save_data()
             return

        # If not game_over:
        # We just made a move. We don't know the reward yet (unless we use intermediate rewards).
        # We don't know the next state yet (opponent hasn't moved).
        # Actually, in Connect 4, the "next state" for the agent is the state *after* the opponent moves.
        
        # So we need to buffer the *current* move and wait for the *next* turn to complete the transition.
        
        # However, the existing `learn` call structure in `ComputerPlayer` is:
        # 1. `learn(state, ..., False)` (Before move execution? No, line 72 in player.py)
        #    "Learn from the *previous* move based on the current state (before this new move)"
        #    So `state` passed here is the result of (My Prev Move + Opponent Move).
        #    So yes, this `state` is the `next_state` for the *previous* action.
        
        # 2. `learn(state, ..., True)` (After winning move)
        
        # Let's use `self.last_state` and `self.last_action` like the QLearningPlayer.
        
        processed_state = self._preprocess_state(current_state)
        
        if self.last_state is not None and self.last_action is not None:
            # We have a pending transition from the previous turn.
            # The `current_state` is the `next_state` for that transition.
            # Reward is 0 (or small step penalty) because game didn't end.
            self.remember(self.last_state, self.last_action, 0.0, processed_state, False)
            self.replay(32)
            
        self.last_state = processed_state
        self.last_action = chosen_action

    def learn_terminal(self, reward):
        if self.mode == 'playing':
            return
        # Called when game ends and it wasn't my turn (Loss or Tie triggered by opponent)
        if self.last_state is not None and self.last_action is not None:
             # Normalize reward? 50 -> 1, -50 -> -1, 0.5 -> 0.01?
             # Let's stick to small range for NN. 1.0, -1.0, 0.0.
             if reward > 10: r = 1.0
             elif reward < -10: r = -1.0
             else: r = 0.0 # Tie?
             
             # Actually, if I lost, reward is -1.
             
             self.remember(self.last_state, self.last_action, r, None, True)
             self.replay(32)
             self.save_data()
             
        self.last_state = None
        self.last_action = None

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done and next_state is not None:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state, verbose=0)[0]))
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
            
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_data(self):
        try:
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            self.model.save(self.file_path)
        except Exception as e:
            print(f"Error saving DQN model: {e}")

    def load_data(self):
        if os.path.exists(self.file_path):
            try:
                self.model = tf.keras.models.load_model(self.file_path)
                print("DQN model loaded.")
            except Exception as e:
                print(f"Error loading DQN model: {e}")
