"""
Camera/Visibility module for handling fog of war with torch visibility.
"""
from typing import Set, Tuple


class Camera:
    """Handle visibility calculation based on torch range."""
    
    def __init__(self, vision_range: int, maze_width: int, maze_height: int):
        """
        Initialize camera with vision range.
        
        Args:
            vision_range: How many tiles the torch can illuminate
            maze_width: Width of maze
            maze_height: Height of maze
        """
        self.vision_range = vision_range
        self.maze_width = maze_width
        self.maze_height = maze_height
    
    def get_visible_tiles(self, player_x: int, player_y: int) -> Set[Tuple[int, int]]:
        """
        Calculate which tiles are visible from player position using Manhattan distance.
        
        Args:
            player_x: Player X coordinate
            player_y: Player Y coordinate
            
        Returns:
            Set of (x, y) tuples representing visible tiles
        """
        visible = set()
        
        for dx in range(-self.vision_range, self.vision_range + 1):
            for dy in range(-self.vision_range, self.vision_range + 1):
                nx = player_x + dx
                ny = player_y + dy
                
                # Use Manhattan distance for torch visibility
                distance = abs(dx) + abs(dy)
                
                if distance <= self.vision_range:
                    # Check bounds
                    if 0 <= nx < self.maze_width and 0 <= ny < self.maze_height:
                        visible. add((nx, ny))
        
        return visible