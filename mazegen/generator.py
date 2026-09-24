import random
from collections import deque
from typing import Dict, Any, List, Tuple, Optional


class MazeGenerator:
    """Generate a maze and (optionally) solve it.

    This class is the reusable core of the project. It knows nothing about
    config files or the rest of the app — you give it plain parameters and
    it gives you back the maze structure and a solution path. That makes it
    safe to import into any future project.

    Two ways to create one:

        # 1) Directly, with your own parameters:
        gen = MazeGenerator(width=20, height=15, entry=(0, 0),
                            exit=(19, 14), perfect=True, seed=42)

        # 2) From a parsed config dict (used by this project's main.py):
        gen = MazeGenerator.from_config(config)

    Then:

        gen.generate()             # builds the maze
        grid = gen.get_grid()      # the maze structure
        path = gen.get_solution()  # e.g. "SSEESSW..." (shortest path)
        gen.save_to_file()         # optional: write it to OUTPUT_FILE
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        perfect: bool = False,
        output_file: str = "maze_output.txt",
        seed: Optional[int] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.output_file = output_file
        self.seed = seed

        if self.seed is not None:
            random.seed(self.seed)

        self.grid = [
            [
                {"N": True, "E": True, "S": True, "W": True, "visited": False}
                for _ in range(self.width)
            ]
            for _ in range(self.height)
        ]
        self.solution: Optional[str] = None

        self._apply_42_pattern()

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "MazeGenerator":
        """Build a MazeGenerator from a parsed config dict (see config_parser)."""
        return cls(
            width=config["WIDTH"],
            height=config["HEIGHT"],
            entry=config["ENTRY"],
            exit=config["EXIT"],
            perfect=config["PERFECT"],
            output_file=config["OUTPUT_FILE"],
            seed=config.get("SEED", None),
        )

    def get_grid(self) -> List[List[Dict[str, Any]]]:
        """Return the maze structure (call generate() first)."""
        return self.grid

    def get_solution(self) -> str:
        """Return the shortest-path solution, computing it once and caching it."""
        if self.solution is None:
            self.solution = self.solve_shortest_path()
        return self.solution

    def _apply_42_pattern(self) -> None:
        # The "42" is drawn by fully-closed cells (1 = a closed wall cell).
        bitmap = [
            "1010111",
            "1010001",
            "1110111",
            "0010100",
            "0010111",
        ]
        ph = len(bitmap)
        pw = len(bitmap[0])
        if self.width < pw + 2 or self.height < ph + 2:
            print("Warning: Maze size is too small to fit the '42' pattern.")
            return

        start_x = (self.width - pw) // 2
        start_y = (self.height - ph) // 2
        for row in range(ph):
            for col in range(pw):
                if bitmap[row][col] == "1":
                    cell = self.grid[start_y + row][start_x + col]
                    cell["N"] = True
                    cell["E"] = True
                    cell["S"] = True
                    cell["W"] = True
                    # mark visited so generate() carves *around* it,
                    # leaving these cells fully closed to form the "42"
                    cell["visited"] = True

    def generate(self) -> None:
        stack = []
        start_x, start_y = 0, 0
        self.grid[start_y][start_x]["visited"] = True
        stack.append((start_x, start_y))

        while stack:
            cx, cy = stack[-1]
            neighbors = self._get_Unvisited_neighbors(cx, cy)

            if neighbors:
                nx, ny, direction = random.choice(neighbors)
                self._remove_walls(cx, cy, nx, ny, direction)
                self.grid[ny][nx]["visited"] = True
                stack.append((nx, ny))
            else:
                stack.pop()

        if not self.perfect:
            self._create_loops()

    def _get_Unvisited_neighbors(self, x: int, y: int) -> List[Tuple[int, int, str]]:
        neighbors = []
        directions = [
            (0, -1, "N", "S"),
            (1, 0, "E", "W"),
            (0, 1, "S", "N"),
            (-1, 0, "W", "E"),
        ]

        for dx, dy, diri, _ in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not self.grid[ny][nx]["visited"]:
                    neighbors.append((nx, ny, diri))

        return neighbors

    def _remove_walls(self, x1: int, y1: int, x2: int, y2: int, direction: str) -> None:
        if direction == "N":
            self.grid[y1][x1]["N"] = False
            self.grid[y2][x2]["S"] = False
        elif direction == "S":
            self.grid[y1][x1]["S"] = False
            self.grid[y2][x2]["N"] = False
        elif direction == "E":
            self.grid[y1][x1]["E"] = False
            self.grid[y2][x2]["W"] = False
        elif direction == "W":
            self.grid[y1][x1]["W"] = False
            self.grid[y2][x2]["E"] = False

    def _create_loops(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.1:
                    if x + 1 < self.width and self.grid[y][x]["E"]:
                        self._remove_walls(x, y, x + 1, y, "E")

    def solve_shortest_path(self) -> str:
        queue = deque([(self.entry[0], self.entry[1], "")])
        visited = {self.entry}

        while queue:
            x, y, path = queue.popleft()

            if (x, y) == self.exit:
                return path

            directions = [
                (0, -1, "N", "N"),
                (1, 0, "E", "E"),
                (0, 1, "S", "S"),
                (-1, 0, "W", "W"),
            ]

            for dx, dy, diri, char in directions:
                if not self.grid[y][x][diri]:
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < self.width
                        and 0 <= ny < self.height
                        and (nx, ny) not in visited
                    ):
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + char))

        return ""

    def save_to_file(self) -> None:
        with open(self.output_file, "w", encoding="utf-8") as f:
            for y in range(self.height):
                row_hex = []
                for x in range(self.width):
                    cell = self.grid[y][x]
                    val = (
                        (1 if cell["N"] else 0) << 0
                        | (1 if cell["E"] else 0) << 1
                        | (1 if cell["S"] else 0) << 2
                        | (1 if cell["W"] else 0) << 3
                    )
                    row_hex.append(format(val, "X"))
                f.write("".join(row_hex) + "\n")
