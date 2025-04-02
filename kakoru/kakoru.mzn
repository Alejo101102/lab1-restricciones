include "globals.mzn";

% Parámetros
int: n; % Tamaño del tablero (n x n)
int: G; % Representación de las celdas negras
int: num_pistas_filas; % Número de pistas en las filas
int: num_pistas_columnas; % Número de pistas en las columnas

% Pistas para las filas y columnas
array[1..n, 1..n] of int: pistas_filas;
array[1..n, 1..n] of int: pistas_columnas;

% Sumas de las pistas
array[1..num_pistas_filas] of int: sumas_pistas_filas;
array[1..num_pistas_columnas] of int: sumas_pistas_columnas;

% Variables de decisión
array[1..n, 1..n] of var 0..9: tablero;

% Estrategia de búsqueda
solve :: int_search([tablero[i, j] | i, j in 1..n], first_fail, indomain_max, complete) satisfy;

% Restricciones
constraint
    % Manejo de celdas negras
    forall(i, j in 1..n) (
        if pistas_filas[i, j] = G then
            tablero[i, j] = 0
        else
            tablero[i, j] > 0
        endif
    )
    /\
    % Restricciones para las filas
    forall(p in 1..num_pistas_filas) (
        sumas_pistas_filas[p] = sum(i, j in 1..n where pistas_filas[i, j] = p) (tablero[i, j])
        /\
        alldifferent([tablero[i, j] | i, j in 1..n where pistas_filas[i, j] = p])
    )
    /\
    % Restricciones para las columnas
    forall(p in 1..num_pistas_columnas) (
        sumas_pistas_columnas[p] = sum(i, j in 1..n where pistas_columnas[i, j] = p + num_pistas_filas) (tablero[i, j])
        /\
        alldifferent([tablero[i, j] | i, j in 1..n where pistas_columnas[i, j] = p + num_pistas_filas])
    );

% Salida
output [
    if j = 1 then "\n" else " " endif ++
    show(tablero[i, j])
    | i, j in 1..n
];