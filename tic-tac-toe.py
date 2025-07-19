import pygame
import sys
import random
import numpy as np
from enum import Enum

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_SIZE = 3
CELL_SIZE = 120
BOARD_PADDING = 50
ANIMATION_SPEED = 15
BG_COLOR = (28, 35, 43)
GRID_COLOR = (86, 98, 112)
X_COLOR = (239, 71, 111)
O_COLOR = (6, 214, 160)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (58, 134, 255)
BUTTON_HOVER_COLOR = (80, 150, 255)

class Player(Enum):
    HUMAN = 1
    AI = 2

class GameMode(Enum):
    PVP = 1
    PVC = 2

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class TicTacToe:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Advanced Tic-Tac-Toe")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.reset_game()
        
    def reset_game(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = 1  # Player 1 starts (X)
        self.game_over = False
        self.winner = 0
        self.winning_cells = []
        self.move_history = []
        self.redo_history = []
        self.scores = {1: 0, 2: 0}
        self.game_history = []
        self.player1_type = Player.HUMAN
        self.player2_type = Player.AI
        self.game_mode = GameMode.PVC
        self.difficulty = Difficulty.HARD
        self.player_symbols = {1: 'X', 2: 'O'}
        self.animation_progress = 0
        self.last_move = None

    def make_move(self, row, col):
        if self.board[row][col] == 0 and not self.game_over:
            self.board[row][col] = self.current_player
            self.move_history.append((row, col, self.current_player))
            self.redo_history = []  # Clear redo history on new move
            self.last_move = (row, col)
            self.check_game_state()
            self.current_player = 3 - self.current_player  # Switch player (1->2, 2->1)
            return True
        return False

    def undo_move(self):
        if self.move_history:
            row, col, player = self.move_history.pop()
            self.board[row][col] = 0
            self.redo_history.append((row, col, player))
            self.current_player = player
            self.game_over = False
            self.winner = 0
            self.winning_cells = []
            return True
        return False

    def redo_move(self):
        if self.redo_history:
            row, col, player = self.redo_history.pop()
            self.board[row][col] = player
            self.move_history.append((row, col, player))
            self.current_player = 3 - player
            self.check_game_state()
            return True
        return False

    def check_game_state(self):
        # Check rows
        for row in range(BOARD_SIZE):
            if self.board[row][0] != 0 and all(self.board[row][0] == self.board[row][j] for j in range(BOARD_SIZE)):
                self.game_over = True
                self.winner = self.board[row][0]
                self.winning_cells = [(row, j) for j in range(BOARD_SIZE)]
                self.scores[self.winner] += 1
                self.record_game()
                return

        # Check columns
        for col in range(BOARD_SIZE):
            if self.board[0][col] != 0 and all(self.board[0][col] == self.board[i][col] for i in range(BOARD_SIZE)):
                self.game_over = True
                self.winner = self.board[0][col]
                self.winning_cells = [(i, col) for i in range(BOARD_SIZE)]
                self.scores[self.winner] += 1
                self.record_game()
                return

        # Check diagonals
        if self.board[0][0] != 0 and all(self.board[0][0] == self.board[i][i] for i in range(BOARD_SIZE)):
            self.game_over = True
            self.winner = self.board[0][0]
            self.winning_cells = [(i, i) for i in range(BOARD_SIZE)]
            self.scores[self.winner] += 1
            self.record_game()
            return

        if self.board[0][BOARD_SIZE-1] != 0 and all(self.board[0][BOARD_SIZE-1] == self.board[i][BOARD_SIZE-1-i] for i in range(BOARD_SIZE)):
            self.game_over = True
            self.winner = self.board[0][BOARD_SIZE-1]
            self.winning_cells = [(i, BOARD_SIZE-1-i) for i in range(BOARD_SIZE)]
            self.scores[self.winner] += 1
            self.record_game()
            return

        # Check for draw
        if all(self.board[i][j] != 0 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)):
            self.game_over = True
            self.record_game()
            return

    def record_game(self):
        game_data = {
            "board": self.board.copy(),
            "winner": self.winner,
            "moves": self.move_history.copy(),
            "player1_type": self.player1_type,
            "player2_type": self.player2_type,
            "difficulty": self.difficulty
        }
        self.game_history.append(game_data)

    def get_ai_move(self):
        if self.difficulty == Difficulty.EASY:
            return self.get_random_move()
        elif self.difficulty == Difficulty.MEDIUM:
            return self.get_medium_move()
        else:
            return self.get_best_move()

    def get_random_move(self):
        empty_cells = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if self.board[i][j] == 0]
        return random.choice(empty_cells) if empty_cells else (None, None)

    def get_medium_move(self):
        # Try to win if possible
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == 0:
                    self.board[i][j] = self.current_player
                    self.check_game_state()
                    self.board[i][j] = 0
                    if self.game_over:
                        return (i, j)
        
        # Block opponent from winning
        opponent = 3 - self.current_player
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == 0:
                    self.board[i][j] = opponent
                    self.check_game_state()
                    self.board[i][j] = 0
                    if self.game_over:
                        return (i, j)
        
        # If no immediate win or block, choose randomly
        return self.get_random_move()

    def get_best_move(self):
        best_score = -float('inf')
        best_move = (-1, -1)
        
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == 0:
                    self.board[i][j] = self.current_player
                    score = self.minimax(0, False)
                    self.board[i][j] = 0
                    
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
        
        return best_move

    def minimax(self, depth, is_maximizing):
        self.check_game_state()
        
        if self.game_over:
            if self.winner == self.current_player:
                return 10 - depth
            elif self.winner == 3 - self.current_player:
                return depth - 10
            else:
                return 0
                
        if is_maximizing:
            best_score = -float('inf')
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if self.board[i][j] == 0:
                        self.board[i][j] = self.current_player
                        score = self.minimax(depth + 1, False)
                        self.board[i][j] = 0
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if self.board[i][j] == 0:
                        self.board[i][j] = 3 - self.current_player
                        score = self.minimax(depth + 1, True)
                        self.board[i][j] = 0
                        best_score = min(score, best_score)
            return best_score

    def draw_board(self):
        # Draw game title
        title = self.font.render("Advanced Tic-Tac-Toe", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Draw scores
        score_text = self.small_font.render(f"Player X: {self.scores[1]}  |  Player O: {self.scores[2]}", True, TEXT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 70))
        
        # Draw board
        board_width = BOARD_SIZE * CELL_SIZE
        board_height = BOARD_SIZE * CELL_SIZE
        board_x = (SCREEN_WIDTH - board_width) // 2
        board_y = (SCREEN_HEIGHT - board_height) // 2 + 20
        
        # Draw grid
        for i in range(BOARD_SIZE + 1):
            # Horizontal lines
            pygame.draw.line(
                self.screen, 
                GRID_COLOR, 
                (board_x, board_y + i * CELL_SIZE), 
                (board_x + board_width, board_y + i * CELL_SIZE), 
                5
            )
            # Vertical lines
            pygame.draw.line(
                self.screen, 
                GRID_COLOR, 
                (board_x + i * CELL_SIZE, board_y), 
                (board_x + i * CELL_SIZE, board_y + board_height), 
                5
            )
        
        # Draw X's and O's with animation
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell_x = board_x + j * CELL_SIZE
                cell_y = board_y + i * CELL_SIZE
                
                if self.board[i][j] == 1:  # Player X
                    color = X_COLOR
                    # Draw X with animation if it's the last move
                    if (i, j) == self.last_move and self.animation_progress < 100:
                        progress = self.animation_progress / 100
                        offset = CELL_SIZE // 2 * progress
                        
                        pygame.draw.line(
                            self.screen, color,
                            (cell_x + CELL_SIZE//2 - offset, cell_y + CELL_SIZE//2 - offset),
                            (cell_x + CELL_SIZE//2 + offset, cell_y + CELL_SIZE//2 + offset),
                            10
                        )
                        pygame.draw.line(
                            self.screen, color,
                            (cell_x + CELL_SIZE//2 + offset, cell_y + CELL_SIZE//2 - offset),
                            (cell_x + CELL_SIZE//2 - offset, cell_y + CELL_SIZE//2 + offset),
                            10
                        )
                    else:
                        pygame.draw.line(
                            self.screen, color,
                            (cell_x + 20, cell_y + 20),
                            (cell_x + CELL_SIZE - 20, cell_y + CELL_SIZE - 20),
                            10
                        )
                        pygame.draw.line(
                            self.screen, color,
                            (cell_x + CELL_SIZE - 20, cell_y + 20),
                            (cell_x + 20, cell_y + CELL_SIZE - 20),
                            10
                        )
                
                elif self.board[i][j] == 2:  # Player O
                    color = O_COLOR
                    # Draw O with animation if it's the last move
                    if (i, j) == self.last_move and self.animation_progress < 100:
                        progress = self.animation_progress / 100
                        radius = int((CELL_SIZE // 2 - 20) * progress)
                        pygame.draw.circle(
                            self.screen, color,
                            (cell_x + CELL_SIZE // 2, cell_y + CELL_SIZE // 2),
                            radius, 10
                        )
                    else:
                        pygame.draw.circle(
                            self.screen, color,
                            (cell_x + CELL_SIZE // 2, cell_y + CELL_SIZE // 2),
                            CELL_SIZE // 2 - 20, 10
                        )
        
        # Highlight winning cells
        for (i, j) in self.winning_cells:
            pygame.draw.rect(
                self.screen, (255, 255, 0, 100),
                (board_x + j * CELL_SIZE + 5, board_y + i * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10),
                5
            )
        
        # Draw status message
        if self.game_over:
            if self.winner:
                message = f"Player {self.player_symbols[self.winner]} wins!"
                color = X_COLOR if self.winner == 1 else O_COLOR
            else:
                message = "Game ended in a draw!"
                color = TEXT_COLOR
        else:
            message = f"Player {self.player_symbols[self.current_player]}'s turn"
            color = X_COLOR if self.current_player == 1 else O_COLOR
        
        status = self.font.render(message, True, color)
        self.screen.blit(status, (SCREEN_WIDTH // 2 - status.get_width() // 2, board_y + board_height + 30))
        
        # Draw game mode info
        mode_text = f"Mode: {'PvP' if self.game_mode == GameMode.PVP else 'PvC'}"
        if self.game_mode == GameMode.PVC:
            mode_text += f" | AI Difficulty: {self.difficulty.name}"
        mode = self.small_font.render(mode_text, True, TEXT_COLOR)
        self.screen.blit(mode, (SCREEN_WIDTH // 2 - mode.get_width() // 2, board_y + board_height + 80))

    def draw_buttons(self):
        # Reset button
        self.reset_button = pygame.Rect(50, SCREEN_HEIGHT - 60, 120, 40)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.reset_button, border_radius=5)
        reset_text = self.small_font.render("New Game", True, TEXT_COLOR)
        self.screen.blit(reset_text, (self.reset_button.x + 20, self.reset_button.y + 10))
        
        # Undo button
        self.undo_button = pygame.Rect(190, SCREEN_HEIGHT - 60, 80, 40)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.undo_button, border_radius=5)
        undo_text = self.small_font.render("Undo", True, TEXT_COLOR)
        self.screen.blit(undo_text, (self.undo_button.x + 15, self.undo_button.y + 10))
        
        # Redo button
        self.redo_button = pygame.Rect(290, SCREEN_HEIGHT - 60, 80, 40)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.redo_button, border_radius=5)
        redo_text = self.small_font.render("Redo", True, TEXT_COLOR)
        self.screen.blit(redo_text, (self.redo_button.x + 15, self.redo_button.y + 10))
        
        # Mode button
        self.mode_button = pygame.Rect(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 60, 170, 40)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.mode_button, border_radius=5)
        mode_text = self.small_font.render(
            "Mode: PvP" if self.game_mode == GameMode.PVP else "Mode: PvC", 
            True, TEXT_COLOR
        )
        self.screen.blit(mode_text, (self.mode_button.x + 15, self.mode_button.y + 10))
        
        # Difficulty button (only visible in PVC mode)
        if self.game_mode == GameMode.PVC:
            self.diff_button = pygame.Rect(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 110, 170, 40)
            pygame.draw.rect(self.screen, BUTTON_COLOR, self.diff_button, border_radius=5)
            diff_text = self.small_font.render(
                f"Difficulty: {self.difficulty.name}", 
                True, TEXT_COLOR
            )
            self.screen.blit(diff_text, (self.diff_button.x + 10, self.diff_button.y + 10))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Handle board clicks
                    if not self.game_over and (
                        (self.current_player == 1 and self.player1_type == Player.HUMAN) or
                        (self.current_player == 2 and self.player2_type == Player.HUMAN)
                    ):
                        board_x = (SCREEN_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
                        board_y = (SCREEN_HEIGHT - BOARD_SIZE * CELL_SIZE) // 2 + 20
                        
                        for i in range(BOARD_SIZE):
                            for j in range(BOARD_SIZE):
                                cell_rect = pygame.Rect(
                                    board_x + j * CELL_SIZE,
                                    board_y + i * CELL_SIZE,
                                    CELL_SIZE, CELL_SIZE
                                )
                                if cell_rect.collidepoint(mouse_pos):
                                    if self.make_move(i, j):
                                        self.animation_progress = 0
                    
                    # Handle button clicks
                    if self.reset_button.collidepoint(mouse_pos):
                        self.reset_game()
                    
                    if self.undo_button.collidepoint(mouse_pos):
                        self.undo_move()
                    
                    if self.redo_button.collidepoint(mouse_pos):
                        self.redo_move()
                    
                    if self.mode_button.collidepoint(mouse_pos):
                        self.game_mode = GameMode.PVP if self.game_mode == GameMode.PVC else GameMode.PVC
                        if self.game_mode == GameMode.PVP:
                            self.player1_type = Player.HUMAN
                            self.player2_type = Player.HUMAN
                        else:
                            self.player1_type = Player.HUMAN
                            self.player2_type = Player.AI
                        self.reset_game()
                    
                    if self.game_mode == GameMode.PVC and self.diff_button.collidepoint(mouse_pos):
                        if self.difficulty == Difficulty.EASY:
                            self.difficulty = Difficulty.MEDIUM
                        elif self.difficulty == Difficulty.MEDIUM:
                            self.difficulty = Difficulty.HARD
                        else:
                            self.difficulty = Difficulty.EASY
                        self.reset_game()
            
            # AI move
            if not self.game_over:
                if (self.current_player == 1 and self.player1_type == Player.AI) or \
                   (self.current_player == 2 and self.player2_type == Player.AI):
                    row, col = self.get_ai_move()
                    if row is not None:
                        self.make_move(row, col)
                        self.animation_progress = 0
            
            # Update animation
            if self.animation_progress < 100:
                self.animation_progress = min(self.animation_progress + ANIMATION_SPEED, 100)
            
            # Draw everything
            self.screen.fill(BG_COLOR)
            self.draw_board()
            self.draw_buttons()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = TicTacToe()
    game.run()