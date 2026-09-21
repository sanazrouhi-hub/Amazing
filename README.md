# mazegen

A small, reusable maze generator. Give it parameters, get back a maze
structure and a shortest-path solution. Reproducible via a seed.

## Install

    pip install mazegen            # from a built wheel / PyPI
    pip install -e .               # editable, for development

## Usage

    from mazegen import MazeGenerator

    gen = MazeGenerator(
        width=20,
        height=15,
        entry=(0, 0),
        exit=(19, 14),
        perfect=True,
        seed=42,          # same seed -> same maze every time
    )
    gen.generate()

    grid = gen.get_grid()        # the maze structure (list of rows of cells)
    path = gen.get_solution()    # shortest path as a string, e.g. "SSEE..."
    gen.save_to_file()           # optional: write to OUTPUT_FILE

### From a config dict

    from config_parser import parse_config
    from mazegen import MazeGenerator

    config = parse_config("config.txt")
    gen = MazeGenerator.from_config(config)
    gen.generate()

## Parameters

| Name          | Type            | Meaning                                   |
| ------------- | --------------- | ----------------------------------------- |
| `width`       | int             | Maze width in cells                       |
| `height`      | int             | Maze height in cells                      |
| `entry`       | (int, int)      | Start cell as (x, y)                      |
| `exit`        | (int, int)      | Goal cell as (x, y)                       |
| `perfect`     | bool            | True = single path; False = add loops     |
| `output_file` | str             | Where `save_to_file()` writes             |
| `seed`        | int or None     | Fix for reproducible output               |

## License

MIT — see LICENSE.md.
