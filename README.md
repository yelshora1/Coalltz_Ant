# Collatz's Ant
Langton's ant meets Collatz Conjecture

I got this idea after I watched a video on Langton's ant and the Collatz Conjecture, and I decided to create this. Here is how it works:
- The ant starts in one cube in a infinite grid
- The starting cube has a value of N0, determined by YOU the user
- If N is an odd number, the ant moves to a block 90 degrees to the left. It then prints the value 3N+1 on that block. The algo keeps going in this way for eternity
- If N is an even number, the ant moves to a block 90 degrees to the right. It then prints the value N/2 on that block. This keeps going on for eternity.
- If the ant is currently at a square with an odd number, that square turns black. If even, it is white.
- If the ant encounters a square with a color and a value already, it overwrites the values with it's new value.

Example:
- Lets say you pick the number N0=7. The sequence would go as follows:
-   7 is an odd number, so you would go to a block 90 degrees to the left. you would then run 3(7)+1, and get 22.
-   22 is now printed on the block you are in, so you run it again. 22 is an even number, so you move to a block 90 degrees to the right. you then compute 22/2 which is 11
-   11 is now printed. 11 is odd, you move 90 degrees left. 3(11)+1=34
-   34 odd, 90 degrees right. 34/2=17
-   17 is even, 90 degrees left. 3(17)+1=52
-   52, 90 degrees right. 52/2=26
-   26, 90 degrees right. 26/2=13
-   13, left. 3(13)+1=40
-   40, right. 40/2=20
-   20, right. 20/2=10
-   10, right. 10/2=5
-   5, left. 3(5)+1=16
-   16, right. 16/2=8
-   8, right. 8/2=4
-   4, right. 4/2=2
-   2, right. 2/2=1
-   1, left. 3(1)+1=4
-   4, right. 4/2=2
-   2, right. 2/2=1
-   1, left. wait.........

What you just noticed (4, 2, 1 loop) is the crux of what is called the Collatz Conjecture. It states that no matter what number you use, even up to 2^68 (this has been tested by brute force), the numbers will ALWAYS lead to the 4, 2, 1 loop. However, we still cannot find a reason for this, nor can we prove it yet.

I combined this with Langton's ant, basically its an ant on an infinite white grid. At a white square, it turns 90 degrees clockwise, flips the color of it's current square, and moves forward one unit. At a black square, instead of clockwise, it does the same thing counterclockwise.

Both of these examples are beautiful illustrations of emergent behavior from seemingly simple processes. What this repo aims to do is show the collatz conjecture in a similar way that Langton's ant is illustrated.


## Running the simulation

Use `python3 collatz_ant.py <start_value> -s <steps> [--version MODE]` to run the simulation. The script prints each step with the current position, value and cell color. `MODE` can be `regular` (default) or `hexagonal`.

To watch the ant move on a scrollable grid, run `python3 visuals.py <start_value> -s <steps> [--version MODE]`.
Each cell displays its computed value and the text automatically shrinks so it always fits inside the square. Use the mouse wheel to zoom in or out.
Hold the `Ctrl` key while scrolling to move vertically and hold `Shift` for horizontal movement. Drag with the left mouse button to pan around the grid. Press `t` to cycle through animation speeds. The viewer listens for mouse-wheel events globally so zoom works across platforms and now supports unlimited zoom in either direction.

You can also set the animation speed from the command line with `--speed` to specify steps per second (overriding `-d`):

```bash
python3 visuals.py 124 -s 600 --speed 50
```

