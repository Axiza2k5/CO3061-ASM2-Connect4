import random
import math

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
    
    def __init__(self, coin_type, player_type):
        """
        Initialize an AI with the proper type which are one of Random and 
        Q-learner currently
        """
        if (player_type == "random"):
            self.player = RandomPlayer(coin_type)
        elif (player_type == "minimax"):
            self.player = MinimaxPlayer(coin_type)
        else:
            self.player = QLearningPlayer(coin_type)
        
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
                
    def learn(self, board, actions, action, game_over, game_logic):
        """
        The random player does not learn from its actions
        """
        pass
       
class QLearningPlayer(Player):
    """A class that represents an AI using Q-learning algorithm"""
    
    def __init__(self, coin_type, epsilon=0.2, alpha=0.3, gamma=0.9):
        """
        Initialize a Q-learner with parameters epsilon, alpha and gamma
        and its coin type
        """
        Player.__init__(self, coin_type)
        self.q = {}
        self.epsilon = epsilon # e-greedy chance of random exploration
        self.alpha = alpha # learning rate
        self.gamma = gamma # discount factor for future rewards 
        
    def getQ(self, state, action):
        """
        Return a probability for a given state and action where the greater
        the probability the better the move
        """
        # encourage exploration; "optimistic" 1.0 initial values
        if self.q.get((state, action)) is None:
            self.q[(state, action)] = 1.0
        return self.q.get((state, action))    
        
    def choose_action(self, state, actions):
        """
        Return an action based on the best move recommendation by the current
        Q-Table with a epsilon chance of trying out a new move
        """
        current_state = state

        if random.random() < self.epsilon: # explore!
            chosen_action = random.choice(actions)
            return chosen_action

        qs = [self.getQ(current_state, a) for a in actions]
        maxQ = max(qs)

        if qs.count(maxQ) > 1:
            # more than 1 best option; choose among them randomly
            best_options = [i for i in range(len(actions)) if qs[i] == maxQ]
            i = random.choice(best_options)
        else:
            i = qs.index(maxQ)

        return actions[i]
    
    def learn(self, board, actions, chosen_action, game_over, game_logic):
        """
        Determine the reward based on its current chosen action and update
        the Q table using the reward recieved and the maximum future reward
        based on the resulting state due to the chosen action
        """
        reward = 0
        if (game_over):
            win_value = game_logic.get_winner()
            if win_value == 0:
                reward = 0.5
            elif win_value == self.coin_type:
                reward = 1
            else:
                reward = -2
        prev_state = board.get_prev_state()
        prev = self.getQ(prev_state, chosen_action)
        result_state = board.get_state()
        maxqnew = max([self.getQ(result_state, a) for a in actions])
        self.q[(prev_state, chosen_action)] = prev + self.alpha * ((reward + self.gamma*maxqnew) - prev)    

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