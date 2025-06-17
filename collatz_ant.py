# Collatz Ant Simulation

"""Core logic for the Collatz Ant simulation."""

import argparse
from dataclasses import dataclass, field
from typing import Dict, Tuple, Iterable


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


@dataclass
class CollatzAnt:
    """Stateful Collatz Ant implementation."""

    start_value: int
    version: str = "regular"
    grid: Dict[Position, int] = field(default_factory=dict)
    position: Position = (0, 0)
    orientation: int = 0  # orientation index
    orientation_mod: int = field(init=False)

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
        return self.position, new_value

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

    for step, (pos, val) in enumerate(simulate(args.start, args.steps, args.version)):
        x, y = pos
        color = "black" if val % 2 else "white"
        print(
            f"{step:4d}: position=({x:3d},{y:3d}) value={val:>10} color={color}"
        )


if __name__ == "__main__":
    main()
