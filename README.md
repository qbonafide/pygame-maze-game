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

**Fog of War**
- Torch illuminates up to 2 tiles (Manhattan distance)
- Creates a challenging exploration experience
- Player must navigate through darkness

**Gameplay**
- Start at top-left (1, 1)
- Find the exit at bottom-right (19, 14)
- Use Arrow Keys or WASD to move
- Yellow square = Player position
- Green square = Exit (when visible)
- White tiles = Paths
- Dark gray tiles = Walls

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

**Enemy Chasing Player**: A Star Algorithm
- Enemy detect player in visin and create shortest path to player using A Star algorithm

**Maze Generation**: Recursive Backtracking
- Carves out paths by randomly choosing unvisited neighbors
- Always creates a perfect maze (no loops, all areas connected)

**Visibility System**: Manhattan Distance
- `distance = |player_x - tile_x| + |player_y - tile_y|`
- Torch illuminates all tiles where distance ≤ 2

### Requirements

- Python 3.7+
- pygame 2.5. 2+