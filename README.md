# That cursed board of wooden pieces you are supposed to arrange such that the only uncovered cells define current date

I'm unaware of existence of a smart approach to that problem, in to my knowledge you just need to be lucky and patient.
It takes a person rougly 20-40mins to complete one solution.

So I went on and created solvers for this:
- Python only solver
- Optimized solver in C with static arrays, uses generated data header file

# Python only solver
Works, takes rougly 2h per solution (~64M placed pieces)

# Optimized C solver
Uses `solver_StaticC_gen.py` to generate a header file called 'board_data.h'. This is then used by the actuall solver, currently `solve_v2.c`. 
The `solver_StaticC_main.py` was supposed to auto generate, compile and run all but setting the compilers sucks so WIP.

The average time per solution is 0.8s :D. 

## How to use
Set the uncovered positions in the `solver_StaticC_gen.py` file, line 87 at time of writing this: 
`uncovered = [(1,5),(5,5),(7,5)]  # 0-based row,col`
Run the python file to regenerate `board_data.h`. Its kinda human readable so check it out that its correct.
Compile and run the `solve_v2.c`, it will spit out the valid shape states into the cmd. 

### Currently
- currently it will run until it finds all solutions or reaches 6969 solutions. 
- currently it does not display the board, but that can be easily reenableded by uncomenting the `// printBoardState(shape_states,NUM_SHAPES); ` for example on line 447 in the solution found if, solve() function.


## info
It transforms the board into a flat array, and transforms the shapes into noodles of offset indexes where the shape is on the flat board. This makes it efficient. I think.
It was supposed to use "unsigned long long iter" as uniqe key to describe all possible states of the shapes to allow for tracking of states. However this value might be overflowing so I fell back to the shapestates as descriptor. If time be I'll return, maybe split it into two %llu s or use some bigger numbers.



# Feel free to upgrade.
It should be quite easy to paralelize this in Cpp, you can just ofset the first shape position for each new thread, this gives still giant statespace for the threads to search.








