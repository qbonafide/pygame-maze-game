"""
A* Pathfinding algorithm for maze navigation. 
"""
import heapq
from typing import List, Tuple, Optional, Set


class Node:
    """Represents a node in the pathfinding grid."""
    
    def __init__(self, position: Tuple[int, int], g_cost: float = 0, h_cost: float = 0):
        """
        Initialize a node.
        
        Args:
            position: (x, y) coordinate
            g_cost: Cost from start node
            h_cost: Heuristic cost to goal
        """
        self. position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent: Optional['Node'] = None
    
    def __lt__(self, other: 'Node') -> bool:
        """Compare nodes by f_cost for priority queue."""
        return self. f_cost < other.f_cost


class AStar:
    """A* pathfinding algorithm implementation."""
    
    def __init__(self, maze):
        """
        Initialize A* pathfinder.
        
        Args:
            maze: Maze instance for collision checking
        """
        self.maze = maze
    
    @staticmethod
    def _heuristic(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Manhattan distance heuristic.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            Manhattan distance
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Find shortest path from start to goal using A*. 
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
            
        Returns:
            List of positions forming the path, or empty list if no path found
        """
        # Check if start/goal are valid
        if not self.maze. is_path(start[0], start[1]) or not self.maze.is_path(goal[0], goal[1]):
            return []
        
        # Initialize
        open_set: List[Node] = []
        closed_set: Set[Tuple[int, int]] = set()
        
        # Create start node
        start_node = Node(start, 0, self._heuristic(start, goal))
        heapq.heappush(open_set, start_node)
        
        # Keep track of visited nodes for path reconstruction
        node_dict = {start: start_node}
        
        while open_set:
            # Get node with lowest f_cost
            current = heapq.heappop(open_set)
            
            # Check if we reached goal
            if current.position == goal:
                return self._reconstruct_path(current)
            
            closed_set.add(current.position)
            
            # Check all 4 neighbors (up, down, left, right)
            neighbors = [
                (current.position[0], current.position[1] - 1),  # Up
                (current.position[0], current.position[1] + 1),  # Down
                (current.position[0] - 1, current.position[1]),  # Left
                (current.position[0] + 1, current.position[1]),  # Right
            ]
            
            for neighbor_pos in neighbors:
                # Skip if already visited or is wall
                if neighbor_pos in closed_set or self.maze.is_wall(neighbor_pos[0], neighbor_pos[1]):
                    continue
                
                # Calculate costs
                g_cost = current.g_cost + 1
                h_cost = self._heuristic(neighbor_pos, goal)
                
                # Check if this path is better than previously found
                if neighbor_pos in node_dict:
                    if g_cost < node_dict[neighbor_pos].g_cost:
                        node_dict[neighbor_pos]. g_cost = g_cost
                        node_dict[neighbor_pos].f_cost = g_cost + h_cost
                        node_dict[neighbor_pos].parent = current
                else:
                    # Create new node
                    neighbor_node = Node(neighbor_pos, g_cost, h_cost)
                    neighbor_node.parent = current
                    node_dict[neighbor_pos] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
        
        # No path found
        return []
    
    @staticmethod
    def _reconstruct_path(node: Node) -> List[Tuple[int, int]]:
        """
        Reconstruct path from goal node to start.
        
        Args:
            node: Goal node
            
        Returns:
            List of positions from start to goal
        """
        path = []
        current = node
        
        while current is not None:
            path.append(current.position)
            current = current.parent
        
        path.reverse()
        return path