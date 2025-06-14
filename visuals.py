"""Tkinter based visualization for the Collatz Ant simulation."""

import argparse
import tkinter as tk

from coalltz_ant import CollatzAnt

CELL_SIZE = 20
DELAY = 200  # milliseconds between steps
INITIAL_EXTENT = 500  # initial half-size of the scroll region


class AntVisualizer:
    def __init__(self, start_value: int, steps: int | None, delay: int = DELAY) -> None:
        self.ant = CollatzAnt(start_value)
        self.steps = steps
        self.delay = delay

        self.root = tk.Tk()
        self.root.title("Collatz Ant")

        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="white")
        self.hbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.vbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.hbar.grid(row=1, column=0, sticky="ew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        extent = INITIAL_EXTENT
        self.canvas.config(scrollregion=(-extent, -extent, extent, extent))
        # Center the view
        self.canvas.xview_moveto(0.5)
        self.canvas.yview_moveto(0.5)

        self.ant_marker = None
        # draw starting cell
        self.draw_cell(self.ant.position, self.ant.grid[self.ant.position])
        self.draw_ant()

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self.on_shift_mousewheel)

    def grid_to_canvas(self, x: int, y: int) -> tuple[int, int, int, int]:
        cx = x * CELL_SIZE
        cy = -y * CELL_SIZE
        return cx, cy, cx + CELL_SIZE, cy + CELL_SIZE

    def on_mousewheel(self, event: tk.Event) -> None:
        delta = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(delta, "units")

    def on_shift_mousewheel(self, event: tk.Event) -> None:
        delta = -1 if event.delta > 0 else 1
        self.canvas.xview_scroll(delta, "units")

    def draw_cell(self, pos: tuple[int, int], value: int) -> None:
        coords = self.grid_to_canvas(*pos)
        color = "black" if value % 2 else "white"
        self.canvas.create_rectangle(*coords, fill=color, outline="gray")

    def draw_ant(self) -> None:
        if self.ant_marker is not None:
            self.canvas.delete(self.ant_marker)
        coords = self.grid_to_canvas(*self.ant.position)
        self.ant_marker = self.canvas.create_rectangle(*coords, fill="red")

    def update_scrollregion(self) -> None:
        bbox = self.canvas.bbox("all")
        if bbox is not None:
            self.canvas.config(scrollregion=bbox)

    def step(self) -> None:
        if self.steps is not None and self.steps <= 0:
            return
        if self.steps is not None:
            self.steps -= 1

        pos, val = self.ant.step()
        self.draw_cell(pos, val)
        self.draw_ant()
        self.update_scrollregion()
        self.root.after(self.delay, self.step)

    def run(self) -> None:
        self.root.after(self.delay, self.step)
        self.root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize the Collatz Ant")
    parser.add_argument("start", type=int, help="Starting value (N0)")
    parser.add_argument("-s", "--steps", type=int, help="Number of steps to simulate")
    parser.add_argument("-d", "--delay", type=int, default=DELAY, help="Delay between steps in ms")
    args = parser.parse_args()

    AntVisualizer(args.start, args.steps, args.delay).run()


if __name__ == "__main__":
    main()
