% Use this editor as a MiniZinc scratch book
include "globals.mzn";

% Definición de variables y dominio
array[1..9, 1..9] of var 1..9: tabla;

% Declaración de la matriz de entrada desde archivo .dzn
array[1..9, 1..9] of int: tabla_inicial;

% Restricciones de filas
constraint forall(i in 1..9)(all_different([tabla[i, j] | j in 1..9]));

% Restricciones de columnas
constraint forall(j in 1..9)(all_different([tabla[i, j] | i in 1..9]));

% Restricciones de subcuadrículas 3x3
constraint forall(r in 0..2, c in 0..2)
  (all_different([tabla[3*r + i, 3*c + j] | i in 1..3, j in 1..3]));

% Fijar valores predefinidos en la cuadrícula
constraint forall(i in 1..9, j in 1..9 where tabla_inicial[i, j] > 0)
  (tabla[i, j] = tabla_inicial[i, j]);

% Estrategia de búsqueda (probando diferentes enfoques)
solve satisfy;
% solve :: int_search([grid[i, j] | i in 1..9, j in 1..9], first_fail, indomain_min, complete);

% Salida de resultados
output [ if j == 9 then show(tabla[i, j]) ++ "\n" else show(tabla[i, j]) ++ " " endif 
         | i in 1..9, j in 1..9 ];
