import copy

baseMatrix = [
    [1,2,3,4,5,6,-1],
    [7,8,9,10,11,12,-1],
    [1,2,3,4,5,6,7],
    [8,9,10,11,12,13,14],
    [15,16,17,18,19,20,21],
    [22,23,24,25,26,27,28],
    [29,30,31,1,2,3,4],
    [-1,-1,-1,-1,5,6,7]
]

uncovered = {(1,5), (5,5), (7,5)}  # (row,col) of 12, 27, 5 (0-based)

shapes = {
    "a": [[1,1,0],[0,1,1]],
    "b": [[1,1,1],[0,0,1]],
    "c": [[1,1,1],[1,0,1]],
    "d": [[1,1,1,1],[0,0,0,1]],
    "e": [[1,1,1,0],[0,0,1,1]],
    "f": [[1,1,1],[0,0,1],[0,0,1]],
    "g": [[1,1,1,1]],
    "h": [[1,1,1],[1,1,0]],
    "i": [[1,1,1],[0,1,0],[0,1,0]],
    "j": [[1,1,0],[0,1,0],[0,1,1]],
}

ROWS, COLS = 8, 7

iterations = 0

def rotations_and_flips(shape):
    variants = set()
    s = shape
    for _ in range(4):
        s = list(zip(*s[::-1]))
        variants.add(tuple(tuple(r) for r in s))
        variants.add(tuple(tuple(r[::-1]) for r in s))
    return [list(map(list, v)) for v in variants]

shape_variants = {k: rotations_and_flips(v) for k,v in shapes.items()}

board = [[None if baseMatrix[r][c] != -1 else "#" for c in range(COLS)] for r in range(ROWS)]

def can_place(shape, r, c):
    for i in range(len(shape)):
        for j in range(len(shape[0])):
            if shape[i][j]:
                rr, cc = r+i, c+j
                if rr>=ROWS or cc>=COLS: return False
                if board[rr][cc] is not None: return False
                if (rr,cc) in uncovered: return False
    return True

def place(shape, r, c, label):
    for i in range(len(shape)):
        for j in range(len(shape[0])):
            if shape[i][j]:
                board[r+i][c+j] = label

def remove(shape, r, c):
    for i in range(len(shape)):
        for j in range(len(shape[0])):
            if shape[i][j]:
                board[r+i][c+j] = None

counter = {"calls": 0}

def solve(keys, idx=0,iterations=0):
    if idx == len(keys):
        return True
    key = keys[idx]
    for variant in shape_variants[key]:
        for r in range(ROWS):
            for c in range(COLS):
                if can_place(variant, r, c):
                    if counter["calls"] % 1000 == 0:
                        print(f"Iter: {counter["calls"]} ")
                    place(variant, r, c, key)
                    if solve(keys, idx+1,iterations):
                        return True
                    remove(variant, r, c)
                    counter["calls"] += 1
    return False

solve(list(shapes.keys()))

for row in board:
    print(row)