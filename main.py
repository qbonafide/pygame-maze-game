"""
Main game loop and entry point for Pygame Maze Game. 
"""
import pygame
import sys
from typing import Tuple
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS,
    MAZE_WIDTH, MAZE_HEIGHT, PLAYER_START_X, PLAYER_START_Y,
    VISION_RANGE, EXIT_X, EXIT_Y,
    COLOR_BLACK, COLOR_WHITE, COLOR_DARK_GRAY, COLOR_YELLOW, COLOR_GREEN
)
from src.maze import Maze
from src.player import Player
from src.enemy import Enemy
from src.camera import Camera


class Game:
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🔦 Maze Game - Find the Exit!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize game components
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.player = Player(PLAYER_START_X, PLAYER_START_Y, TILE_SIZE)
        self.camera = Camera(VISION_RANGE, MAZE_WIDTH, MAZE_HEIGHT)
        
        # Load textures
        self.brick_texture = self._load_brick_texture()
        self.path_texture = self._load_path_texture()
        
        # Initialize enemies
        self.enemies = self._spawn_enemies()
        
        # Game state
        self.running = True
        self.game_won = False
        self.game_over = False
        self.game_over_reason = ""
        self.enemies_killed = 0
        
        # Ensure exit is a path
        self.maze.grid[EXIT_Y][EXIT_X] = 0
    
    def _spawn_enemies(self) -> list:
        """Spawn enemies at random locations far from player."""
        enemies = []
        spawn_count = 2
        speeds = [1.0] * spawn_count
        
        for i, speed in enumerate(speeds):
            while True:
                import random
                x = random.randint(5, MAZE_WIDTH - 5)
                y = random.randint(5, MAZE_HEIGHT - 5)
                
                if self.maze.is_path(x, y) and (x, y) != (PLAYER_START_X, PLAYER_START_Y):
                    enemy = Enemy(x, y, TILE_SIZE, move_delay=speed)
                    enemy.set_maze(self.maze)
                    enemies.append(enemy)
                    print(f"✓ Enemy {i+1} spawned at ({x}, {y})")
                    break
        
        return enemies
    
    def _get_random_spawn_location(self) -> Tuple[int, int]:
        """Get random valid spawn location for enemy respawn."""
        import random
        
        while True:
            x = random.  randint(5, MAZE_WIDTH - 5)
            y = random.randint(5, MAZE_HEIGHT - 5)
            
            player_x, player_y = self.player.get_position()
            
            # Make sure spawn is far from player (at least 5 tiles away)
            distance = abs(x - player_x) + abs(y - player_y)
            
            if self.maze.is_path(x, y) and distance >= 5:
                return (x, y)
    
    def _load_brick_texture(self) -> pygame.Surface:
        """Load brick texture from file."""
        try:
            brick_texture = pygame.image.load("assets/textures/brick.png")
            brick_texture = pygame.  transform.scale(brick_texture, (TILE_SIZE, TILE_SIZE))
            print("✓ Brick texture loaded successfully!")
            return brick_texture
        except pygame.error as e:
            print(f"⚠ Warning: Could not load brick texture: {e}")
            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback.fill(COLOR_DARK_GRAY)
            return fallback
    
    def _load_path_texture(self) -> pygame.Surface:
        """Load path texture from file."""
        try:
            path_texture = pygame.image.load("assets/textures/background.png")
            path_texture = pygame. transform. scale(path_texture, (TILE_SIZE, TILE_SIZE))
            print("✓ Path texture loaded successfully!")
            return path_texture
        except pygame. error as e:
            print(f"⚠ Warning: Could not load path texture: {e}")
            fallback = pygame. Surface((TILE_SIZE, TILE_SIZE))
            fallback.fill(COLOR_WHITE)
            return fallback
    
    def handle_input(self) -> None:
        """Handle player input and events."""
        for event in pygame.  event.get():
            if event. type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.  KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Movement
                elif event.key == pygame.  K_UP or event. key == pygame.K_w:
                    self.player.move(0, -1, self.maze)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.  player.move(0, 1, self.maze)
                elif event.key == pygame.K_LEFT or event.key == pygame.  K_a:
                    self.player.move(-1, 0, self.maze)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.move(1, 0, self.maze)
                # Hit enemy with SPACE
                elif event.key == pygame.K_SPACE:
                    self._try_hit_enemy()
    
    def _try_hit_enemy(self) -> None:
        """
        Try to hit an enemy adjacent to player.
        Hit works on enemies 1 tile away in any direction.
        """
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
                enemy.hit()
                print(f"💥 Hit enemy at {enemy_pos}!")
                self.enemies_killed += 1
                break
    
    def update(self) -> None:
        """Update game logic."""
        if self.game_over or self.game_won:
            return
        
        player_x, player_y = self.player.get_position()
        
        # Update all enemies
        for enemy in self.  enemies:
            if not enemy.is_alive:
                # Check if hit animation finished
                if enemy.is_hit_animation_finished():
                    # Respawn enemy
                    new_x, new_y = self._get_random_spawn_location()
                    enemy.reset_position(new_x, new_y)
                    print(f"✓ Enemy respawned at ({new_x}, {new_y})")
                continue
            
            enemy.update(player_x, player_y, self.maze)
            
            # Check collision with player
            if enemy.get_position() == (player_x, player_y):
                self.game_over = True
                self.game_over_reason = "CAUGHT BY ENEMY!"
                return
        
        # Check win condition
        if self.player.get_position() == (EXIT_X, EXIT_Y):
            self.game_won = True
    
    def render(self) -> None:
        """Render the game."""
        self.screen.  fill(COLOR_BLACK)
        
        # Get visible tiles from player's torch
        visible_tiles = self.camera.get_visible_tiles(self.player.x, self.player.y)
        
        # Draw maze - ONLY visible tiles
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if (x, y) in visible_tiles:
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    
                    if self.maze.is_wall(x, y):
                        self.screen.blit(self.  brick_texture, tile_rect)
                    else:
                        self.screen. blit(self.  path_texture, tile_rect)
                        pygame.draw.rect(self.screen, (100, 100, 100), tile_rect, 1)
        
        # Draw exit marker (if visible)
        if (EXIT_X, EXIT_Y) in visible_tiles:
            exit_rect = pygame.Rect(EXIT_X * TILE_SIZE, EXIT_Y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.  draw.rect(self.screen, COLOR_GREEN, exit_rect)
            exit_text = self.small_font.render("EXIT", True, (0, 0, 0))
            text_rect = exit_text.get_rect(center=exit_rect.center)
            self.screen.blit(exit_text, text_rect)
        
        # Draw enemies (if visible)
        for enemy in self.  enemies:
            enemy_x, enemy_y = enemy.get_position()
            if (enemy_x, enemy_y) in visible_tiles:
                enemy.  render(self.screen, TILE_SIZE)
        
        # Draw player sprite
        player_sprite = self.player.get_sprite()
        player_rect = pygame.Rect(self.player.x * TILE_SIZE, self.player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.screen.blit(player_sprite, player_rect)
        
        # Draw UI
        if not self.game_won and not self.game_over:
            hint_text = self.small_font.render("WASD/Arrows: Move | SPACE: Hit Enemy | ESC: Quit", True, COLOR_WHITE)
            self.screen.blit(hint_text, (10, SCREEN_HEIGHT - 30))
            
            # Kill counter
            kills_text = self.small_font.render(f"Enemies Defeated: {self.enemies_killed}", True, (255, 100, 100))
            self.  screen.blit(kills_text, (10, 10))
        elif self.game_over:
            # Game over screen
            over_text = self.font.render("💀 GAME OVER 💀", True, (255, 0, 0))
            over_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(over_text, over_rect)
            
            reason_text = self.small_font.render(self.game_over_reason, True, (255, 100, 100))
            reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(reason_text, reason_rect)
            
            exit_text = self.small_font.render("Press ESC to quit", True, COLOR_WHITE)
            exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(exit_text, exit_rect)
        else:
            # Win screen
            win_text = self.font.  render("🎉 YOU WIN! 🎉", True, COLOR_GREEN)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(win_text, win_rect)
            
            kills_text = self.small_font.render(f"Enemies Defeated: {self.enemies_killed}", True, (255, 100, 100))
            kills_rect = kills_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(kills_text, kills_rect)
            
            exit_text = self.  small_font.render("Press ESC to exit", True, COLOR_WHITE)
            exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(exit_text, exit_rect)
        
        pygame.  display.flip()
    
    def run(self) -> None:
        """Main game loop."""
        print("=" * 50)
        print("🎮 MAZE GAME WITH COMBAT!")
        print("=" * 50)
        print("🕯️  You have a torch that illuminates 2 tiles in all directions")
        print("🤖 2 Intelligent Enemies with A* Pathfinding")
        print("⚔️  Press SPACE to hit adjacent enemies!")
        print("🎯 Goal: Navigate to EXIT or defeat all enemies")
        print("🕹️  Controls:")
        print("   - Arrow Keys or WASD: Move")
        print("   - SPACE: Hit adjacent enemy")
        print("   - ESC: Quit game")
        print("=" * 50)
        
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        print("Thanks for playing! 👋")
        pygame. quit()
        sys.exit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()