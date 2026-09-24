import tkinter as tk
from mazegen import MazeGenerator

CELL = 30  # pixels per cell
PAD = 20  # margin around the maze

# 1) make a real maze using YOUR package
gen = MazeGenerator(
    width=10, height=8, entry=(0, 0), exit=(9, 7), perfect=True, seed=42
)
gen.generate()
grid = gen.get_grid()

# 2) size the window to fit the maze
width_px = gen.width * CELL + 2 * PAD
height_px = gen.height * CELL + 2 * PAD

root = tk.Tk()
root.title("My Maze Viewer")
canvas = tk.Canvas(root, width=width_px, height=height_px, bg="white")
canvas.pack()

# color the entry (green) and exit (red), behind the walls
for (cx, cy), color in ((gen.entry, "green"), (gen.exit, "red")):
    x0 = PAD + cx * CELL
    y0 = PAD + cy * CELL
    canvas.create_rectangle(x0, y0, x0 + CELL, y0 + CELL, fill=color, outline="")

# 3) draw only the walls that are still closed
for y in range(gen.height):
    for x in range(gen.width):
        cell = grid[y][x]
        x0 = PAD + x * CELL
        y0 = PAD + y * CELL
        x1 = x0 + CELL
        y1 = y0 + CELL
        if cell["N"]:
            canvas.create_line(x0, y0, x1, y0, fill="black", width=2)  # top edge
        if cell["S"]:
            canvas.create_line(x0, y1, x1, y1, fill="black", width=2)  # bottom edge
        if cell["W"]:
            canvas.create_line(x0, y0, x0, y1, fill="black", width=2)  # left edge
        if cell["E"]:
            canvas.create_line(x1, y0, x1, y1, fill="black", width=2)  # right edge

# --- draw the solution path in blue ---
STEP = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def cell_center(cx, cy):
    """Pixel coordinates of the middle of cell (cx, cy)."""
    return PAD + cx * CELL + CELL // 2, PAD + cy * CELL + CELL // 2


solution = gen.get_solution()
if solution:
    x, y = gen.entry
    points = [cell_center(x, y)]  # start at the entry's center
    for step in solution:
        dx, dy = STEP[step]  # how this letter moves us
        x, y = x + dx, y + dy  # move to the next cell
        points.append(cell_center(x, y))

    flat = [n for point in points for n in point]  # [x0,y0,x1,y1,...]
    canvas.create_line(*flat, fill="blue", width=3)
root.bind("<Escape>", lambda event: root.destroy())
root.mainloop()
