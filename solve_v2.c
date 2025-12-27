#include "board_data.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>


/*For this version, the board is casted as falt and the shapes are remebered as flat indexes of only positive values*/


int *flat_board = &board[0][0];
#define IDX(r, c) ((r) * COLS + (c))
//flat[IDX(3,3)] = 1; // how to use

//for the same flat reason we will use flattened shapes, which actaully allow the speedup i believe:
int flat_shapes[NUM_SHAPES][8][MAX_SHAPE_LEN*MAX_SHAPE_LEN] = {0};
int flatened_shape_size[NUM_SHAPES] = {0};

void flatten_shapes(){
    for(int s=0; s<NUM_SHAPES; s++){
        for(int v=0; v<num_variants[s]; v++){
            int on_shape_IDX = 0;
            for(int r=0; r<MAX_SHAPE_LEN; r++){
                for(int c=0; c<MAX_SHAPE_LEN; c++){
                    if(shapes[s][v][r][c] == 1){
                        
                        flat_shapes[s][v][on_shape_IDX] = IDX(r,c);
                        ++on_shape_IDX;
                    }
                    
                }
                
            }
            for(int i = on_shape_IDX; i < MAX_SHAPE_LEN*MAX_SHAPE_LEN;i++ ){
                flat_shapes[s][v][i]= -1; // fill the rest with -1 for giggles
            }
            if(v==0){ // shape have same size for all variants
                flatened_shape_size[s] = on_shape_IDX;
            }
            
            
        }
    }


}

void printFlattenedShapes(){
    for(int s=0; s<NUM_SHAPES; s++){
        for(int v=0; v<num_variants[s]; v++){
            printf("Shape %d variant %d: (%d) [", s, v, flatened_shape_size[s]);
            for(int i=0; i<MAX_SHAPE_LEN*MAX_SHAPE_LEN; i++){
               printf(" %d,",flat_shapes[s][v][i]);
            }
            printf("] \n");
        }
    }


}



// for debug
void printAllShapes(){
    for(int s=0; s<NUM_SHAPES; s++){
        for(int v=0; v<num_variants[s]; v++){
            printf("Shape %d variant %d:\n", s, v);
            for(int r=0; r<MAX_SHAPE_LEN; r++){
                for(int c=0; c<MAX_SHAPE_LEN; c++){
                    printf("%d ", shapes[s][v][r][c]);
                }
                printf("\n");
            }
            printf("\n");
        }
    }

}


void coverBoard(){
    for(int i =0; i<num_uncovered;i++)
    {
        int r = uncovered[i][0];
        int c = uncovered[i][1];
        board[r][c] = 1;

    }

}


// actuall solving
// input: shape, variant, offsetIDX
// returns 1 for valid
int tryToPlaceShape(int s, int v, int idx){

    for(int i = 0; i<flatened_shape_size[s];++i){
        int pos_flat_og = flat_shapes[s][v][i];
        if( (pos_flat_og % COLS) +  (idx % COLS) >= COLS ) //shape wrapping around the right edge, therefore invalid placement
            return -1;
        if(pos_flat_og + idx >= ROWS*COLS) //shape wrapping around the bottom edge, therefore invalid    
            return -2;
        
        if(flat_board[ pos_flat_og+idx ] > 0) //the space is already occupied
            return -3;
            
    }

    return 1;

}

void placeShape(int s, int v, int idx){
   for(int i = 0; i<flatened_shape_size[s];++i){
    flat_board[ flat_shapes[s][v][i] + idx ] = 1;
   } 
}
void removeShape(int s, int v, int idx){
   for(int i = 0; i<flatened_shape_size[s];++i){
    flat_board[ flat_shapes[s][v][i] + idx ] = 0;
   } 
}

// for solving with single iteration variable to describe all the states a bit of a setup is needed.
// something about a radix math.
# define ULL_t unsigned long long

unsigned int    choices[NUM_SHAPES] = {0};
ULL_t           radix[NUM_SHAPES] = {0};

typedef struct {
    int variant;
    int position;
} ShapeState;

void setup_iter2state_mapping(){
    int N = ROWS * COLS;  // number of positions on board

    // Step 1: compute total choices per shape
    for (int i = 0; i < NUM_SHAPES; i++)
        choices[i] = num_variants[i] * N;

    // Step 2: compute radix array (product of choices for lower shapes)
    radix[NUM_SHAPES - 1] = 1;
    for (int i = NUM_SHAPES - 2; i >= 0; i--)
        radix[i] = radix[i + 1] * choices[i + 1];

}

void iter2shape_state(ULL_t iter, ShapeState shape_states[NUM_SHAPES]){
    //map iteration to each shape's variant & position
    int N = ROWS * COLS;
    ULL_t remainder = iter;
    for (int i = 0; i < NUM_SHAPES; i++) {
        unsigned int idx = (remainder / radix[i]) % choices[i];
        shape_states[i].variant = idx / N;
        shape_states[i].position = idx % N;

        remainder -= idx * radix[i];
    }

}

ULL_t shape_state2iter(ShapeState shape_states[NUM_SHAPES]){
    //map iteration to each shape's variant & position
    int N = ROWS * COLS;
    ULL_t iter = 0;
    for (int i = 0; i < NUM_SHAPES; i++) {
        ULL_t idx = shape_states[i].variant * N + shape_states[i].position;
        iter += idx * radix[i];
    }

    return iter;

}

void printShapeStates(ShapeState shape_states[NUM_SHAPES],int doNewLine){
    for(int s = 0;s<NUM_SHAPES;s++){
        int v = shape_states[s].variant;
        int i = shape_states[s].position;
        printf("(%d):%d, %d/ ",s,v,i);
    }
    printf("\b\b");
    // ULL_t iter = shape_state2iter(shape_states);
    // printf("/ iter: %llu ",iter);
    if(doNewLine){
        printf("\n");
    }
    


}

void printBoardState(ShapeState shape_states[NUM_SHAPES],int depth){

    printf("Current shape state: \n");
    printShapeStates(shape_states,1);
    
    printf("Equivalent board state: \n");
    int print_board[ROWS][COLS] = {0};
    int *flat_print_board = &print_board[0][0];
    int *flat_og_board = &board_og[0][0];
    for(int i=0;i<ROWS*COLS;i++){
        if( flat_og_board[i] == 1)
            {flat_print_board[i] = -1;}
        else
        {
            flat_print_board[i] = -3;
        }
    }

    for(int i = 0;i<num_uncovered;i++){
        print_board[uncovered[i][0]][uncovered[i][1]]=-2;

    }


    for(int s = 0;s<depth;s++){
        int v = shape_states[s].variant;
        int p = shape_states[s].position;
        for(int i = 0; i<flatened_shape_size[s];++i){
            flat_print_board[ flat_shapes[s][v][i]+p ] = s;
        } 
    }

    for(int r = 0;r<ROWS;r++){
        for(int c = 0;c<COLS;c++)
        {
            int val = print_board[r][c];
            
            if(val < 0){
                if(val == -2){
                printf("X");    
                }
                else if (val == -3)
                {
                    printf(".");
                }
                else{
                printf("#");    
                }
                
            }
            else{
                printf("%c", 'a' + val);
            }

        }
        printf("\n");
    }

    //#define kekeke
    #ifdef kekeke
    printf("OG: \n");
    for(int r = 0;r<ROWS;r++){
        for(int c = 0;c<COLS;c++)
        {
            int val = board[r][c];
            if(NUM_SHAPES>9){ // need two chars per shape
                
                if(val < 0){
                    if(val == -2){
                    printf("XX ");    
                    }
                    else if (val == -3)
                    {
                        printf("L_ ");
                    }
                    
                    else{
                    printf("## ");    
                    }
                    
                }
                else{
                    printf("%2d ",val);
                }
                
            }
            else{

                if(val < 0){
                    if(val == -2){
                    printf("X");    
                    }
                    else if (val == -3)
                    {
                        printf("L");
                    }
                    else{
                    printf("#");    
                    }
                }
                else{
                    printf("%1d",val);
                }
            }

        }
        if(NUM_SHAPES>9){printf("\n\n");}
        else{printf("\n");}
    }
    #endif
    
  
}

void print_dataBoardState(){
    for(int r = 0;r<ROWS;r++){
        for(int c = 0;c<COLS;c++)
        {
            int val = board[r][c];
            printf("%1d",val);

        }
        printf("\n");
    }

}

ULL_t totalIterations_M = 0;


int solve(ShapeState shape_states[NUM_SHAPES], ShapeState result[NUM_SHAPES]){

setup_iter2state_mapping();

int run = 1;
// printf("starting state: ");
// printShapeStates(shape_states,1);

clock_t solve_start = clock();

ULL_t simpleIterations = 0;
int N = ROWS*COLS;
int depth = 0;
int ret = -69;
int noSolutionFound = 0;
int skipPlacementToMove = 0;
while (run)
{   
    //printShapeStates(shape_states,0);
    ret = tryToPlaceShape(depth,shape_states[depth].variant,shape_states[depth].position);
    //printf("ret: %d\n",ret);
    if(skipPlacementToMove == 1){
        ret = 0;
        skipPlacementToMove = 0;
        simpleIterations -=1;
    }
    if(ret == 1) // success of placement
    {
        placeShape(depth,shape_states[depth].variant,shape_states[depth].position);
        depth+=1;
        if(depth >= NUM_SHAPES){
            run = 0;
            //clear board for next run
            for(int d=depth-1;d>=0;d--){
                depth = d;
                removeShape(depth,shape_states[depth].variant,shape_states[depth].position);
                //printf("Removed shape at depth %d \n",depth);
            }
            //printBoardState(shape_states,depth);
            //print_dataBoardState();

        }
        //printBoardState(shape_states,depth);
    }
    else //could not place
    {
        //try to increment position
        if(shape_states[depth].position < N-1)
        {
            shape_states[depth].position+=1;
        }
        else
        {
            //reset position
            shape_states[depth].position=0;

            // try to increment varant
            if(shape_states[depth].variant < num_variants[depth]-1){
                shape_states[depth].variant +=1;    
            }
            else
            {
                //reset variant
                shape_states[depth].variant =0;   

                //try to decrement depth
                if(depth > 0){
                    depth -=1;
                    //remove previously placed shape
                    removeShape(depth,shape_states[depth].variant,shape_states[depth].position);

                    //increment previous depth state.
                    skipPlacementToMove = 1;


                }
                else // no solution found
                {
                    run = 0;
                    noSolutionFound = 1;
                }
            }

        }
    }
    
    simpleIterations += 1;

    // if(simpleIterations % 10000000 == 0){
    //     printf("simple: %lluM \n",simpleIterations/1000000);

    //     //printBoardState(shape_states);
    // }




}



//printf("Simple iterations: %llu \n",simpleIterations);
totalIterations_M += simpleIterations/(1000*1000);

clock_t solve_end = clock();

double solve_time = (double)(solve_end - solve_start) / CLOCKS_PER_SEC;
double time_per_million = (simpleIterations > 0) ? (solve_time / (simpleIterations / 1000000.0)) : 0.0;
//printf("Solve time: %.3f seconds, Time per 1M iterations: %.3f seconds\n", solve_time, time_per_million);



if(noSolutionFound){
    printf("Solution does not exist!");
    printf(" iters: %10llu, total: %lluM / took %.3f [s], 1M iters: %.3f [s] ",simpleIterations,totalIterations_M,solve_time,time_per_million);
    printShapeStates(shape_states,1);
    return 0;
}
else{
    printf("found!");
    printf(" iters: %10llu, total: %lluM / took %.3f [s], 1M iters: %.3f [s] ",simpleIterations,totalIterations_M,solve_time,time_per_million);
    printShapeStates(shape_states,1);
    // printBoardState(shape_states,NUM_SHAPES);
    // Copy solution to result array
    for(int i = 0; i < NUM_SHAPES; i++) {
        result[i] = shape_states[i];
    }
    return 1;
}

}

// to test the iter integrity
unsigned long long random_ull() {
    unsigned long long val = 0;
    for (int i = 0; i < 4; i++) {
        val = (val << 16) | (rand() & 0xFFFF);
    }
    return val;
}

#define MAX_SOLUTIONS 6969

int main(int argc, char const *argv[])
{
    srand(time(NULL));
    ShapeState solutions[MAX_SOLUTIONS][NUM_SHAPES];  // array of completed shape states
    int num_solutions = 0; 
    
    clock_t total_start = clock();
    
    printAllShapes();// for debug
    coverBoard();
    flatten_shapes();
    printFlattenedShapes();


    while(num_solutions < MAX_SOLUTIONS)
    {   
        ShapeState current_state[NUM_SHAPES] = {0};  // start state (all zeros)
        ShapeState result_state[NUM_SHAPES];         // to hold solution
        
        if(num_solutions > 0)
        {
            // Copy previous solution as starting point
            for(int i = 0; i < NUM_SHAPES; i++) {
                current_state[i] = solutions[num_solutions-1][i];
            }
            // Increment to next state
            int d = NUM_SHAPES - 1;
            int N = ROWS * COLS;
            while(d >= 0) {
                if(current_state[d].position < N-1) {
                    current_state[d].position += 1;
                    break;
                } else {
                    current_state[d].position = 0;
                    if(current_state[d].variant < num_variants[d]-1) {
                        current_state[d].variant += 1;
                        break;
                    } else {
                        current_state[d].variant = 0;
                        d--;
                    }
                }
            }
        }
        printf("Solution %d: ",num_solutions);
        int found = solve(current_state, result_state);
        if(found)
        {
            // Copy result to solutions array
            for(int i = 0; i < NUM_SHAPES; i++) {
                solutions[num_solutions][i] = result_state[i];
            }
            num_solutions+=1;
        }
        else
        {
            break;  // no more solutions
        }
    }
    
    clock_t total_end = clock();
    double total_time = (double)(total_end - total_start) / CLOCKS_PER_SEC;
    
    printf("\n=== FINAL STATS ===\n");
    printf("Total solutions found: %d\n", num_solutions);
    printf("Total time: %.3f seconds\n", total_time);
    printf("Average time per solution: %.3f seconds\n", (num_solutions > 0) ? (total_time / num_solutions) : 0.0);



    return 0;
}






/*

int run = 100;
    setup_iter2state_mapping();
    ShapeState shape_states[NUM_SHAPES];
    ULL_t iters = 0;
    while (run>0)
    {   
        iters +=1;
        ULL_t testIter = random_ull();
        iter2shape_state(testIter,shape_states);
        ULL_t returnIter = shape_state2iter(shape_states);
        if(returnIter != testIter)
        {
            run -=1;
            printf("in: %llu, out: %llu - dont match. \n In shape states: ");
            printShapeStates(shape_states,1);
        }

        if(iters % 1000000 == 0){
            printf("Testing, iters: %llu \n",iters);
        }

    }
    
    return 0;*/