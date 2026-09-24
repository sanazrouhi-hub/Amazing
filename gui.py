import tkinter as tk
from mazegen import MazeGenerator

CELL = 28
PAD = 20

# colours of the two "42" digits — change these to whatever you like
FOUR_COLOR = "Purple"  # the "4"
TWO_COLOR = "Purple"  # the "2"

gen = MazeGenerator(
    width=20, height=15, entry=(0, 0), exit=(19, 14), perfect=True, seed=42
)
gen.generate()
grid = gen.get_grid()

width_px = gen.width * CELL + 2 * PAD
height_px = gen.height * CELL + 2 * PAD

root = tk.Tk()
root.title("My Maze Viewer")
canvas = tk.Canvas(root, width=width_px, height=height_px, bg="black")
canvas.pack()

# colour the fully-closed "42" blocks: left digit vs right digit
for y in range(gen.height):
    for x in range(gen.width):
        c = grid[y][x]
        if c["N"] and c["E"] and c["S"] and c["W"]:
            color = FOUR_COLOR if x < gen.width // 2 else TWO_COLOR
            x0 = PAD + x * CELL
            y0 = PAD + y * CELL
            canvas.create_rectangle(
                x0, y0, x0 + CELL, y0 + CELL, fill=color, outline=""
            )

# entry (green) and exit (red)
for (cx, cy), color in ((gen.entry, "green"), (gen.exit, "red")):
    x0 = PAD + cx * CELL
    y0 = PAD + cy * CELL
    canvas.create_rectangle(x0, y0, x0 + CELL, y0 + CELL, fill=color, outline="")

# walls
for y in range(gen.height):
    for x in range(gen.width):
        cell = grid[y][x]
        x0 = PAD + x * CELL
        y0 = PAD + y * CELL
        x1 = x0 + CELL
        y1 = y0 + CELL
        if cell["N"]:
            canvas.create_line(x0, y0, x1, y0, fill="blue", width=3)
        if cell["S"]:
            canvas.create_line(x0, y1, x1, y1, fill="blue", width=3)
        if cell["W"]:
            canvas.create_line(x0, y0, x0, y1, fill="blue", width=3)
        if cell["E"]:
            canvas.create_line(x1, y0, x1, y1, fill="blue", width=3)

# blue solution path
STEP = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
solution = gen.get_solution()
if solution:
    x, y = gen.entry
    points = [(PAD + x * CELL + CELL // 2, PAD + y * CELL + CELL // 2)]
    for step in solution:
        dx, dy = STEP[step]
        x, y = x + dx, y + dy
        points.append((PAD + x * CELL + CELL // 2, PAD + y * CELL + CELL // 2))
    flat = [n for point in points for n in point]
    canvas.create_line(*flat, fill="red", width=4)

root.bind("<Escape>", lambda event: root.destroy())
root.mainloop()
