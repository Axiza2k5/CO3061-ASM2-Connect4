import random
import math
import pickle
import os

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
    
    def __init__(self, coin_type, player_type, mode='learning'):
        """
        Initialize an AI with the proper type which are one of Random and 
        Q-learner currently
        """
        if (player_type == "random"):
            self.player = RandomPlayer(coin_type)
        elif (player_type == "minimax"):
            self.player = MinimaxPlayer(coin_type)
        elif (player_type == "rl" or player_type == "qlearner"):
            self.player = QLearningPlayer(coin_type, mode=mode)
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
        coin.move_right(background, chosen_action)
        coin.set_column(chosen_action)
        game_over = board.insert_coin(coin, background, game_logic)
        self.player.learn(board, actions, chosen_action, game_over, game_logic)
        
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

    def __init__(self, coin_type, mode='learning', epsilon=0.2, alpha=0.3, gamma=0.9, file_path="RL/q_data1.pkl"):
        """
        Initialize a Q-learner with parameters epsilon, alpha and gamma
        and its coin type
        """
        Player.__init__(self, coin_type)
        self.q = {}
        self.epsilon = epsilon # e-greedy chance of random exploration
        self.alpha = alpha # learning rate
        self.gamma = gamma # discount factor for future rewards 
        self.mode = mode
        self.file_path = file_path
        
        if self.mode == 'playing':
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
                
    def learn(self, board, actions, chosen_action, game_over, game_logic):
        """
        Determine the reward based on its current chosen action and update
        the Q table using the reward recieved and the maximum future reward
        based on the resulting state due to the chosen action
        """
        if self.mode == 'playing':
            return

        reward = 0
        if (game_over):
            win_value = game_logic.get_winner()
            if win_value == 0: # Draw
                reward = 0.5
            elif win_value == self.coin_type: # Win
                reward = 50
            else: # Loss
                reward = -50
        else:
            reward = -1 # Penalty for not ending the game
            
        prev_state = board.get_prev_state()
        prev = self.getQ(prev_state, chosen_action)
        result_state = board.get_state()
        
        # If the game is over, there are no future actions, so maxqnew is 0
        if game_over:
            maxqnew = 0
        else:
            # Get available actions for the new state
            next_actions = board.get_available_actions()
            if not next_actions: # No available actions, game might be a draw or full
                maxqnew = 0
            else:
                maxqnew = max([self.getQ(result_state, a) for a in next_actions])
                
        self.q[(prev_state, chosen_action)] = prev + self.alpha * ((reward + self.gamma*maxqnew) - prev)
        
        if game_over:
            self.save_data()

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