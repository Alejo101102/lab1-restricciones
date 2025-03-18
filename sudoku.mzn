% Sudoku en MiniZinc
include "globals.mzn";

int: n = 9;
array[1..n, 1..n] of var 1..9: grid;

constraint
    forall(i in 1..n)(
        alldifferent([grid[i, j] | j in 1..n])
    )
    /\
    forall(j in 1..n)(
        alldifferent([grid[i, j] | i in 1..n])
    )
    /\
    forall(i in 0..2, j in 0..2)(
        alldifferent([grid[3*i + di, 3*j + dj] | di in 1..3, dj in 1..3])
    );

solve satisfy;