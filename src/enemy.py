# Enemy module with multiple pathfinding algorithms, speed control, and hit system.
from typing import Tuple, Optional, List
import pygame
import time
from src.maze import Maze
from src.pathfinding import AStar, BFS, DFS

class Enemy:

    def __init__(self, x: int, y: int, tile_size: int = 32, move_delay: float = 0.5, 
                 max_hits: int = 10, algorithm: str = "A*"):
        """
        Initialize enemy at given position. 
        
            x: Starting X coordinate
            y: Starting Y coordinate
            tile_size: Size of each tile (default 32px)
            move_delay: Seconds between each move
            max_hits: Not used (kept for compatibility)
            algorithm: Pathfinding algorithm ("A*", "BFS", "DFS")
        """
        self.x = x
        self.y = y
        self. tile_size = tile_size
        self.direction = "down"
        self.is_alive = True
        
        # Movement
        self.move_delay = move_delay
        self.last_move_time = time.time()
        
        # Pathfinding
        self.pathfinder: Optional[object] = None
        self.path: List[Tuple[int, int]] = []
        self.path_index = 0
        self.recalc_interval = 1
        self.moves_since_recalc = 0
        self.algorithm = algorithm
        
        # Vision
        self.vision_range = 8
        self.player_detected = False
        
        # Hit animation
        self.hit_animation_time = 0.5  # Show death animation for 0.5 seconds
        self.is_hit = False
        self.hit_start_time = 0
        
        # Sprite
        self.sprite = self._load_sprite()
        self.color = (255, 0, 0)
    
    def _load_sprite(self) -> pygame.Surface:
        try:
            sprite = pygame.image.load("assets/sprites/enemy.png")
            sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
            print("Enemy sprite loaded successfully!")
            return sprite
        except pygame.error as e:
            print(f"Warning: Could not load enemy sprite: {e}")
            fallback = pygame.Surface((self.tile_size, self.tile_size))
            fallback.fill((255, 0, 0))
            pygame.draw.rect(fallback, (255, 255, 255), fallback.get_rect(), 2)
            return fallback
    
    def set_maze(self, maze: Maze) -> None:
        # Set maze and initialize pathfinder based on algorithm.
        if self.algorithm == "A*":
            self.pathfinder = AStar(maze)
        elif self.algorithm == "BFS":
            self.pathfinder = BFS(maze)
        elif self.algorithm == "DFS":
            self.pathfinder = DFS(maze)
        else:
            self.pathfinder = AStar(maze)
    
    def can_see_player(self, player_x: int, player_y: int) -> bool:
        # Check if enemy can see player (within vision range).
        distance = abs(self.x - player_x) + abs(self.y - player_y)
        return distance <= self.vision_range
    
    def _can_move_now(self) -> bool:
        # Check if enough time has passed for next move.
        current_time = time.time()
        if current_time - self. last_move_time >= self.move_delay:
            self.last_move_time = current_time
            return True
        return False
    
    def hit(self) -> bool:
        """
        Register a hit on the enemy.
        Returns True if hit was successful, False if already dead
        """
        if not self.is_alive:
            return False
    
        self.is_alive = False
        self.is_hit = True
        self.hit_start_time = time.time()
        
        print(f"Enemy is dead")
        return True
    
    def is_hit_animation_finished(self) -> bool:
        # Check if hit animation has finished.
        if self.is_hit:
            current_time = time.time()
            if current_time - self. hit_start_time >= self. hit_animation_time:
                self.is_hit = False
                return True
        return False
    
    def reset_position(self, x: int, y: int) -> None:
        # Reset enemy to new position (respawn).
        self.x = x
        self.y = y
        self.is_alive = True
        self.is_hit = False
        self.path = []
        self.path_index = 0
        self.moves_since_recalc = 0
    
    def update(self, player_x: int, player_y: int, maze: Maze) -> None:
        # Update enemy state.
        if not self.is_alive:
            return
        
        # Check if enough time has passed for next move
        if not self._can_move_now():
            return
        
        # Check if player is visible
        self.player_detected = self.can_see_player(player_x, player_y)
        
        if self.player_detected:
            self._chase_player((player_x, player_y), maze)
        else:
            self._patrol(maze)
    
    def _chase_player(self, player_pos: Tuple[int, int], maze: Maze) -> None:
        # Chase player using configured pathfinding algorithm.
        if self.moves_since_recalc >= self.recalc_interval or not self.path:
            if self.pathfinder:
                self.path = self.pathfinder.find_path((self.x, self.y), player_pos)
                self.path_index = 0
                self.moves_since_recalc = 0
        
        # Move one step towards next position
        if self.path and self.path_index < len(self.path) - 1:
            next_pos = self.path[self.path_index + 1]
            
            if maze.is_path(next_pos[0], next_pos[1]):
                old_x, old_y = self.x, self.y
                self.x = next_pos[0]
                self.y = next_pos[1]
                
                dx = self.x - old_x
                dy = self.y - old_y
                self._update_direction(dx, dy)
                
                self.path_index += 1
                self.moves_since_recalc += 1
    
    def _patrol(self, maze: Maze) -> None:
        # Patrol randomly when player not detected.
        import random
        
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = self.x + dx, self.y + dy
            if maze.is_path(new_x, new_y):
                self.x = new_x
                self.y = new_y
                self._update_direction(dx, dy)
                break
    
    def _update_direction(self, dx: int, dy: int) -> None:
        # Update enemy direction based on movement.
        if dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"
        elif dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"
    
    def get_position(self) -> Tuple[int, int]:
        # Get enemy current position.
        return (self.x, self.y)
    
    def render(self, screen: pygame.Surface, tile_size: int) -> None:
        # Render enemy sprite on screen.
        if not self.is_alive:
            return
        
        rect = pygame.Rect(self.x * tile_size, self.y * tile_size, tile_size, tile_size)
        
        # Flashing effect when hit
        if self.is_hit:
            current_time = time.time()
            elapsed = current_time - self.hit_start_time
            
            # Flash between normal and red
            if int(elapsed * 10) % 2 == 0:
                hit_surface = pygame.Surface((tile_size, tile_size))
                hit_surface.fill((255, 0, 0))
                screen.blit(hit_surface, rect)
            else:
                screen.blit(self.sprite, rect)
        else:
            screen.blit(self.sprite, rect)