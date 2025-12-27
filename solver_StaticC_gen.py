import copy

# --- helper functions ---
def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def flip(shape):
    return [row[::-1] for row in shape]

def generate_variants(shape):
    variants = []
    seen = set()
    for _ in range(4):
        shape = rotate(shape)
        for f in [shape, flip(shape)]:
            key = tuple(tuple(row) for row in f)
            if key not in seen:
                seen.add(key)
                variants.append(copy.deepcopy(f))
    return variants

# --- shapes ---
shape_list = [
    [[1,1]],       # shape 0
    [[1,1],[1,0]],  # shape 1
    [[1,1,1]]  # shape 2
]

shape_list = [
    [[1,1,1],[1,0,0],[1,0,0]],      # shape bigL
    [[1,1,1],[0,1,0],[0,1,0]],      # shape T
    [[1,1,0],[0,1,0],[0,1,1]],      # shape bigS
    [[1,1,1,1],[1,0,0,0]],          # shape long L
    [[1,1,1,0],[0,0,1,1]],          # shape long S
    [[1,1,1,1]],                    # shape long I
    [[1,1,1],[1,0,1]],              # shape U
    [[1,1,1],[1,1,0]],              # shape wierd P
    [[1,1,1],[0,0,1]],              # shape L
    [[0,1,1],[1,1,0]],              # shape S
    
]


# Get max shape lenght to generate the rotated shapes later.
max_shape_length = max(len(row) for shape in shape_list for row in shape)


all_variants = []
num_variants = []

for shape in shape_list:
    variants = generate_variants(shape)
    all_variants.append(variants)
    num_variants.append(len(variants))

# ---------------------
# --- board ---
# ---------------------
board_numbers = [
    [1, 2,-1],
    [3, 4, 5],
    [6, -1,-1]
]

board = [
    [0, 0,0],
    [0, 0,0],
    [0, 0,0]
]

board = [
    [0,0,0,0,0,0,1],
    [0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [1,1,1,1,0,0,0],
]


num_rows = len(board)
num_cols = len(board[0])


uncovered = [(1,5),(5,5),(7,5)]  # 0-based row,col

num_uncovered = len(uncovered)


# ---------------------
# Generate C header
# ---------------------
header_content = f"""
// Auto-generated board data
#define ROWS {num_rows}
#define COLS {num_cols}
#define MAX_SHAPE_LEN {max_shape_length}
#define NUM_SHAPES {len(shape_list)}
/*
Board definition: 0 means free spot, 1 means its covered, either from the getgo or from the placed shape.
*/

int board[ROWS][COLS] = {{
"""
header_content += f"\n"

for row in board:
    header_content += "    {" + ",".join(str(x) for x in row) + "},\n"
header_content += "};\n"

header_content += f"int board_og[ROWS][COLS] = {{ \n"

for row in board:
    header_content += "    {" + ",".join(str(x) for x in row) + "},\n"
header_content += "};\n"

# uncovered
header_content += f"int uncovered[{num_uncovered}][2] = {{"
for i in range(num_uncovered):
    header_content += f"{{ {uncovered[i][0]},{uncovered[i][1]} }}, \n"
    pass
header_content += "} ;\n"
header_content += f"int num_uncovered = {num_uncovered};\n"

header_content += f"int num_variants[{len(shape_list)}] = {{{','.join(str(n) for n in num_variants)}}};\n\n"


# Build the big 4D array
header_content += f"int shapes[{len(shape_list)}][8][MAX_SHAPE_LEN][MAX_SHAPE_LEN] = {{ \t\t//[shape_id][rot*flip][row][col] \n"  # 8 = max variants, 
for s, variants in enumerate(all_variants):
    header_content += "  {\n"
    for v in range(8):
        if v < len(variants):
            var = variants[v]
            header_content += "    {\n"
            for r in range(max_shape_length):
                row_vals = []
                if r < len(var):
                    row_vals = var[r] + [0]*(max_shape_length-len(var[r]))
                else:
                    row_vals = [0] * max_shape_length
                header_content += "      {" + ",".join(str(x) for x in row_vals) + "},\n"
            header_content += "    },\n"
        else:
            # empty variant
            header_content += "    {"
            row_vals = [0] * max_shape_length
            for i in range(max_shape_length):
                header_content += "{" + ",".join(str(x) for x in row_vals) + "},"
                pass
            header_content += "},\n"
    header_content += "  },\n"
header_content += "};\n"

with open("board_data.h", "w") as f:
    f.write(header_content)

print("Generated board_data.h")