# Coalltz Ant Simulation

import argparse


def turn_left(orientation):
    return (orientation - 1) % 4


def turn_right(orientation):
    return (orientation + 1) % 4


def move_forward(position, orientation):
    x, y = position
    if orientation == 0:  # up
        return x, y + 1
    elif orientation == 1:  # right
        return x + 1, y
    elif orientation == 2:  # down
        return x, y - 1
    elif orientation == 3:  # left
        return x - 1, y


def simulate(start_value, steps):
    grid = {(0, 0): start_value}
    position = (0, 0)
    orientation = 0  # start facing up

    history = [(position, start_value)]

    for _ in range(steps):
        current_value = grid[position]
        if current_value % 2 == 0:
            orientation = turn_right(orientation)
            new_value = current_value // 2
        else:
            orientation = turn_left(orientation)
            new_value = 3 * current_value + 1

        position = move_forward(position, orientation)
        grid[position] = new_value
        history.append((position, new_value))

    return history


def main():
    parser = argparse.ArgumentParser(description="Coalltz Ant simulation")
    parser.add_argument("start", type=int, help="Starting value (N0)")
    parser.add_argument("-s", "--steps", type=int, default=20, help="Number of steps to simulate")
    args = parser.parse_args()

    history = simulate(args.start, args.steps)
    for step, (pos, val) in enumerate(history):
        x, y = pos
        color = "black" if val % 2 else "white"
        print(f"{step:4d}: position=({x:3d},{y:3d}) value={val:>10} color={color}")


if __name__ == "__main__":
    main()
