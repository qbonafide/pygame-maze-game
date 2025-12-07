"""
Player module for handling player movement and sprite animation.
"""
from typing import Tuple, Dict, Optional
import pygame
from src.maze import Maze


class Player:
    
    def __init__(self, x: int, y: int, tile_size: int = 32):
        """
        Initialize player at given position.
        
        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            tile_size: Size of each tile (default 32px)
        """
        self. x = x
        self.y = y
        self.tile_size = tile_size
        self.direction = "down"  # down, up, left, right
        self. sprites: Dict[str, Optional[pygame.Surface]] = {
            "down": None,
            "up": None,
            "left": None,
            "right": None
        }
        self.load_sprites()
    
    def load_sprites(self) -> None:
        """
        Load sprite assets from files.
        Tries to load custom sprites, falls back to placeholder if not found.
        """
        sprite_paths = {
            "down": "assets/sprites/player_down.png",
            "up": "assets/sprites/player_up.png",
            "left": "assets/sprites/player_left.png",
            "right": "assets/sprites/player_right.png"
        }
        
        for direction, path in sprite_paths.items():
            try:
                sprite = pygame.image.load(path)
                # Scale to tile size if needed
                sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
                self.sprites[direction] = sprite
                print(f"✓ Loaded sprite: {direction}")
            except pygame.error as e:
                print(f"⚠ Warning: Could not load sprite {path}: {e}")
                print(f"  Using placeholder for {direction} direction")
                # Create placeholder sprite
                self.sprites[direction] = self._create_placeholder_sprite()
    
    def _create_placeholder_sprite(self) -> pygame.Surface:
        """
        Create a placeholder sprite in case sprite assets are not found.
        
        Returns:
            Placeholder surface with a colored square
        """
        surface = pygame.Surface((self.tile_size, self.tile_size))
        surface.fill((255, 255, 0))  # Yellow placeholder
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
        return surface
    
    def move(self, dx: int, dy: int, maze: Maze) -> bool:
        """
        Move player in given direction with collision detection.
        
        Args:
            dx: Change in X
            dy: Change in Y
            maze: Maze instance for collision checking
            
        Returns:
            True if movement was successful, False if blocked by wall
        """
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check bounds and collision
        if maze.is_path(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self._update_direction(dx, dy)
            return True
        
        return False
    
    def _update_direction(self, dx: int, dy: int) -> None:
        """
        Update player direction based on movement. 
        
        Args:
            dx: Change in X
            dy: Change in Y
        """
        if dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"
        elif dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get player current position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self. y)
    
    def get_direction(self) -> str:
        """
        Get player current direction.
        
        Returns:
            Direction string: 'up', 'down', 'left', or 'right'
        """
        return self.direction
    
    def get_sprite(self) -> pygame.Surface:
        """
        Get current sprite based on player direction.
        
        Returns:
            Sprite surface for current direction
        """
        sprite = self.sprites.get(self.direction)
        if sprite is None:
            return self._create_placeholder_sprite()
        return sprite
    
    def get_sprite_rect(self, screen_offset_x: int = 0, screen_offset_y: int = 0) -> pygame.Rect:
        """
        Get sprite rectangle for rendering.
        
        Args:
            screen_offset_x: X offset for screen position (default 0)
            screen_offset_y: Y offset for screen position (default 0)
            
        Returns:
            Rect object with player sprite position
        """
        x = self.x * self.tile_size + screen_offset_x
        y = self.y * self.tile_size + screen_offset_y
        return pygame.Rect(x, y, self.tile_size, self.tile_size)