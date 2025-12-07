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
        self._type = None
        
    def type(self):
        """
        Return the type of the player
        """
        return self._type
        
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
        self._type = "human"
        
        
        
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
        elif (player_type == "dqn"):
             self.player = DQNPlayer(coin_type, mode=mode, file_path=file_path, model=q_table)
        else:
            self.player = RandomPlayer(coin_type)
            
    def type(self):
        """
        Return the type of the inner player
        """
        return self.player.type()
        
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
        self._type = "random"
        
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
       



class MinimaxPlayer(Player):
    """placeholder for minimax player"""
    
    def __init__(self, coin_type):
        """
        Initialize the computer player
        """
        Player.__init__(self, coin_type)
        self._type = "minimax"
        
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

    def __init__(self, coin_type, mode='learning', epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.9995, alpha=0.001, gamma=0.99, file_path="RL/dqn_model.keras", model=None):
        Player.__init__(self, coin_type)
        self._type = "dqn"
        self.state_size = 42 # 6 rows * 7 cols
        self.action_size = 7
        self.memory = deque(maxlen=5000)
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
        model.add(tf.keras.layers.Dense(128, activation='relu'))
        model.add(tf.keras.layers.Dense(128, activation='relu'))
        model.add(tf.keras.layers.Dense(64, activation='relu'))
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
        
        processed = np.zeros_like(flat_state)
        my_coin = self.coin_type
        opponent_coint = 1 if my_coin == 2 else 2
        processed[flat_state == my_coin] = 1
        processed[flat_state == opponent_coint] = -1
        processed[flat_state == 0] = 0
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
            reward = 10.0
        elif winner == 0:
            reward = 0.0
        else:
            reward = -10.0
            
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
             if reward > 10: r = 10.0
             elif reward < -10: r = -10.0
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
        # Chuyển đổi list of tuples thành các numpy array riêng biệt để xử lý song song
        states = np.array([i[0] for i in minibatch])
        states = np.squeeze(states) # Đảm bảo shape là (batch_size, 42) thay vì (batch_size, 1, 42)
        
        actions = np.array([i[1] for i in minibatch])
        rewards = np.array([i[2] for i in minibatch])
        next_states = np.array([i[3] if i[3] is not None else np.zeros((1, self.state_size)) for i in minibatch])
        next_states = np.squeeze(next_states)
        dones = np.array([i[4] for i in minibatch])

        # Dự đoán Q-values hiện tại và tương lai cho cả batch cùng lúc (chỉ tốn 2 lần gọi predict)
        # Tốc độ nhanh hơn gấp hàng chục lần so với vòng lặp
        targets = self.model.predict_on_batch(states)
        next_q_values = self.model.predict_on_batch(next_states)

        # Tính toán Q-learning target: Q(s,a) = r + gamma * max(Q(s', a'))
        # np.amax(next_q_values, axis=1) lấy giá trị lớn nhất của mỗi hàng
        targets[range(batch_size), actions] = rewards + self.gamma * np.amax(next_q_values, axis=1) * (1 - dones)

        # Train model một lần duy nhất cho cả batch
        self.model.fit(states, targets, epochs=1, verbose=0)
        
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
