"""
Maze module for generating random mazes using Recursive Backtracking algorithm.
"""
import random
from typing import List, Set, Tuple


class Maze:
    
    def __init__(self, width: int, height: int):
        """
        Initialize maze with given dimensions.
        
        Args:
            width: Maze width in tiles
            height: Maze height in tiles
        """
        self. width = width
        self.height = height
        # 1 = wall, 0 = path
        self.grid: List[List[int]] = [[1 for _ in range(width)] for _ in range(height)]
        self.generate_maze()
    
    def generate_maze(self) -> None:
        """Generate maze using Recursive Backtracking algorithm."""
        stack: List[Tuple[int, int]] = []
        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = 0  # Mark as path
        stack.append((start_x, start_y))
        
        # 4 directions: Up, Right, Down, Left (2 steps at a time)
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        
        while stack:
            x, y = stack[-1]
            random.shuffle(directions)
            found = False
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # Check if next cell is within bounds and is a wall
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                    if self.grid[ny][nx] == 1:  # Unvisited wall
                        # Mark the wall between current and next cell as path
                        self.grid[y + dy // 2][x + dx // 2] = 0
                        # Mark next cell as path
                        self. grid[ny][nx] = 0
                        stack.append((nx, ny))
                        found = True
                        break
            
            if not found:
                stack.pop()
    
    def is_wall(self, x: int, y: int) -> bool:
        """
        Check if a tile is a wall.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if tile is a wall, False if it's a path
        """
        if not (0 <= x < self. width and 0 <= y < self.height):
            return True
        return self.grid[y][x] == 1
    
    def is_path(self, x: int, y: int) -> bool:
        """
        Check if a tile is a path.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if tile is a path, False if it's a wall
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.grid[y][x] == 0