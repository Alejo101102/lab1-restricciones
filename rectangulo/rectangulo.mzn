% ==============================
% MiniZinc - Empaque de Cuadrados
% ==============================

% --------------------------------
% Inclusión de librerías
% --------------------------------
include "lex_lesseq.mzn";

% ==============================
% Parámetros
% ==============================
int: W;  % Ancho del rectángulo
int: H;  % Alto del rectángulo
int: n;  % Número de cuadrados
array[1..n] of int: sizes;  % Tamaño (lado) de cada cuadrado

% ==============================
% Variables
% ==============================
array[1..n] of var 0..W-1: x;  % Coordenada x (esquina inferior izquierda)
array[1..n] of var 0..H-1: y;  % Coordenada y (esquina inferior izquierda)

% ==============================
% Restricciones
% ==============================

% Cada cuadrado debe estar completamente dentro del rectángulo
constraint forall(i in 1..n)(
    x[i] + sizes[i] <= W /\
    y[i] + sizes[i] <= H
);

% Ningún par de cuadrados debe solaparse
constraint forall(i, j in 1..n where i < j)(
    x[i] + sizes[i] <= x[j] \/
    x[j] + sizes[j] <= x[i] \/
    y[i] + sizes[i] <= y[j] \/
    y[j] + sizes[j] <= y[i]
);

% El área total de los cuadrados debe ser igual al área del rectángulo
constraint W * H = sum(i in 1..n)(sizes[i] * sizes[i]);

% ==============================
% Restriccion de Rompimiento de Simetría
% ==============================

% Rompimiento de simetría: ordenar cuadrados del mismo tamaño
constraint forall(i, j in 1..n where i < j /\ sizes[i] = sizes[j]) (
    lex_lesseq([x[i], y[i]], [x[j], y[j]])
);

% ==============================
% Estrategia de búsqueda
% ==============================
solve satisfy;

% ==============================
% Salida de resultados
% ==============================
output [
  "Coordenadas de los cuadrados:\n"
] ++
[
  "Cuadrado\(i):(x=\(x[i]),y=\(y[i])),tamano=\(sizes[i])\n"
  | i in 1..n
];
