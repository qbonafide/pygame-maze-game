"""
Main game loop and entry point for Pygame Maze Game. 
"""
import pygame
import sys
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS,
    MAZE_WIDTH, MAZE_HEIGHT, PLAYER_START_X, PLAYER_START_Y,
    VISION_RANGE, EXIT_X, EXIT_Y,
    COLOR_BLACK, COLOR_WHITE, COLOR_DARK_GRAY, COLOR_YELLOW, COLOR_GREEN
)
from src.maze import Maze
from src.player import Player
from src.camera import Camera


class Game:
    """Main game class handling the game loop and logic."""
    
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display. set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🔦 Maze Game - Find the Exit!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self. small_font = pygame.font.Font(None, 24)
        
        # Initialize game components
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.player = Player(PLAYER_START_X, PLAYER_START_Y, TILE_SIZE)
        self.camera = Camera(VISION_RANGE, MAZE_WIDTH, MAZE_HEIGHT)
        
        # Load textures
        self.brick_texture = self._load_brick_texture()
        self.path_texture = self._load_path_texture()
        
        # Game state
        self.running = True
        self.game_won = False
        
        # Ensure exit is a path
        self.maze.grid[EXIT_Y][EXIT_X] = 0
    
    def _load_brick_texture(self) -> pygame.Surface:
        """
        Load brick texture from file. 
        Falls back to solid color if texture not found.
        
        Returns:
            Brick texture surface
        """
        try:
            brick_texture = pygame.image.load("assets/textures/brick.png")
            brick_texture = pygame.transform.scale(brick_texture, (TILE_SIZE, TILE_SIZE))
            print("✓ Brick texture loaded successfully!")
            return brick_texture
        except pygame.error as e:
            print(f"⚠ Warning: Could not load brick texture: {e}")
            print("  Using solid color fallback for walls")
            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback.fill(COLOR_DARK_GRAY)
            return fallback
    
    def _load_path_texture(self) -> pygame.Surface:
        """
        Load path texture from file. 
        Falls back to solid white color if texture not found.
        
        Returns:
            Path texture surface
        """
        try:
            path_texture = pygame.image.load("assets/textures/background.png")
            path_texture = pygame.transform.scale(path_texture, (TILE_SIZE, TILE_SIZE))
            print("✓ Path texture loaded successfully!")
            return path_texture
        except pygame.error as e:
            print(f"⚠ Warning: Could not load path texture: {e}")
            print("  Using solid color fallback for paths")
            fallback = pygame. Surface((TILE_SIZE, TILE_SIZE))
            fallback.fill(COLOR_WHITE)
            return fallback
    
    def handle_input(self) -> None:
        """Handle player input and events (turn-based movement)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self. running = False
            elif event. type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Turn-based movement: 1 key press = 1 move
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.move(0, -1, self.maze)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self. player.move(0, 1, self.maze)
                elif event.key == pygame.K_LEFT or event.key == pygame. K_a:
                    self.player.move(-1, 0, self.maze)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.move(1, 0, self.maze)
    
    def update(self) -> None:
        """Update game logic."""
        # Check win condition
        if self.player.get_position() == (EXIT_X, EXIT_Y):
            self.game_won = True
    
    def render(self) -> None:
        """Render the game."""
        # Start with black background (fog of war)
        self.screen. fill(COLOR_BLACK)
        
        # Get visible tiles from player's torch
        visible_tiles = self. camera.get_visible_tiles(self.player.x, self.player.y)
        
        # Draw maze - ONLY visible tiles
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                # Only render tiles that are actually visible
                if (x, y) in visible_tiles:
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    
                    # Draw visible tiles
                    if self.maze.is_wall(x, y):
                        # Draw brick texture for walls
                        self.screen.blit(self. brick_texture, tile_rect)
                    else:
                        # Draw path texture (your background. png)
                        self.screen.blit(self.path_texture, tile_rect)
                        # Draw borders for grid
                        pygame.draw.rect(self.screen, (100, 100, 100), tile_rect, 1)
        
        # Draw exit marker (if visible)
        if (EXIT_X, EXIT_Y) in visible_tiles:
            exit_rect = pygame.Rect(EXIT_X * TILE_SIZE, EXIT_Y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame. draw.rect(self.screen, COLOR_GREEN, exit_rect)
            exit_text = self.small_font.render("EXIT", True, (0, 0, 0))
            text_rect = exit_text.get_rect(center=exit_rect.center)
            self.screen.blit(exit_text, text_rect)
        
        # Draw player sprite
        player_sprite = self.player.get_sprite()
        player_rect = pygame.Rect(self.player.x * TILE_SIZE, self.player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.screen.blit(player_sprite, player_rect)
        
        # Draw UI - Only show controls hint
        if not self.game_won:
            hint_text = self.small_font.render("Arrow Keys / WASD to move | ESC to quit", True, COLOR_WHITE)
            self.screen.blit(hint_text, (10, SCREEN_HEIGHT - 30))
        else:
            # Win screen
            win_text = self. font.render("🎉 YOU WIN! 🎉", True, COLOR_GREEN)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(win_text, win_rect)
            
            exit_text = self.small_font.render("Press ESC to exit", True, COLOR_WHITE)
            exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(exit_text, exit_rect)
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop."""
        print("=" * 50)
        print("🎮 MAZE GAME STARTED!")
        print("=" * 50)
        print("🕯️  You have a torch that illuminates 2 tiles in all directions")
        print("🎯 Goal: Navigate through the maze and find the EXIT (green tile)")
        print("🕹️  Controls:")
        print("   - Arrow Keys or WASD: Move (1 block per keypress)")
        print("   - ESC: Quit game")
        print("=" * 50)
        
        while self.running:
            self. handle_input()
            self. update()
            self.render()
            self.clock.tick(FPS)
        
        print("Thanks for playing! 👋")
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()