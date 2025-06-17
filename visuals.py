"""Tkinter based visualization for the Collatz Ant simulation."""

import argparse
import tkinter as tk

from collatz_ant import CollatzAnt

BASE_CELL_SIZE = 20
DELAY = 200  # milliseconds between steps
INITIAL_EXTENT = 500  # initial half-size of the scroll region


class AntVisualizer:
    def __init__(self, start_value: int, steps: int |None, delay: int = DELAY, version: str = "regular") -> None:
        self.ant = CollatzAnt(start_value, version=version)
        self.steps = steps
        self.delay = delay
        self.delay_options = [50, 100, 200, 400, 800]
        if self.delay not in self.delay_options:
            self.delay_options.append(self.delay)
            self.delay_options.sort()
        self.delay_index = self.delay_options.index(self.delay)
        self.zoom = 1.0
        self.cell_size = BASE_CELL_SIZE * self.zoom

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
        self.speed_label = tk.Label(self.root)
        self.speed_label.grid(row=2, column=0, columnspan=2)

        extent = INITIAL_EXTENT
        self.canvas.config(scrollregion=(-extent, -extent, extent, extent))
        # Center the view
        self.canvas.xview_moveto(0.5)
        self.canvas.yview_moveto(0.5)

        self.ant_marker = None
        self.drawn_cells: dict[tuple[int, int], tuple[int, int]] = {}
        # draw starting cell
        self.draw_cell(self.ant.position, self.ant.grid[self.ant.position])
        self.draw_ant()

        # Bind mouse events for scrolling, dragging and zooming
        # ``bind_all`` ensures we capture the wheel even when the canvas does
        # not have focus and ``Button-4/5`` supports Linux systems.
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.root.bind("t", self.toggle_speed)
        self.update_speed_label()


    def grid_to_canvas(self, x: int, y: int) -> tuple[int, int, int, int]:
        size = self.cell_size
        cx = x * size
        cy = -y * size
        return cx, cy, cx + size, cy + size

    def font_for_value(self, value: int) -> tuple[str, int]:
        digits = max(len(str(value)), 1)
        # Keep some padding so numbers do not touch cell edges
        size = int(min(self.cell_size * 0.5, self.cell_size * 1.1 / digits))
        size = max(size, 1)
        return ("Helvetica", size)

    def zoom_view(self, direction: int) -> None:
        factor = 1.1 if direction < 0 else 0.9
        self.zoom *= factor
        self.cell_size = BASE_CELL_SIZE * self.zoom
        for pos, (rect_id, text_id) in self.drawn_cells.items():
            value = self.ant.grid.get(pos, 0)
            coords = self.grid_to_canvas(*pos)
            self.canvas.coords(rect_id, *coords)
            self.canvas.coords(text_id, coords[0] + self.cell_size / 2, coords[1] + self.cell_size / 2)
            self.canvas.itemconfig(text_id, font=self.font_for_value(value))
        if self.ant_marker is not None:
            coords = self.grid_to_canvas(*self.ant.position)
            self.canvas.coords(self.ant_marker, *coords)
        self.update_scrollregion()

    def on_button_press(self, event: tk.Event) -> None:
        self.canvas.scan_mark(event.x, event.y)

    def on_drag(self, event: tk.Event) -> None:
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_mousewheel(self, event: tk.Event) -> None:
        """Zoom with the mouse wheel, scroll with modifiers."""
        if hasattr(event, "num") and event.num in (4, 5):
            delta = -1 if event.num == 4 else 1
        else:
            delta = -1 if event.delta > 0 else 1
        if event.state & 0x0001:  # Shift pressed -> horizontal pan
            self.canvas.xview_scroll(delta, "units")
        elif event.state & 0x0004:  # Control pressed -> vertical pan
            self.canvas.yview_scroll(delta, "units")
        else:
            self.zoom_view(delta)

    def draw_cell(self, pos: tuple[int, int], value: int) -> None:
        coords = self.grid_to_canvas(*pos)
        color = "black" if value % 2 else "white"
        text_color = "white" if value % 2 else "black"
        rect_id, text_id = self.drawn_cells.get(pos, (None, None))
        font = self.font_for_value(value)
        if rect_id is None:
            rect_id = self.canvas.create_rectangle(*coords, fill=color, outline="gray")
            text_id = self.canvas.create_text(
                coords[0] + self.cell_size / 2,
                coords[1] + self.cell_size / 2,
                text=str(value),
                fill=text_color,
                font=font,
            )
            self.drawn_cells[pos] = (rect_id, text_id)
        else:
            self.canvas.coords(rect_id, *coords)
            self.canvas.coords(text_id, coords[0] + self.cell_size / 2, coords[1] + self.cell_size / 2)
            self.canvas.itemconfig(rect_id, fill=color)
            self.canvas.itemconfig(text_id, text=str(value), fill=text_color, font=font)

    def draw_ant(self) -> None:
        if self.ant_marker is not None:
            self.canvas.delete(self.ant_marker)
        coords = self.grid_to_canvas(*self.ant.position)
        self.ant_marker = self.canvas.create_rectangle(*coords, fill="red")

    def update_scrollregion(self) -> None:
        bbox = self.canvas.bbox("all")
        if bbox is not None:
            pad = 100 * self.zoom
            self.canvas.config(
                scrollregion=(bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)
            )

    def update_speed_label(self) -> None:
        sps = 1000 / self.delay if self.delay else 0
        self.speed_label.config(text=f"{sps:.1f} steps/sec")

    def toggle_speed(self, event: tk.Event | None = None) -> None:
        self.delay_index = (self.delay_index + 1) % len(self.delay_options)
        self.delay = self.delay_options[self.delay_index]
        self.update_speed_label()

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
    parser.add_argument("--speed", type=float, help="Animation speed in steps per second")
    parser.add_argument(
        "--version",
        choices=["regular", "hexagonal"],
        default="regular",
        help="Simulation mode to use",
    )
    args = parser.parse_args()

    delay = args.delay
    if args.speed is not None:
        delay = int(1000 / args.speed) if args.speed > 0 else 0

    AntVisualizer(args.start, args.steps, delay, args.version).run()


if __name__ == "__main__":
    main()
