
# Import packages
from itertools import combinations
from PIL import Image, ImageDraw
import time



class Input:
    """
    The Input class processes a `.bff` file to extract configuration data for a Lazor puzzle, 
    including grid layout, block types and counts, lazor start positions, directions, and 
    target points of intersection (POIs). This class handles both the reading of the file 
    and the necessary transformations to align coordinates with the grid’s bottom-left origin. 

    Attributes:
        filename (str): The name of the Lazor test file.
        width (int): The width of the Lazor grid.
        height (int): The height of the Lazor grid.
        
    Methods:
        __call__(): Processes the `.bff` file and returns a dictionary with grid size, 
                    block positions, lazors, POIs, and block counts required for the puzzle.
    """

    def __init__(self, filename: str):
        # Check if file has a valid `.bff` extension
        if not filename.lower().endswith('.bff'):
            raise SystemExit("Invalid file type. Please provide a `.bff` file.")
        
        self.filename = filename
        self.width = 0  # Grid width
        self.height = 0  # Grid height

    def __call__(self) -> dict:
        # Initialize counts and lists for different blocks and positions
        A_count, B_count, C_count = 0, 0, 0
        o_positions, x_positions = [], []  # Open and blocked positions
        A_blocks, B_blocks, C_blocks = [], [], []  # Fixed block positions
        lazors, points = [], []  # Lazor start points and target points

        # Read file content and handle missing file error
        try:
            with open(self.filename, 'r') as file:
                lines = file.read().splitlines()
        except FileNotFoundError:
            raise SystemExit(f"File `{self.filename}` not found.")

        # Locate grid start and stop markers to identify grid boundaries
        try:
            start_idx = lines.index("GRID START") + 1
            stop_idx = lines.index("GRID STOP")
        except ValueError:
            raise SystemExit("GRID START or GRID STOP not found in the test file.")

        # Parse the grid line by line
        for y, line in enumerate(lines[start_idx:stop_idx], start=1):
            tokens = line.split()
            for x, token in enumerate(tokens):
                position = [x, y]
                # Add position to corresponding list based on token
                if token == 'o':
                    o_positions.append(position)
                elif token == 'x':
                    x_positions.append(position)
                elif token == 'A':
                    A_blocks.append(position)
                elif token == 'B':
                    B_blocks.append(position)
                elif token == 'C':
                    C_blocks.append(position)
            self.height = y  # Update height based on rows parsed
            self.width = max(self.width, len(tokens))  # Update width based on max tokens in a line

        # Ensure there is at least one open position for placing blocks
        if not o_positions:
            raise SystemExit("No open positions ('o') found in the grid.")

        # Transform y-coordinates to match grid origin at the bottom-left corner
        for block_list in [o_positions, x_positions, A_blocks, B_blocks, C_blocks]:
            for position in block_list:
                position[1] = self.height - position[1]

        # Parse configurations following the grid (e.g., lazors, POIs, block counts)
        for line in lines[stop_idx + 1:]:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Ignore empty lines and comments

            tokens = line.split()
            identifier = tokens[0]

            # Set block counts based on identifiers
            if identifier in {'A', 'B', 'C'}:
                try:
                    count = int(tokens[-1])
                except (IndexError, ValueError):
                    raise SystemExit(f"Invalid count for block '{identifier}'.")
                if identifier == 'A':
                    A_count = count
                elif identifier == 'B':
                    B_count = count
                elif identifier == 'C':
                    C_count = count
            # Add lazor starting positions and directions
            elif identifier == 'L':
                try:
                    lazors.append([int(tok) for tok in tokens[1:5]])
                except (IndexError, ValueError):
                    raise SystemExit("Invalid Lazor configuration. Ensure positions and directions are specified.")
            # Add points of intersection (POIs)
            elif identifier == 'P':
                try:
                    points.append([int(tok) for tok in tokens[1:3]])
                except (IndexError, ValueError):
                    raise SystemExit("Invalid POI coordinates. Ensure correct format.")

        # Check if any blocks are specified for solving the puzzle
        if not any([A_count, B_count, C_count]):
            raise SystemExit("No blocks ('A', 'B', 'C') specified to solve the Lazor puzzle.")

        # Ensure at least one lazor is defined in the configuration
        if not lazors:
            raise SystemExit("No Lazors provided in the test file.")

        # Transform lazor and POI coordinates to match bottom-left grid origin
        for lazor in lazors:
            lazor[0] *= 0.5  # Scale x-position
            lazor[1] = self.height - (lazor[1] * 0.5)  # Invert and scale y-position
            lazor[2] *= 0.5  # Scale x-direction
            lazor[3] *= -0.5  # Invert and scale y-direction

        for poi in points:
            poi[0] *= 0.5  # Scale x-position
            poi[1] = self.height - (poi[1] * 0.5)  # Invert and scale y-position

        # Compile extracted data into a dictionary for output
        input_data = {
            "Size": [self.width, self.height],
            "o_l": o_positions,
            "Lazers": lazors,
            "Points": points,
            "A": A_count,
            "B": B_count,
            "C": C_count,
            "x_l": x_positions,
            "A_l": A_blocks,
            "B_l": B_blocks,
            "C_l": C_blocks
        }

        return input_data




class Lazor_Solution:
    '''
        This class processes grid and lazor data from input, finds possible 
        block combinations, and checks if any configuration meets the criteria 
        for solving the puzzle by intersecting with all points of interest (POIs).
    '''

    def __init__(self, input_data):
        self.o_l = input_data['o_l']
        self.size = input_data['Size']
        self.lazers = input_data['Lazers']
        self.points = input_data['Points']
        self.A = input_data['A']
        self.B = input_data['B']
        self.C = input_data['C']
        self.A_l = input_data['A_l']
        self.B_l = input_data['B_l']
        self.C_l = input_data['C_l']
        self.sel_comb = {}

    def __call__(self):
        o_lA = list(combinations(self.o_l, self.A))
        for i_a in o_lA:
            o_l = [pos for pos in self.o_l if pos not in i_a]
            a_comb = list(i_a)
            o_lB = list(combinations(o_l, self.B))
            for i_b in o_lB:
                o_l_b = [pos for pos in o_l if pos not in i_b]
                b_comb = list(i_b)
                o_lC = list(combinations(o_l_b, self.C))
                for i_c in o_lC:
                    c_comb = list(i_c)
                    
                    # Populate sel_comb dictionary with A, B, and C combinations
                    self.sel_comb = {}
                    for j, block_position in enumerate([a_comb, b_comb, c_comb]):
                        block_name = ['A', 'B', 'C'][j]
                        for pos in block_position:
                            self.sel_comb[(pos[0], pos[1])] = block_name

                    # Add fixed blocks to sel_comb
                    for block_list, label in zip([self.A_l, self.B_l, self.C_l], ['A', 'B', 'C']):
                        for pos in block_list:
                            self.sel_comb[(pos[0], pos[1])] = label

                    # Check if the current combination solves the puzzle
                    if self.check_solution():
                        return self.sel_comb

    def check_solution(self):
        remaining_points = list(self.points)
        active_lasers = list(self.lazers)  # Start with initial lazors
        
        while active_lasers:
            x, y, vx, vy = active_lasers.pop(0)
            
            while True:
                pos = [x, y]
                
                # Remove intersected points from POIs
                remaining_points = list(filter(lambda p: p != pos, remaining_points))
                if not remaining_points:
                    return True  # All points intersected

                # Determine updated position based on direction
                if x.is_integer() and vx < 0:
                    upd_pos = (x - 1, (y * 2 - 1) / 2)
                elif x.is_integer() and vx > 0:
                    upd_pos = (x, (y * 2 - 1) / 2)
                elif not x.is_integer() and vy < 0:
                    upd_pos = ((x * 2 - 1) / 2, y - 1)
                else:
                    upd_pos = ((x * 2 - 1) / 2, y)

                # Check if the laser is within bounds
                if not self.pos_chk(upd_pos):
                    break  # Out of bounds, end this laser's path

                # Handle interactions with blocks
                if upd_pos in self.sel_comb:
                    block_type = self.sel_comb[upd_pos]
                    if block_type == 'A':
                        x, y, vx, vy = self.reflect((x, y, vx, vy))
                    elif block_type == 'C':
                        # Add both refracted paths to active lazors
                        active_lasers.extend(self.refract((x, y, vx, vy)))
                        break  # Stop processing this path, continue with new paths
                    else:
                        break  # Block B stops the laser
                else:
                    # Move to the next position in the same direction
                    x += vx
                    y += vy

        return not remaining_points  # Return True if all points are intersected

    def pos_chk(self, upd_pos):
        x, y = upd_pos
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]

    def reflect(self, lazer):
        x, y, vx, vy = lazer
        if x.is_integer():
            return x - vx, y + vy, -vx, vy
        else:
            return x + vx, y - vy, vx, -vy

    def refract(self, lazer):
        '''
        Refracts the lazor through a C block, creating two paths:
        one continuing in the original direction and one reflecting.

        **Input Parameters**
            lazer: *List, int*
                Lazor position and direction
        **Returns**
            List of tuples, each representing a new lazor path
            [(x1, y1, vx1, vy1), (x2, y2, vx2, vy2)]
        '''
        x, y, vx, vy = lazer
        
        # Path 1: Continue in original direction
        path1 = (x + vx, y + vy, vx, vy)
        
        # Path 2: Reflect in the opposite direction
        if x.is_integer():
            path2 = (x - vx, y + vy, -vx, vy)
        else:
            path2 = (x + vx, y - vy, vx, -vy)
        
        return [path1, path2]




class SaveSolution:
    '''
        This class defines operations for plotting and saving the final solution
        for a given lazor test case.
    '''

    def __init__(self, filename, info, sel_comb):
        self.filename = filename
        self.info = info
        self.sel_comb = sel_comb
        self.lazers = info["Lazers"]
        self.points = info["Points"]
        self.block_size = 100

    def __call__(self):
        if not self.sel_comb:
            print("No solution is found for the given file")
            return

        size = self.info['Size']
        figure = self.build_figure(size)
        img = self.create_image(size, figure)
        self.draw_grid_lines(img, size)
        self.draw_lazor_points(img, size)
        self.save_image(img)

    def build_figure(self, size):
        color_mapping = {'A': 1, 'B': 2, 'C': 3, 'x': 4}
        figure = [[0] * size[0] for _ in range(size[1])]

        for (x, y), block_type in self.sel_comb.items():
            figure[size[1] - y - 1][x] = color_mapping.get(block_type, 0)
        for x, y in self.info['x_l']:
            figure[size[1] - y - 1][x] = 4

        return figure

    def create_image(self, size, figure):
        img = Image.new("RGBA", (size[0] * self.block_size, size[1] * self.block_size), color=0)
        colors = {
            0: (255, 255, 153),
            1: (0, 102, 204),
            2: (204, 0, 0),
            3: (0, 204, 0),
            4: (51, 51, 51)
        }

        for y, row in enumerate(figure):
            for x, color_id in enumerate(row):
                self.fill_block(img, x, y, colors[color_id])
        return img

    def fill_block(self, img, x, y, color):
        for i in range(self.block_size):
            for j in range(self.block_size):
                img.putpixel((x * self.block_size + i, y * self.block_size + j), color)

    def draw_grid_lines(self, img, size):
        draw = ImageDraw.Draw(img)
        for x in range(0, size[0] * self.block_size, self.block_size):
            draw.line([(x, 0), (x, size[1] * self.block_size)], fill=(0, 0, 0, 255))
        for y in range(0, size[1] * self.block_size, self.block_size):
            draw.line([(0, y), (size[0] * self.block_size, y)], fill=(0, 0, 0, 255))

    def draw_lazor_points(self, img, size):
        draw = ImageDraw.Draw(img)
        colors = {
            'lazor': (255, 140, 0),
            'poi': (128, 0, 128)
        }

        for x, y, *_ in self.lazers:
            xp, yp = x * self.block_size, (size[1] - y) * self.block_size
            draw.ellipse([(xp - 5, yp - 5), (xp + 5, yp + 5)], fill=colors['lazor'])

        for x, y in self.points:
            xp, yp = x * self.block_size, (size[1] - y) * self.block_size
            draw.ellipse([(xp - 10, yp - 10), (xp + 10, yp + 10)], fill=colors['poi'])

    def save_image(self, img):
        if ".bff" in self.filename:
            self.filename = self.filename.replace(".bff", "")
        if not self.filename.endswith(".png"):
            self.filename += ".png"
        img.save(self.filename)


if __name__ == "__main__":
    filenames = ["yarn_5.bff", "tiny_5.bff", "showstopper_4.bff", "numbered_6.bff",
                 "mad_1.bff", "mad_7.bff", "mad_4.bff", "dark_1.bff"]
    execution_times = []

    for filename in filenames:
        start_time = time.time()

        input_processor = Input(filename)
        input_data = input_processor()

        lazor_solver = Lazor_Solution(input_data)
        selected_combination = lazor_solver()

        save_solution = SaveSolution(filename, input_data, selected_combination)
        save_solution()

        end_time = time.time()
        execution_times.append(end_time - start_time)

    print(f"Execution Times: {execution_times}")
