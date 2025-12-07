## Pygame Maze Game

A simple maze game built with Pygame featuring:
- **Random Maze Generation** using Recursive Backtracking algorithm
- **Torch Visibility System** - Player can only see 2 tiles in any direction
- **Player Movement** - 4-directional movement with collision detection
- **Goal-Based Gameplay** - Navigate through darkness to find the exit

### Features

**Maze Generation**
- Uses Recursive Backtracking algorithm to generate random, solvable mazes
- Guarantees at least one path from start to exit
- Maze dimensions: 20x15 tiles

**Torch Visibility System**
- Player can only see 2 tiles in any direction (Manhattan distance)
- Creates a challenging exploration experience
- Torch illuminates dynamically as player moves

**Difficulty System**
- Easy: 2 enemies, speed 1. 0, 10 hit attempts
- Medium: 3 enemies, speed 0.75, 7 hit attempts
- Hard: 4 enemies, speed 0. 5, 7 hit attempts

**Multiple Enemy Pathfinding Algorithms**
- A* (A-Star): Optimal pathfinding using heuristics for fastest pursuit
- BFS (Breadth-First Search): Systematic exploration guaranteeing shortest path
- DFS (Depth-First Search): Memory-efficient pathfinding

**Scoring System**
- Base score: 100 points
- Movement penalty: -1 point per step
- Hit bonus: Remaining unused hit attempts converted to bonus points
  - Easy: 3 points per unused hit
  - Medium: 4 points per unused hit
  - Hard: 5 points per unused hit
- Final score minimum: 0 (cannot go negative)

**Combat System**
- Players have limited hit attempts based on difficulty
- Each hit kills an enemy instantly
- Enemies respawn 10 tiles away from player
- Enemy hit detection is responsive and reliable

**Gameplay Elements**
- Start at top-left (1, 1)
- Find the exit at bottom-right (19, 14)
- Defeat or avoid enemies during exploration
- Manage limited hit attempts strategically

### Installation

1. Pull the repository:
```bash
git pull https://github.com/qbonafide/pygame-maze-game.git
cd pygame-maze-game
```

2. Create virtual environment (optional but recommended):
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Game

```bash
python main.py
```

### Controls

- **Arrow Keys** or **WASD** - Move player
- **ESC** - Quit game

### Game Configuration

Edit `config.py` to customize:
- `SCREEN_WIDTH` / `SCREEN_HEIGHT` - Window size
- `MAZE_WIDTH` / `MAZE_HEIGHT` - Maze dimensions
- `TILE_SIZE` - Size of each maze tile
- `VISION_RANGE` - How far the torch can see
- `FPS` - Game frame rate

### Algorithm Used

**A* (A-Star) Algorithm**
- Optimal pathfinding that combines actual distance traveled and heuristic estimate
- Formula: f(n) = g(n) + h(n), where g is cost from start and h is estimated cost to goal
- Uses Manhattan distance heuristic for maze navigation
- Explores only promising nodes, resulting in faster pathfinding
- Enemy behavior: Appears highly intelligent, pursues player efficiently
- Performance: Best for real-time gameplay
- Data structure: Priority queue (heap)

**BFS (Breadth-First Search) Algorithm**
- Explores all neighbors level by level systematically
- Guarantees shortest path in unweighted graphs
- Explores nodes in order of distance from start
- More nodes explored compared to A* but guaranteed optimal path
- Enemy behavior: Systematic exploration, fair and predictable
- Performance: Slower than A* but reliable
- Data structure: Queue (FIFO)
- Worst case: Explores all reachable nodes

**DFS (Depth-First Search) Algorithm**
- Explores deeply along one path before backtracking
- Does not guarantee shortest path
- Memory efficient compared to BFS
- Can find paths faster if target is deep in tree
- Enemy behavior: May take longer routes, less predictable
- Performance: Memory efficient, variable speed
- Data structure: Stack (recursion)
- Use case: When memory is limited or less optimal paths are acceptable

**Maze Generation**: Recursive Backtracking
- Carves out paths by randomly choosing unvisited neighbors
- Always creates a perfect maze (no loops, all areas connected)

**Visibility System**: Manhattan Distance
- `distance = |player_x - tile_x| + |player_y - tile_y|`
- Torch illuminates all tiles where distance ≤ 2

### Requirements

- Python 3.7+
- pygame 2.5. 2+