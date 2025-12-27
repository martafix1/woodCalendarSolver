#include "board_data.h"
#include <stdio.h>

int main(int argc, char const *argv[])
{
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
    return 0;
}



