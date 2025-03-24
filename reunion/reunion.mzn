% ==============================
% Parámetros
% ==============================
include "globals.mzn";


int: n;  % Número de personas
array[1..n] of string: personas;

int: m_next;
array[1..1, 1..2] of int: next;  % Restricciones de "next"

int: m_separate;
array[1..1, 1..2] of int: separate;  % Restricciones de "separate"

int: m_distance;
array[1..1, 1..3] of int: distance;  % Restricciones de "distance"

% ==============================
% Variables
% ==============================

array[1..n] of var 1..n: posicion;  % Posición de cada persona en la fila

% ==============================
% Restricciones
% ==============================

% Cada persona debe ocupar una posición única
constraint all_different(posicion);

% Restricción "next": deben estar juntos en la fila
constraint forall(i in 1..m_next) (
    abs(posicion[next[i,1]] - posicion[next[i,2]]) = 1
);

% Restricción "separate": no deben estar juntos
constraint forall(i in 1..m_separate) (
    abs(posicion[separate[i,1]] - posicion[separate[i,2]]) > 1
);

% Restricción "distance": deben mantener una distancia exacta
constraint forall(i in 1..m_distance) (
    abs(posicion[distance[i,1]] - posicion[distance[i,2]]) = distance[i,3]
);

% ==============================
% Resolución
% ==============================

solve satisfy;

% ==============================
% Salida de resultados
% ==============================

output ["Orden de la fila: " ++ join(", ", [personas[i] ++ " en posición " ++ show(posicion[i]) | i in 1..n])];