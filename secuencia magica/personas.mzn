include "globals.mzn";

int: n;
array[1..n] of string: personas;
array[1..n] of var 1..n: posicion;

constraint all_different(posicion);

% --- Restricciones tipo NEXT ---
array[_, 1..2] of int: next;
constraint
    forall(i in index_set_1of2(next)) (
        abs(posicion[next[i,1]] - posicion[next[i,2]]) = 1
    );

% --- Restricciones tipo SEPARATE ---
array[_, 1..2] of int: separate;
constraint
    forall(i in index_set_1of2(separate)) (
        abs(posicion[separate[i,1]] - posicion[separate[i,2]]) > 1
    );

% --- Restricciones tipo DISTANCE ---
array[_, 1..3] of int: distance;
constraint
    forall(i in index_set_1of2(distance)) (
        abs(posicion[distance[i,1]] - posicion[distance[i,2]]) = distance[i,3]
    );

constraint posicion[1] < posicion[n];
    
% === OUTPUT ===
output [
  "Fila real:\\n",
  concat([
    personas[i] ++ if p < n then " - " else "\\n" endif
    | p in 1..n, i in 1..n where fix(posicion[i]) = p
  ])
];
