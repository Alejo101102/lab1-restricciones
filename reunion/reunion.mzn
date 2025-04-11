include "globals.mzn";

%=== Parámetros ===

int: n;
array[1..n] of string: personas;

%=== Variables ===

array[1..n] of var 1..n: posicion;

% === Restricciones ===

constraint all_different(posicion);

% === Next ===
array[_, 1..2] of int: next;
constraint
    forall(i in index_set_1of2(next)) (
        abs(posicion[next[i,1]] - posicion[next[i,2]]) = 1
    );

% === Separate ===
array[_, 1..2] of int: separate;
constraint
    forall(i in index_set_1of2(separate)) (
        abs(posicion[separate[i,1]] - posicion[separate[i,2]]) > 1
    );

% === Distance ===
array[_, 1..3] of int: distance;
constraint
    forall(i in index_set_1of2(distance)) (
        abs(posicion[distance[i,1]] - posicion[distance[i,2]]) <= distance[i,3]
    );

% === Redundancias ===

% === Redundancia para NEXT (bordes extremos) ===
constraint
    forall(i in index_set_1of2(next)) (
        (posicion[next[i,1]] = 1 -> posicion[next[i,2]] = 2) /\
        (posicion[next[i,1]] = n -> posicion[next[i,2]] = n-1)
    );

% === Redundancia para Separate ===
constraint
    forall(i in index_set_1of2(separate)) (
        posicion[separate[i,1]] - posicion[separate[i,2]] > 1 \/
        posicion[separate[i,2]] - posicion[separate[i,1]] > 1
    );

% === Simetría ===
constraint
    if not exists(i,j in index_set_1of2(next)) ( next[i,1] != next[j,2] ) then
        posicion[1] < posicion[n]
    else true endif;

solve satisfy;
%solve :: int_search([tabla[i, j] | i in 1..9, j in 1..9], first_fail, indomain_min, complete) satisfy;
%solve :: int_search([tabla[i, j] | i in 1..9, j in 1..9], first_fail, indomain_split) satisfy;
%solve :: int_search([tabla[i, j] | i in 1..9, j in 1..9], first_fail, indomain_split) satisfy;
%solve :: int_search([tabla[i, j] | i in 1..9, j in 1..9], input_order, indomain_min) satisfy;

% === OUTPUT ===
output [
  "Fila real:\n",
  concat([
    personas[i] ++ if p < n then " - " else "\n" endif
    | p in 1..n, i in 1..n where fix(posicion[i]) = p
  ])
];
