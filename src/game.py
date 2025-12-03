import pygame
import random
from src.constants import WHITE, BLACK, GREEN, RED, BOARD_SIZE, SLOT_SIZE, FONT_NAME
from src.board import Board, ColumnFullException
from src.player import HumanPlayer, ComputerPlayer
from src.coin import Coin

class GameLogic():
    """A class that handles win conditions and determines winner"""
    WIN_SEQUENCE_LENGTH = 4
    
    def __init__(self, board):
        """
        Initialize the GameLogic object with a reference to the game board
        """
        self.board = board
        (num_rows, num_columns) = self.board.get_dimensions()
        self.board_rows = num_rows
        self.board_cols = num_columns
        self.winner_value = 0
    
    def check_game_over(self):
        """
        Check whether the game is over which can be because of a tie or one
        of two players have won
        """
        (last_visited_nodes, player_value) = self.board.get_last_filled_information()
        representation = self.board.get_representation()        
        player_won = self.search_win(last_visited_nodes, representation)
        if player_won:
            self.winner_value = player_value
            
        return ( player_won or self.board.check_board_filled() )
        
        
    
    def search_win(self, last_visited_nodes, representation):
        """
        Determine whether one of the players have won
        """
        for indices in last_visited_nodes:
            current_node = representation[indices[0]][indices[1]]
            if ( current_node.top_left_score == GameLogic.WIN_SEQUENCE_LENGTH or 
                 current_node.top_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.top_right_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.left_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.right_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.bottom_left_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.bottom_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.bottom_right_score == GameLogic.WIN_SEQUENCE_LENGTH ):
                return True
            
        return False
    
    def determine_winner_name(self):
        """
        Return the winner's name
        """
        if (self.winner_value == 1):
            return "BLUE"
        elif (self.winner_value == 2):
            return "RED"
        else:
            return "TIE"
        
    def get_winner(self):
        """
        Return the winner coin type value
        """
        return self.winner_value

class GameView(object):
    """A class that represents the displays in the game"""

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
        """
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.trainedComputer = None
        self.win_list = [0,0]
        
    def initialize_game_variables(self, game_mode):
        """
        Initialize the game board and the GameLogic object
        """
        self.game_board = Board(BOARD_SIZE[0], BOARD_SIZE[1])
        (self.board_rows, self.board_cols) = self.game_board.get_dimensions()
        self.game_logic = GameLogic(self.game_board)
        first_coin_type = random.randint(1,2)
        second_coin_type = 2 if first_coin_type == 1 else 1 
        
        if game_mode == "single":
            self.p1 = HumanPlayer(first_coin_type)
            if (self.trainedComputer == None):
                self.p2 = ComputerPlayer(second_coin_type, "qlearner")
                self.trainedComputer = self.p2
            else:
                self.trainedComputer.set_coin_type(second_coin_type)
                self.p2 = self.trainedComputer
        elif game_mode == "two_player":
            self.p1 = HumanPlayer(first_coin_type)
            self.p2 = HumanPlayer(second_coin_type)
        else:
            self.trainedComputer = None
            self.win_list = [0,0]
            self.p1 = ComputerPlayer(first_coin_type, "qlearner")
            self.p2 = ComputerPlayer(second_coin_type, "qlearner")
        
    
    def main_menu(self, iterations=20):
        """
        Display the main menu screen
        """
        main_menu = True
        play_game = False
        selected_option = 0
        options = ["two_player", "single", "train", "quit"]
        
        self.background.fill(WHITE)
        self.draw_menu(selected_option)
        
        while main_menu:            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.rect1.collidepoint(pos):
                        selected_option = 0
                        play_game = True
                        main_menu = False
                        game_mode = "two_player"
                        
                    elif self.rect2.collidepoint(pos):
                        selected_option = 1
                        play_game = True
                        main_menu = False
                        game_mode = "single"
                        
                    elif self.rect3.collidepoint(pos):
                        selected_option = 2
                        play_game = True
                        main_menu = False
                        game_mode = "train"
                        
                    elif self.rect4.collidepoint(pos):
                        selected_option = 3
                        main_menu = False
                            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        main_menu = False
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        selected_option = (selected_option - 1) % len(options)
                        self.background.fill(WHITE)
                        self.draw_menu(selected_option)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        selected_option = (selected_option + 1) % len(options)
                        self.background.fill(WHITE)
                        self.draw_menu(selected_option)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if options[selected_option] == "quit":
                            main_menu = False
                        else:
                            play_game = True
                            main_menu = False
                            game_mode = options[selected_option]
                        
                if event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    if self.rect1.collidepoint(pos):
                        selected_option = 0
                    elif self.rect2.collidepoint(pos):
                        selected_option = 1
                    elif self.rect3.collidepoint(pos):
                        selected_option = 2
                    elif self.rect4.collidepoint(pos):
                        selected_option = 3
                    self.background.fill(WHITE)
                    self.draw_menu(selected_option)

                if event.type == pygame.QUIT:
                    main_menu = False

                               
            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))            
            
        if not play_game:
            pygame.quit()
            
        elif game_mode == "train":
            self.run(game_mode, iterations)
        
        else:
            self.run(game_mode)


    def run(self, game_mode, iterations=1):
        """
        Main loop in the game
        """
        while (iterations > 0):
            self.initialize_game_variables(game_mode)
            self.background.fill(BLACK)
            self.game_board.draw(self.background)
            game_over = False
            turn_ended = False
            uninitialized = True
            current_type = random.randint(1,2)
            if game_mode == "single":
                human_turn = (self.p1.get_coin_type() == current_type)
                
            elif game_mode == "two_player":
                human_turn = True
                
            else:
                human_turn = False
                
            p1_turn = (self.p1.get_coin_type() == current_type)
                
            (first_slot_X, first_slot_Y) = self.game_board.get_slot(0,0).get_position()
            coin = Coin(current_type)
            game_over_screen = False
            while not game_over:
                         
                if uninitialized:
                    coin = Coin(current_type)
                    coin.set_position(first_slot_X, first_slot_Y - SLOT_SIZE)
                    coin.set_column(0)
                    uninitialized = False
                    coin_inserted = False
                                   
                coin.draw(self.background)
                
                current_player = self.p1 if p1_turn else self.p2
                
                if not human_turn:
                    game_over = current_player.complete_move(coin, self.game_board, self.game_logic, self.background)
                    coin_inserted = True
                    uninitialized = True
                    
                # handle the keyboard events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game_over = True
                        if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and human_turn:
                            if (coin.get_column() + 1 < self.board_cols):
                                coin.move_right(self.background)
                            
                        elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and human_turn:
                            if (coin.get_column() - 1 >= 0):
                                coin.move_left(self.background)
                            
                        elif (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE) and human_turn and not coin_inserted:
                            try:
                                game_over = self.game_board.insert_coin(coin, self.background, self.game_logic)
                                current_player.complete_move()
                                uninitialized = True
                                coin_inserted = True
                                
                            except ColumnFullException as e:
                                pass
                
                if game_over:
                    winner = self.game_logic.determine_winner_name()
                    winner_value = self.game_logic.get_winner()
                    if (winner_value > 0 and game_mode == "train"):
                        self.win_list[winner_value - 1] += 1
                    game_over_screen = True
                    
                if coin_inserted:
                    if game_mode == "single":
                        human_turn = not human_turn
                    current_type = 1 if current_type == 2 else 2 
                    p1_turn = not p1_turn
                         
    
                milliseconds = self.clock.tick(self.fps)
                self.playtime += milliseconds / 1000.0
                pygame.display.flip()
                self.screen.blit(self.background, (0, 0))
                
            iterations -= 1
            
        if game_mode == "train":
            index = self.win_list.index(max(self.win_list))
            self.trainedComputer = self.p1 if index == 0 else self.p2
            self.main_menu()
        
        else:
            self.game_over_view(winner)
        
    def draw_menu(self, selected_option=None):
        """
        Draw the elements for the main menu screen
        """
        font = pygame.font.SysFont(FONT_NAME, 60, bold=True)
        self.title_surface = font.render('CONNECT 4', True, BLACK)
        fw, fh = font.size('CONNECT 4')
        self.background.blit(self.title_surface, ((self.width - fw) // 2, 150))
        two_player_text = '2 Player Mode'
        computer_player_text = 'vs Computer'
        train_text = 'Train Computer'
        quit_text = 'QUIT'
        font = pygame.font.SysFont(FONT_NAME, 40, bold=True)
        
        # Define colors based on selection
        c1 = RED if selected_option == 0 else BLACK
        c2 = RED if selected_option == 1 else BLACK
        c3 = RED if selected_option == 2 else BLACK
        c4 = RED if selected_option == 3 else BLACK

        self.play_surface = font.render(two_player_text, True, c1)
        fw, fh = font.size(two_player_text)     
        self.rect1 = self.play_surface.get_rect(topleft=((self.width - fw) // 2, 300))
        self.background.blit(self.play_surface, ((self.width - fw) // 2, 300) )
        
        computer_play_surface = font.render(computer_player_text, True, c2)
        fw, fh = font.size(computer_player_text)     
        self.rect2 = computer_play_surface.get_rect(topleft=((self.width - fw) // 2, 350))
        self.background.blit(computer_play_surface, ((self.width - fw) // 2, 350) )    
        
        self.train_surface = font.render(train_text, True, c3)
        fw, fh = font.size(train_text)        
        self.rect3 = self.train_surface.get_rect(topleft=((self.width - fw) // 2, 400))
        self.background.blit(self.train_surface, ((self.width - fw) // 2, 400) )        
        
        self.quit_surface = font.render(quit_text, True, c4)
        fw, fh = font.size(quit_text)        
        self.rect4 = self.quit_surface.get_rect(topleft=((self.width - fw) // 2, 450))
        self.background.blit(self.quit_surface, ((self.width - fw) // 2, 450) )   
        
    def game_over_view(self, winner):
        """
        Display the game over screen
        """
        selected_option = 0
        options = ["main_menu", "quit"]
        game_over_screen = True
        main_menu = False
        
        self.background.fill(WHITE)
        self.draw_game_over(winner, selected_option)
        
        while game_over_screen:            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.rect1.collidepoint(pygame.mouse.get_pos()):
                        selected_option = 0
                        main_menu = True
                        game_over_screen = False
                        
                    elif self.rect2.collidepoint(pygame.mouse.get_pos()):
                        selected_option = 1
                        game_over_screen = False
                            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_over_screen = False
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        selected_option = (selected_option - 1) % len(options)
                        self.background.fill(WHITE)
                        self.draw_game_over(winner, selected_option)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        selected_option = (selected_option + 1) % len(options)
                        self.background.fill(WHITE)
                        self.draw_game_over(winner, selected_option)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if options[selected_option] == "quit":
                            game_over_screen = False
                        else:
                            main_menu = True
                            game_over_screen = False
                
                if event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    if self.rect1.collidepoint(pos):
                        selected_option = 0
                    elif self.rect2.collidepoint(pos):
                        selected_option = 1
                    self.background.fill(WHITE)
                    self.draw_game_over(winner, selected_option)

                if event.type == pygame.QUIT:
                    game_over_screen = False

                               
            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))            
            
        if not main_menu:
            pygame.quit()
            
        else:
            self.main_menu()        
        
    
    def draw_game_over(self, winner, selected_option=None):
        """
        Draw the elements for the game over screen
        """        
        font = pygame.font.SysFont(FONT_NAME, 60, bold=True)
        
        if winner != 'TIE':
            title_text = winner + " won!"
        else:
            title_text = "It was a TIE!"
            
        self.title_surface = font.render(title_text, True, GREEN)
        fw, fh = font.size(title_text)
        self.background.blit(self.title_surface, ((self.width - fw) // 2, 150))
        
        play_again_text = 'Return to Main Menu'
        quit_text = 'Quit'
        
        # Define colors based on selection
        c1 = RED if selected_option == 0 else BLACK
        c2 = RED if selected_option == 1 else BLACK

        font = pygame.font.SysFont(FONT_NAME, 40, bold=True)
        self.play_surface = font.render(play_again_text, True, c1)       
        fw, fh = font.size(play_again_text)     
        self.rect1 = self.play_surface.get_rect(topleft=((self.width - fw) // 2, 360))
        self.background.blit(self.play_surface, ((self.width - fw) // 2, 360) )
        
        self.quit_surface = font.render(quit_text, True, c2)
        fw, fh = font.size(quit_text)        
        self.rect2 = self.quit_surface.get_rect(topleft=((self.width - fw) // 2, 410))
        self.background.blit(self.quit_surface, ((self.width - fw) // 2, 410) ) 
