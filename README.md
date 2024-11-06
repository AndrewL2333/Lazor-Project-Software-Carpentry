# Lazor-Project-Software-Carpentry
# Lazor Puzzle Solver

This project provides a Python solution for Lazor puzzles defined in `.bff` files. Lazor puzzles involve directing lasers through a grid with blocks of various types, and the objective is to hit specific points in the grid by reflecting or refracting the lasers. This program reads a `.bff` puzzle file, processes its configuration, and then attempts to solve the puzzle by trying different block configurations. If a solution is found, it visualizes the solved puzzle with the laser paths and saves it as a PNG image.

## Features

- **Input Processing:** Reads and parses `.bff` files to extract puzzle configurations, including grid size, block positions, and laser starting positions.
- **Solution Generation:** Uses combinations to place blocks on the grid and checks if a configuration meets the puzzle’s requirements.
- **Path Visualization:** Tracks and draws laser paths as they interact with blocks.
- **Image Saving:** Generates a 3D-effect visualization of the puzzle solution and saves it as a PNG file.

## Dependencies

This program requires the following Python packages:
- `itertools` (standard library)
- `PIL` (Python Imaging Library, often installed as `Pillow`)
- `time` (standard library)

Install the `Pillow` package if not already installed:
```bash
pip install Pillow
```

## Classes

### `Input`

- **Purpose**: Processes a `.bff` file to load the puzzle configuration.
- **Usage**: Instantiates with a filename, then calls to retrieve configuration data.
- **Attributes**: Width, height, and block positions (`o_positions`, `x_positions`, etc.).
- **Methods**: 
  - `__call__()`: Reads the puzzle file and returns a dictionary of configuration data.

### `Lazor_Solution`

- **Purpose**: Solves the Lazor puzzle by testing block configurations.
- **Usage**: Instantiate with puzzle configuration data and call to get a solution.
- **Attributes**: Block counts (`A`, `B`, `C`), positions, laser paths, and solution paths.
- **Methods**:
  - `__call__()`: Attempts to solve the puzzle, returning block layout and paths if successful.
  - `check_solution()`: Simulates laser paths and checks if all target points are hit.

### `SaveSolution`

- **Purpose**: Visualizes and saves the solved puzzle as a PNG image.
- **Usage**: Instantiate with filename, puzzle data, solution layout, and paths, then call to save.
- **Attributes**: Stores information needed to render blocks, lasers, and paths.
- **Methods**:
  - `__call__()`: Generates and saves the solution image.
  - `create_block_with_3d_effect()`: Creates a block image with 3D effect.
  - `draw_lazor_paths()`: Draws laser paths with glow effect.

## Usage

Run the code in a Python environment by specifying `.bff` files. Example:
```python
if __name__ == "__main__":
    filenames = ["puzzle1.bff", "puzzle2.bff"]
    # Main execution loop processes each file
```

This script reads `.bff` files, attempts to solve each puzzle, and saves the solutions as images.

### Example Output

- For each puzzle, if a solution is found, it will be saved as a PNG with laser paths overlaid on the grid.
- Execution times for each puzzle are displayed at the end of the script’s run.

## Notes

- Ensure `.bff` files are properly formatted with "GRID START" and "GRID STOP" delimiters.
- The `Solution` image will be saved in the same directory as the script.
  
Enjoy solving Lazor puzzles with this solver!
