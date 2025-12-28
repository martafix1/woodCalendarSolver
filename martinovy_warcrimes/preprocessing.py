

def rotate(shape):
    rows = len(shape)
    cols = len(shape[0])

    rotated = [[shape[rows-nc-1][nr] for nc in range(rows)] for nr in range(cols)]
    return rotated

def flip(shape):
    return shape[::-1]

def create_unique_variants(shapes):
    variants = []
    intervals = []
    last_interval_end = 0

    for shape in shapes:
        unique_variants = []
        unique_variants_str = []
        last_rot = shape
        for r in range(4):
            shape_r = rotate(last_rot)
            shape_r_str = str(shape_r)
            if shape_r_str not in unique_variants_str:
                unique_variants.append(shape_r)
                unique_variants_str.append(shape_r_str)

            shape_f = flip(shape_r)
            shape_f_str = str(shape_f)
            if shape_f_str not in unique_variants_str:
                unique_variants.append(shape_f)
                unique_variants_str.append(shape_f_str)

            last_rot = shape_r

        variants.extend(unique_variants)

        interval_start = last_interval_end
        interval_end = interval_start + len(unique_variants)
        intervals.append((interval_start, interval_end))
        last_interval_end = interval_end

    return variants, intervals


def print_shape(shape):
    for r in shape:
        print(r)
    print("----------")


def flatten(shape, grid_cols):
    filler = [0 for i in range(grid_cols - len(shape[0]))]
    flat = []
    for i, row in enumerate(shape):
        flat.extend(row)
        if i != len(shape) - 1:
            flat.extend(filler)
    tail_padding = flat[::-1].index(1)
    return flat if tail_padding == 0 else flat[:-tail_padding]

def find_invalid_offsets(anchor_shape, other_shape):
    invalid_offsets = set()
    for i in range(len(anchor_shape)):
        for a, o in zip(anchor_shape[i:], other_shape):
            if a + o == 2:
                invalid_offsets.add(i)
                break
    return invalid_offsets

def rc2offset(point, COLS):
    return point[0] * COLS + point[1]

def get_invalid_offset_table(unique_variations_flat, intervals ,COLS):
    table = [[None for _ in unique_variations_flat] for _ in unique_variations_flat]
    interval_index = 0

    for asi, anchor_shape in enumerate(unique_variations_flat):
        interval = intervals[interval_index]

        for osi, offset_shape in enumerate(unique_variations_flat):
            if osi >= interval[0] and osi < interval[1]:
                continue
            table[asi][osi] = find_invalid_offsets(anchor_shape, offset_shape)

        if asi + 1 >= interval[1]:
            interval_index += 1

    return table

def get_interval_sets(intervals):
    sets = []
    for i in intervals:
        repetition = i[1] - i[0]
        for r in range(repetition):
            sets.append(set(range(i[0], i[1])))
    return sets
