# Collatz Ant Simulation

"""Core logic for the Collatz Ant simulation."""

import argparse
from dataclasses import dataclass, field
from typing import Dict, Iterable, Tuple
from collections import deque


Position = Tuple[int, int]


def turn_left(orientation: int, mod: int) -> int:
    """Rotate ``orientation`` counter-clockwise."""
    return (orientation - 1) % mod


def turn_right(orientation: int, mod: int) -> int:
    """Rotate ``orientation`` clockwise."""
    return (orientation + 1) % mod


def move_forward(position: Position, orientation: int, version: str) -> Position:
    """Move one unit forward from ``position`` in ``orientation``."""
    x, y = position
    if version == "regular":
        if orientation == 0:  # up
            return x, y + 1
        if orientation == 1:  # right
            return x + 1, y
        if orientation == 2:  # down
            return x, y - 1
        if orientation == 3:  # left
            return x - 1, y
    elif version == "hexagonal":
        deltas = [
            (0, 1),  # north
            (1, 0),  # north-east
            (1, -1),  # south-east
            (0, -1),  # south
            (-1, 0),  # south-west
            (-1, 1),  # north-west
        ]
        dx, dy = deltas[orientation]
        return x + dx, y + dy
    raise ValueError(f"Invalid orientation {orientation}")


def count_loops(grid: Dict[Position, int]) -> int:
    """Return the number of enclosed empty regions in ``grid``."""
    if not grid:
        return 0

    xs = [x for x, _ in grid.keys()]
    ys = [y for _, y in grid.keys()]
    min_x, max_x = min(xs) - 1, max(xs) + 1
    min_y, max_y = min(ys) - 1, max(ys) + 1
    width = max_x - min_x + 1
    height = max_y - min_y + 1

    # build binary map of visited cells
    visited_map = [[0] * width for _ in range(height)]
    for x, y in grid.keys():
        row = max_y - y
        col = x - min_x
        visited_map[row][col] = 1

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    seen = [[False] * width for _ in range(height)]
    loops = 0

    for r in range(height):
        for c in range(width):
            if visited_map[r][c] == 0 and not seen[r][c]:
                queue = deque([(r, c)])
                seen[r][c] = True
                touches_border = False
                while queue:
                    cr, cc = queue.popleft()
                    if cr == 0 or cr == height - 1 or cc == 0 or cc == width - 1:
                        touches_border = True
                    for dr, dc in dirs:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < height and 0 <= nc < width:
                            if visited_map[nr][nc] == 0 and not seen[nr][nc]:
                                seen[nr][nc] = True
                                queue.append((nr, nc))
                if not touches_border:
                    loops += 1
    return loops


@dataclass
class CollatzAnt:
    """Stateful Collatz Ant implementation."""

    start_value: int
    version: str = "regular"
    grid: Dict[Position, int] = field(default_factory=dict)
    position: Position = (0, 0)
    orientation: int = 0  # orientation index
    orientation_mod: int = field(init=False)
    steps_taken: int = 0
    loop_count: int = 0


    def __post_init__(self) -> None:
        self.grid[self.position] = self.start_value
        if self.version == "regular":
            self.orientation_mod = 4
        elif self.version == "hexagonal":
            self.orientation_mod = 6
        else:
            raise ValueError(f"Unknown version {self.version}")

    def step(self) -> Tuple[Position, int]:
        """Advance the ant by a single step.

        Returns a tuple ``(position, value)`` of the new cell the ant lands on.
        """

        current_value = self.grid[self.position]
        if current_value % 2 == 0:
            self.orientation = turn_right(self.orientation, self.orientation_mod)
            new_value = current_value // 2
        else:
            self.orientation = turn_left(self.orientation, self.orientation_mod)
            new_value = 3 * current_value + 1

        self.position = move_forward(self.position, self.orientation, self.version)
        self.grid[self.position] = new_value
        self.steps_taken += 1

        return self.position, new_value

    def update_loop_count(self) -> int:
        """Recalculate ``loop_count`` based on the current grid."""
        if self.version != "regular":
            self.loop_count = 0
            return 0
        self.loop_count = count_loops(self.grid)
        return self.loop_count

    def history(self, steps: int) -> Iterable[Tuple[Position, int]]:
        """Iterate over ``steps`` simulation steps including the start state."""

        yield self.position, self.grid[self.position]
        for _ in range(steps):
            yield self.step()


def simulate(start_value: int, steps: int, version: str = "regular") -> Iterable[Tuple[Position, int]]:
    """Utility function returning ``steps`` steps of the simulation."""

    ant = CollatzAnt(start_value, version=version)
    yield from ant.history(steps)


def main():
    parser = argparse.ArgumentParser(description="Collatz Ant simulation")
    parser.add_argument("start", type=int, help="Starting value (N0)")
    parser.add_argument("-s", "--steps", type=int, default=20, help="Number of steps to simulate")
    parser.add_argument(
        "--version",
        choices=["regular", "hexagonal"],
        default="regular",
        help="Simulation mode to use",
    )
    args = parser.parse_args()

    ant = CollatzAnt(args.start, version=args.version)
    for step, (pos, val) in enumerate(ant.history(args.steps)):
        x, y = pos
        color = "black" if val % 2 else "white"
        print(
            f"{step:4d}: position=({x:3d},{y:3d}) value={val:>10} color={color}"
        )

    if args.version == "regular":
        ant.update_loop_count()
        print(f"Loops observed: {ant.loop_count}")


if __name__ == "__main__":
    main()
