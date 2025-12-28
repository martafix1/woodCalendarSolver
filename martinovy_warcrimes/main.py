from solver import *
from benchmark import run_benchmark


shapez = [
    [[1,1,1],
     [1,0,1]],

    [[1,1,1,1]],

    [[1,1,1],
     [0,1,0],
     [0,1,0]],

    [[1,1,0],
     [0,1,1]],

    [[1,1,1],
     [0,0,1]],

    [[1,1,1],
     [1,1,0]],

    [[1,1,1],
     [0,0,1],
     [0,0,1]],

    [[1,1,1,0],
     [0,0,1,1]],

    [[1,1,0],
     [0,1,0],
     [0,1,1]],

    [[1,1,1,1],
     [0,0,0,1]],
]

ROWS = 8
COLUMNS = 7

obstacles = [[0,6],[1,6],[7,0],[7,1],[7,2],[7,3]]
# user_obstacles = [[1,0], [5,5], [6,4]]
# obstacles.extend(user_obstacles)
#
# s = Solver(shapez, obstacles, ROWS, COLUMNS)
# solution = s.solve()


run_benchmark(shapez, obstacles, ROWS, COLUMNS)

