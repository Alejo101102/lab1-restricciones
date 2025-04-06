% ==============================
% Parámetros
% ==============================
include "globals.mzn";


% ==============================
% Romper simetría
% ==============================

constraint posicion[1] = 1;


% ==============================
% Dominio
% ==============================

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
% Restricciones redundantes
% ==============================

% Si dos personas deben estar juntas ("next"), entonces su diferencia absoluta debe ser 1.
constraint forall(i in 1..m_next) (
    posicion[next[i,1]] + 1 = posicion[next[i,2]] \/ posicion[next[i,1]] - 1 = posicion[next[i,2]]
);

% Si dos personas no deben estar juntas ("separate"), entonces su diferencia absoluta debe ser al menos 2.
constraint forall(i in 1..m_separate) (
    abs(posicion[separate[i,1]] - posicion[separate[i,2]]) >= 2
);

% Si dos personas tienen una distancia exacta ("distance"), entonces su posición debe cumplir con esa distancia.
constraint forall(i in 1..m_distance) (
    posicion[distance[i,1]] + distance[i,3] = posicion[distance[i,2]] \/
    posicion[distance[i,1]] - distance[i,3] = posicion[distance[i,2]]
);

% ==============================
% Estrategia de búsqueda
% ==============================

% Estrategia por defecto

%solve satisfy;

% Otras estrategias posibles para experimentar:
%solve :: int_search(posicion, first_fail, indomain_min, complete) satisfy;
%solve :: int_search(posicion, dom_w_deg, indomain_split) satisfy;
%solve :: int_search(posicion, input_order, indomain_min) satisfy;
%solve :: int_search(posicion, occurrence, indomain_max) satisfy;

% ==============================
% Salida de resultados
% ==============================

output ["Orden de la fila: " ++ join(", ", [personas[i] ++ " en posición " ++ show(posicion[i]) | i in 1..n])];