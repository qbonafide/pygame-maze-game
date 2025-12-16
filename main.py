# Main game loop and entry point for Pygame Maze Game with difficulty selection and scoring system.
import pygame
import sys
from typing import Tuple
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS,
    MAZE_WIDTH, MAZE_HEIGHT, PLAYER_START_X, PLAYER_START_Y,
    VISION_RANGE, EXIT_X, EXIT_Y,
    COLOR_BLACK, COLOR_WHITE, COLOR_DARK_GRAY, COLOR_LIGHT_GRAY, COLOR_YELLOW, COLOR_GREEN, COLOR_RED,
    DIFFICULTY_SETTINGS, PATHFINDING_ALGORITHMS, INITIAL_SCORE
)
from src.maze import Maze
from src.player import Player
from src.enemy import Enemy
from src.camera import Camera


class GameState:
    # Enum-like class for game states.
    DIFFICULTY_SELECT = "difficulty_select"
    ALGORITHM_SELECT = "algorithm_select"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    GAME_WON = "game_won"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Game - Find the Exit!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        
        # Game state
        self.state = GameState.DIFFICULTY_SELECT
        self.difficulty = None
        self.algorithm = None
        self.selected_difficulty_index = 0
        self.selected_algorithm_index = 0
        
        # Game components (initialized after difficulty selection)
        self.maze = None
        self.player = None
        self.camera = None
        self.brick_texture = None
        self.path_texture = None
        self.enemies = []
        
        # Game progress tracking
        self.score = INITIAL_SCORE
        self.moves_made = 0
        self.enemies_killed = 0
        self.hits_used = 0
        self.max_hits_allowed = 0
        self.running = True
        self.game_won = False
        self.game_over = False
        self.game_over_reason = ""
    
    def _initialize_game(self) -> None:
        # Initialize game components
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.player = Player(PLAYER_START_X, PLAYER_START_Y, TILE_SIZE)
        self.camera = Camera(VISION_RANGE, MAZE_WIDTH, MAZE_HEIGHT)
        
        # Load textures
        self.brick_texture = self._load_brick_texture()
        self.path_texture = self._load_path_texture()
        
        # Initialize enemies with difficulty settings
        self.enemies = self._spawn_enemies()
        
        # Ensure exit is a path
        self.maze.grid[EXIT_Y][EXIT_X] = 0
        
        # Initialize score and hit tracking
        self.score = INITIAL_SCORE
        self.moves_made = 0
        self.enemies_killed = 0
        self.hits_used = 0
        
        # Set max hits allowed based on difficulty
        difficulty_config = DIFFICULTY_SETTINGS[self.difficulty]
        self.max_hits_allowed = difficulty_config["max_hits"]
    
    def _spawn_enemies(self) -> list:
        # Spawn enemies based on difficulty settings
        enemies = []
        difficulty_config = DIFFICULTY_SETTINGS[self.difficulty]
        enemy_count = difficulty_config["enemy_count"]
        enemy_speed = difficulty_config["enemy_speed"]
        max_hits = difficulty_config["max_hits"]
        
        for i in range(enemy_count):
            while True:
                import random
                x = random.randint(5, MAZE_WIDTH - 5)
                y = random.randint(5, MAZE_HEIGHT - 5)
                
                if self.maze.is_path(x, y) and (x, y) != (PLAYER_START_X, PLAYER_START_Y):
                    enemy = Enemy(x, y, TILE_SIZE, move_delay=enemy_speed,
                                max_hits=max_hits, algorithm=self.algorithm)
                    enemy.set_maze(self.maze)
                    enemies.append(enemy)
                    print(f"Enemy {i+1} spawned at ({x}, {y}) - Algorithm: {self.algorithm}")
                    break
        
        return enemies
    
    def _get_random_spawn_location(self) -> Tuple[int, int]:
        # Get random valid spawn location for enemy respawn
        import random
        
        while True:
            x = random. randint(5, MAZE_WIDTH - 5)
            y = random.randint(5, MAZE_HEIGHT - 5)
            
            player_x, player_y = self.player.get_position()
            
            # Make sure spawn is far from player (at least 10 tiles away)
            distance = abs(x - player_x) + abs(y - player_y)
            
            if self.maze.is_path(x, y) and distance >= 10:
                return (x, y)
    
    def _load_brick_texture(self) -> pygame.Surface:
        # Load brick texture from file
        try:
            brick_texture = pygame.image.load("assets/textures/brick.png")
            brick_texture = pygame.transform.scale(brick_texture, (TILE_SIZE, TILE_SIZE))
            print("Brick texture loaded successfully!")
            return brick_texture
        except pygame.error as e:
            print(f"Warning: Could not load brick texture: {e}")
            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback.fill(COLOR_DARK_GRAY)
            return fallback
    
    def _load_path_texture(self) -> pygame.Surface:
        # Load path texture from file
        try:
            path_texture = pygame.image.load("assets/textures/background.png")
            path_texture = pygame.transform.scale(path_texture, (TILE_SIZE, TILE_SIZE))
            print("Path texture loaded successfully!")
            return path_texture
        except pygame.error as e:
            print(f"Warning: Could not load path texture: {e}")
            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback.fill(COLOR_WHITE)
            return fallback
    
    def handle_input(self) -> None:
        # Handle player input and events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.DIFFICULTY_SELECT
                    else:
                        self.running = False
                elif self.state == GameState.DIFFICULTY_SELECT:
                    self._handle_difficulty_input(event)
                elif self.state == GameState.ALGORITHM_SELECT:
                    self._handle_algorithm_input(event)
                elif self.state == GameState.PLAYING:
                    self._handle_gameplay_input(event)
                elif self.state in (GameState.GAME_OVER, GameState.GAME_WON):
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.DIFFICULTY_SELECT
    
    def _handle_difficulty_input(self, event) -> None:
        # Handle input for difficulty selection
        difficulties = list(DIFFICULTY_SETTINGS.keys())
        
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            self.selected_difficulty_index = (self.selected_difficulty_index - 1) % len(difficulties)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.selected_difficulty_index = (self.selected_difficulty_index + 1) % len(difficulties)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self.difficulty = difficulties[self.selected_difficulty_index]
            self.state = GameState.ALGORITHM_SELECT
            self.selected_algorithm_index = 0
    
    def _handle_algorithm_input(self, event) -> None:
        # Handle input for algorithm selection
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            self.selected_algorithm_index = (self.selected_algorithm_index - 1) % len(PATHFINDING_ALGORITHMS)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.selected_algorithm_index = (self.selected_algorithm_index + 1) % len(PATHFINDING_ALGORITHMS)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self.algorithm = PATHFINDING_ALGORITHMS[self.selected_algorithm_index]
            self._initialize_game()
            self.state = GameState.PLAYING
    
    def _handle_gameplay_input(self, event) -> None:
        # Handle input during gameplay
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            if self.player.move(0, -1, self.maze):
                self.moves_made += 1
                self.score = max(0, self.score - 1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            if self.player.move(0, 1, self.maze):
                self.moves_made += 1
                self.score = max(0, self.score - 1)
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            if self.player.move(-1, 0, self.maze):
                self.moves_made += 1
                self.score = max(0, self.score - 1)
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            if self.player.move(1, 0, self.maze):
                self.moves_made += 1
                self.score = max(0, self.score - 1)
        elif event.key == pygame.K_SPACE:
            self._try_hit_enemy()
    
    def _try_hit_enemy(self) -> None:
        """
        Try to hit an enemy adjacent to player.
        Hit works on enemies 1 tile away in any direction.
        """

        # Check if player has remaining hits
        if self.hits_used >= self.max_hits_allowed:
            print(f"Out of hits! You've used {self.hits_used}/{self.max_hits_allowed} hits")
            return
        
        player_x, player_y = self.player.get_position()
        
        # Check all 4 adjacent positions
        adjacent_positions = [
            (player_x, player_y - 1),  # Up
            (player_x, player_y + 1),  # Down
            (player_x - 1, player_y),  # Left
            (player_x + 1, player_y),  # Right
        ]
        
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            
            enemy_pos = enemy.get_position()
            
            # Check if enemy is adjacent to player
            if enemy_pos in adjacent_positions:
                # hit() method returns True if enemy is hit
                if enemy.hit():
                    self.hits_used += 1
                    if not enemy.is_alive:
                        self.enemies_killed += 1
                        print(f"✓ Enemy defeated!  Hits used: {self.hits_used}/{self.max_hits_allowed}")
                break
    
    def update(self) -> None:
        # Update game logic
        if self.state != GameState.PLAYING:
            return
        
        if self.game_over or self.game_won:
            return
        
        player_x, player_y = self.player.get_position()
        
        # Update all enemies
        for enemy in self.enemies:
            if not enemy.is_alive:
                # Check if hit animation finished
                if enemy.is_hit_animation_finished():
                    # Respawn enemy
                    new_x, new_y = self._get_random_spawn_location()
                    enemy.reset_position(new_x, new_y)
                    print(f"Enemy respawned at ({new_x}, {new_y})")
                continue
            
            enemy.update(player_x, player_y, self.maze)
            
            # Check collision with player
            if enemy.get_position() == (player_x, player_y):
                self.game_over = True
                self.game_over_reason = "CAUGHT BY ENEMY!"
                self.state = GameState.GAME_OVER
                return
        
        # Check win condition
        if self.player.get_position() == (EXIT_X, EXIT_Y):
            self.game_won = True
            self._calculate_final_score()
            self.state = GameState.GAME_WON
    
    def _calculate_final_score(self) -> None:
        # Calculate final score when reaching the exit
        difficulty_config = DIFFICULTY_SETTINGS[self.difficulty]
        hit_to_score = difficulty_config["hit_to_score_multiplier"]
        
        # Calculate remaining hits converted to score
        remaining_hits = self.max_hits_allowed - self.hits_used
        bonus_score = max(0, remaining_hits) * hit_to_score
        
        self.score += bonus_score
        
        # Ensure final score tidak minus
        self.score = max(0, self.score)
        
        print(f"\nFINAL SCORE CALCULATION:")
        print(f"Base Score: {INITIAL_SCORE}")
        print(f"Score Lost (Movement): -{self.moves_made}")
        print(f"Remaining Hits Bonus: +{bonus_score} ({remaining_hits} hits × {hit_to_score} points)")
        print(f"FINAL SCORE: {self.score}")
    
    def _get_total_remaining_hits(self) -> int:
        # Calculate remaining hits player can use
        return self.max_hits_allowed - self.hits_used
    
    def render(self) -> None:
        # Render the game
        self.screen.fill(COLOR_BLACK)
        
        if self.state == GameState.DIFFICULTY_SELECT:
            self._render_difficulty_select()
        elif self.state == GameState.ALGORITHM_SELECT:
            self._render_algorithm_select()
        elif self.state == GameState.PLAYING:
            self._render_gameplay()
        elif self.state == GameState. GAME_OVER:
            self._render_game_over()
        elif self.state == GameState.GAME_WON:
            self._render_game_won()
        
        pygame. display.flip()
    
    def _render_difficulty_select(self) -> None:
        # Render difficulty selection screen
        title = self.title_font.render("SELECT DIFFICULTY", True, COLOR_GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen. blit(title, title_rect)
        
        difficulties = list(DIFFICULTY_SETTINGS.keys())
        y_offset = 150
        
        for i, difficulty in enumerate(difficulties):
            config = DIFFICULTY_SETTINGS[difficulty]
            is_selected = i == self.selected_difficulty_index
            
            color = COLOR_YELLOW if is_selected else COLOR_WHITE
            prefix = ">>> " if is_selected else "    "
            
            difficulty_text = f"{prefix}{difficulty. upper()}"
            text = self.font.render(difficulty_text, True, color)
            self.screen.blit(text, (50, y_offset))
            
            # Show difficulty info
            info = f"Enemies: {config['enemy_count']} | Speed: {config['enemy_speed']} | Max Hits: {config['max_hits']}"
            info_text = self.small_font.render(info, True, COLOR_LIGHT_GRAY)
            self. screen.blit(info_text, (100, y_offset + 40))
            
            y_offset += 100
        
        # Instructions
        instructions = self.small_font.render("UP/DOWN: Navigate | SPACE/ENTER: Select | ESC: Quit", True, COLOR_WHITE)
        self.screen.blit(instructions, (10, SCREEN_HEIGHT - 30))
    
    def _render_algorithm_select(self) -> None:
        # Render algorithm selection screen
        title = self.title_font.render(f"SELECT ALGORITHM", True, COLOR_GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font.render(f"Difficulty: {self.difficulty.upper()}", True, COLOR_YELLOW)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(subtitle, subtitle_rect)
        
        y_offset = 200
        
        for i, algorithm in enumerate(PATHFINDING_ALGORITHMS):
            is_selected = i == self.selected_algorithm_index
            
            color = COLOR_YELLOW if is_selected else COLOR_WHITE
            prefix = ">>> " if is_selected else "    "
            
            algorithm_text = f"{prefix}{algorithm}"
            text = self.font. render(algorithm_text, True, color)
            self.screen. blit(text, (100, y_offset))
            
            y_offset += 80
        
        # Instructions
        instructions = self.small_font. render("UP/DOWN: Navigate | SPACE/ENTER: Select | ESC: Back", True, COLOR_WHITE)
        self.screen.blit(instructions, (10, SCREEN_HEIGHT - 30))
    
    def _render_gameplay(self) -> None:
        # Get visible tiles from player's torch
        visible_tiles = self.camera.get_visible_tiles(self.player.x, self.player.y)
        
        # Draw maze - only visible tiles
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if (x, y) in visible_tiles:
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    
                    if self.maze. is_wall(x, y):
                        self.screen.blit(self.brick_texture, tile_rect)
                    else:
                        self.screen.blit(self. path_texture, tile_rect)
                        pygame.draw.rect(self.screen, (100, 100, 100), tile_rect, 1)
        
        # Draw exit marker (if visible)
        if (EXIT_X, EXIT_Y) in visible_tiles:
            exit_rect = pygame.Rect(EXIT_X * TILE_SIZE, EXIT_Y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame. draw.rect(self.screen, COLOR_GREEN, exit_rect)
            exit_text = self.small_font.render("EXIT", True, (0, 0, 0))
            text_rect = exit_text.get_rect(center=exit_rect.center)
            self.screen.blit(exit_text, text_rect)
        
        # Draw enemies (if visible)
        for enemy in self.enemies:
            enemy_x, enemy_y = enemy.get_position()
            if (enemy_x, enemy_y) in visible_tiles:
                enemy. render(self.screen, TILE_SIZE)
        
        # Draw player sprite
        player_sprite = self.player.get_sprite()
        player_rect = pygame.Rect(self.player.x * TILE_SIZE, self.player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.screen.blit(player_sprite, player_rect)
        
        # Draw UI
        hint_text = self.small_font.render("WASD/Arrows: Move | SPACE: Hit Enemy | ESC: Back to Menu", True, COLOR_WHITE)
        self.screen.blit(hint_text, (10, SCREEN_HEIGHT - 30))
        
        # Score display
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_YELLOW)
        self.screen.blit(score_text, (10, 10))
        
        # Difficulty display
        difficulty_text = self.small_font.render(f"Difficulty: {self.difficulty. upper()} | Algorithm: {self.algorithm}",True, COLOR_LIGHT_GRAY)
        self.screen.blit(difficulty_text, (10, 50))
        
        # Remaining hits counter
        remaining_hits = self._get_total_remaining_hits()
        hits_text = self.small_font.render(f"Remaining Hits: {remaining_hits}/{self.max_hits_allowed}", True, (255, 100, 100))
        self.screen.blit(hits_text, (10, 80))
    
    def _render_game_over(self) -> None:
        """Render game over screen."""
        over_text = self.title_font.render("YOU LOSE", True, COLOR_RED)
        over_rect = over_text. get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(over_text, over_rect)
        
        reason_text = self.font.render(self.game_over_reason, True, (255, 100, 100))
        reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(reason_text, reason_rect)
        
        exit_text = self.small_font.render("Press ESC to return to menu", True, COLOR_WHITE)
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        self.screen.blit(exit_text, exit_rect)
    
    def _render_game_won(self) -> None:
        """Render game won screen."""
        win_text = self.title_font.render("YOU WIN!", True, COLOR_GREEN)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(win_text, win_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(score_text, score_rect)
        
        kills_text = self.small_font.render(f"Enemies Defeated: {self.enemies_killed}", True, (255, 100, 100))
        kills_rect = kills_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(kills_text, kills_rect)
        
        exit_text = self.small_font.render("Press ESC to return to menu", True, COLOR_WHITE)
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(exit_text, exit_rect)
    
    def run(self) -> None:
        # Main game loop
        print("=" * 60)
        print("PYGAME MAZE GAME")
        print("=" * 60)
        print("Features:")
        print("  • Difficulty Selection (Easy, Medium, Hard)")
        print("  • Multiple Pathfinding Algorithms (A*, BFS, DFS)")
        print("  • Limited Hits System (varies by difficulty)")
        print("  • Scoring System (Base 100 - Movement - Hit Bonus)")
        print("=" * 60)
        
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        print("\nThanks for playing!")
        pygame.quit()
        sys.exit()


def main():
    # Entry point for the game
    game = Game()
    game.run()


if __name__ == "__main__":
    main()