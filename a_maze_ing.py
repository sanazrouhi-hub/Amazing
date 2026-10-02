import sys

from config_parser import parse_config
from mazegen import MazeGenerator
import tui


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    try:
        config = parse_config(sys.argv[1])
        gen = MazeGenerator.from_config(config)
        gen.generate()
        gen.save_to_file()
        print(f"Maze saved to {config['OUTPUT_FILE']}")
        tui.run(config)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
