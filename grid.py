"""
grid.py - Mars Rover Environment & Sensor Percept Model with Multi-Cell Storm Hazards
---------------------------------------------------------------------------------
State Space & Environment Definition:
- Supports scenario presets ("solvable", "trapped", "clear").
- Features Multi-Cell Storm Hazards (2x2 / 3x3 contiguous hazard clusters).
"""

# Cell Constants
UNKNOWN = 0
SAFE = 1
START = 2
GOAL = 3
HAZARD = 4
RADIATION = 5
STORM = 6  # Multi-Cell Dust Storm Hazard


class GridEnvironment:
    def __init__(self, size=10, start=(0, 0), goal=(9, 9), preset="solvable"):
        """
        Initializes the Mars Environment ground truth grid and sensor model.
        """
        self.size = size
        self.start = start
        self.goal = goal
        self.preset = preset
        
        # Ground Truth Grid Array
        self.ground_truth = [[SAFE for _ in range(size)] for _ in range(size)]
        self.perceived_grid = [[UNKNOWN for _ in range(size)] for _ in range(size)]
        self.storm_cells = set()
        
        self._setup_environment()

    def _setup_environment(self):
        """Sets up multi-cell storm clusters, static hazards, radiation, start, and goal."""
        sx, sy = self.start
        gx, gy = self.goal
        
        self.ground_truth[sy][sx] = START
        self.ground_truth[gy][gx] = GOAL
        self.perceived_grid[sy][sx] = START
        self.perceived_grid[gy][gx] = GOAL

        if self.preset == "trapped":
            # Trapped Preset: Large 3x2 Multi-Cell Storm Barrier blocking column 2
            storm_clusters = [
                (2, 0), (2, 1), (2, 2),  # 3-cell storm cluster
                (3, 0), (3, 1), (3, 2),  # Adjacent 3-cell storm cluster (3x2 block)
                (6, 5), (6, 6), (7, 5), (7, 6) # 2x2 storm cluster
            ]
            hazards = [(4, 4), (4, 5)]
            radiation_zones = [(1, 3), (1, 4)]

        elif self.preset == "clear":
            storm_clusters = [(4, 4), (4, 5), (5, 4), (5, 5)]  # Single 2x2 storm cluster
            hazards = []
            radiation_zones = []

        else:
            # Solvable Preset: Multi-cell storm cluster (2x2) with safe path around
            storm_clusters = [
                (3, 1), (3, 2), (4, 1), (4, 2), # 2x2 Multi-Cell Storm Hazard
                (7, 6), (7, 7), (8, 6), (8, 7)  # 2x2 Multi-Cell Storm Hazard
            ]
            hazards = [(6, 3), (2, 6)]
            radiation_zones = [(5, 1), (1, 5)]

        # Place Storm Clusters
        for cx, cy in storm_clusters:
            if (cx, cy) != self.start and (cx, cy) != self.goal:
                self.ground_truth[cy][cx] = STORM
                self.storm_cells.add((cx, cy))

        # Place Static Hazards
        for hx, hy in hazards:
            if (hx, hy) != self.start and (hx, hy) != self.goal:
                self.ground_truth[hy][hx] = HAZARD

        # Place Radiation Zones
        for rx, ry in radiation_zones:
            if (rx, ry) != self.start and (rx, ry) != self.goal:
                self.ground_truth[ry][rx] = RADIATION

    def deploy_shield_blast(self, x, y):
        """Clears ground truth storm/hazard at (x, y) via Overdrive Shield Blast."""
        if 0 <= x < self.size and 0 <= y < self.size:
            if (x, y) != self.goal and (x, y) != self.start:
                self.ground_truth[y][x] = SAFE
                if (x, y) in self.storm_cells:
                    self.storm_cells.remove((x, y))

    def get_neighbors(self, x, y):
        """Returns valid 4-orthogonal neighbors."""
        neighbors = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors

    def perceive(self, x, y):
        """Sensor Percept Model: Detects adjacent Hazards, Radiation, and Multi-Cell Storms."""
        neighbors = self.get_neighbors(x, y)
        breeze = any(self.ground_truth[ny][nx] in (HAZARD, STORM) for nx, ny in neighbors)
        glow = any(self.ground_truth[ny][nx] == RADIATION for nx, ny in neighbors)
        return breeze, glow
