import sys
from config_parser import parse_config
from maze_generator import MazeGenerator

def main():
    try:
        print("Reading configuration from config.txt...")
        config = parse_config("config.txt")
        
        print("Generating maze...")
        maze = MazeGenerator(config)
        maze.generate()
        
        print(f"Saving maze and solution to {config['OUTPUT_FILE']}...")
        maze.save_to_file()
        
        print("Maze generated and saved successfully!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()