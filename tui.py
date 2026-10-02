from mazegen import MazeGenerator

RESET = "\033[0m"
WHITE = "\033[47m"  # white board
PATH_FG = "\033[34;47m"  # blue thin path line
LOGO = "\033[105m"  # the "42" (one colour — change this to recolour it)
ENTRY = "\033[42m"  # green start
EXIT = "\033[41m"  # red exit

# wall line colours option 3 cycles through (first = black)
WALL_PALETTE = ["30", "34", "31", "35", "90"]

STEP = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}

HEAVY = {
    (0, 0, 0, 0): " ",
    (0, 0, 1, 1): "━",
    (1, 1, 0, 0): "┃",
    (0, 1, 0, 1): "┏",
    (0, 1, 1, 0): "┓",
    (1, 0, 0, 1): "┗",
    (1, 0, 1, 0): "┛",
    (1, 1, 0, 1): "┣",
    (1, 1, 1, 0): "┫",
    (0, 1, 1, 1): "┳",
    (1, 0, 1, 1): "┻",
    (1, 1, 1, 1): "╋",
    (1, 0, 0, 0): "┃",
    (0, 1, 0, 0): "┃",
    (0, 0, 1, 0): "━",
    (0, 0, 0, 1): "━",
}
LIGHT = {
    (0, 0, 1, 1): "─",
    (1, 1, 0, 0): "│",
    (0, 1, 0, 1): "┌",
    (0, 1, 1, 0): "┐",
    (1, 0, 0, 1): "└",
    (1, 0, 1, 0): "┘",
    (1, 1, 0, 1): "├",
    (1, 1, 1, 0): "┤",
    (0, 1, 1, 1): "┬",
    (1, 0, 1, 1): "┴",
    (1, 1, 1, 1): "┼",
    (1, 0, 0, 0): "│",
    (0, 1, 0, 0): "│",
    (0, 0, 1, 0): "─",
    (0, 0, 0, 1): "─",
    (0, 0, 0, 0): " ",
}


def _fully(c):
    return c["N"] and c["E"] and c["S"] and c["W"]


def render(gen, show_path=True, wall_fg="30"):
    grid = gen.get_grid()
    H, W = gen.height, gen.width
    R, Cc = 2 * H + 1, 2 * W + 1

    wall = [[False] * Cc for _ in range(R)]
    for y in range(H):
        for x in range(W):
            c = grid[y][x]
            cy, cx = 2 * y + 1, 2 * x + 1
            for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                wall[cy + dr][cx + dc] = True
            if c["N"]:
                wall[cy - 1][cx] = True
            if c["S"]:
                wall[cy + 1][cx] = True
            if c["W"]:
                wall[cy][cx - 1] = True
            if c["E"]:
                wall[cy][cx + 1] = True

    conn = {}
    if show_path:
        px, py = gen.entry
        for s in gen.get_solution():
            dx, dy = STEP[s]
            nx, ny = px + dx, py + dy
            conn.setdefault((px, py), set()).add(s)
            conn.setdefault((nx, ny), set()).add(
                {"N": "S", "S": "N", "E": "W", "W": "E"}[s]
            )
            px, py = nx, ny

    def is42(x, y):
        return 0 <= x < W and 0 <= y < H and _fully(grid[y][x])

    wcol = "\033[" + wall_fg + ";47m"

    def heavy(r, c):
        up = wall[r - 1][c] if r > 0 else False
        dn = wall[r + 1][c] if r < R - 1 else False
        lf = wall[r][c - 1] if c > 0 else False
        rt = wall[r][c + 1] if c < Cc - 1 else False
        return wcol + HEAVY[(int(up), int(dn), int(lf), int(rt))] + RESET

    logo = LOGO + " " + RESET
    white = WHITE + " " + RESET

    def pathline(d):
        g = LIGHT[(int("N" in d), int("S" in d), int("W" in d), int("E" in d))]
        return PATH_FG + g + RESET

    out = []
    for r in range(R):
        s = ""
        for c in range(Cc):
            er, ec = (r % 2 == 0), (c % 2 == 0)
            x, y = c // 2, r // 2
            if er and ec:
                if wall[r][c]:
                    s += heavy(r, c)
                elif (
                    is42(x - 1, y - 1)
                    and is42(x, y - 1)
                    and is42(x - 1, y)
                    and is42(x, y)
                ):
                    s += logo
                else:
                    s += white
            elif er and not ec:
                uy, dyy = r // 2 - 1, r // 2
                if wall[r][c]:
                    s += logo * 3 if is42(x, uy) and is42(x, dyy) else heavy(r, c) * 3
                else:
                    on = (x, uy) in conn and "S" in conn.get((x, uy), set())
                    s += white + (PATH_FG + "│" + RESET if on else white) + white
            elif not er and ec:
                lx, rx = c // 2 - 1, c // 2
                if wall[r][c]:
                    s += logo if is42(lx, y) and is42(rx, y) else heavy(r, c)
                else:
                    on = (lx, y) in conn and "E" in conn.get((lx, y), set())
                    s += PATH_FG + "─" + RESET if on else white
            else:
                if is42(x, y):
                    s += logo * 3
                elif (x, y) == gen.entry:
                    s += ENTRY + "   " + RESET
                elif (x, y) == gen.exit:
                    s += EXIT + "   " + RESET
                elif (x, y) in conn:
                    d = conn[(x, y)]
                    s += PATH_FG + "─" + RESET if "W" in d else white
                    s += pathline(d)
                    s += PATH_FG + "─" + RESET if "E" in d else white
                else:
                    s += white * 3
        out.append(s)
    return "\n".join(out)


def build_maze(config, randomize=False):
    cfg = dict(config)
    if randomize:
        cfg["SEED"] = None
    gen = MazeGenerator.from_config(cfg)
    gen.generate()
    return gen


def run(config):
    gen = build_maze(config)
    show_path = True
    wall_i = 0
    while True:
        print("\033[2J\033[H", end="")
        print(render(gen, show_path, WALL_PALETTE[wall_i]))
        print()
        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show / Hide the shortest path")
        print("3. Rotate the wall colours")
        print("4. Quit")
        choice = input("Choice? (1-4): ").strip()
        if choice == "1":
            gen = build_maze(config, randomize=True)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            wall_i = (wall_i + 1) % len(WALL_PALETTE)
        elif choice == "4":
            break


if __name__ == "__main__":
    from config_parser import parse_config

    run(parse_config("config.txt"))
