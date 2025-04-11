include "lex_lesseq.mzn";


int: W;  % Ancho
int: H;  % Alto
int: n;  % Número de cuadrados
array[1..n] of int: sizes;  % Lados de cada cuadrado

% Variables: coordenadas (x, y) de la esquina inferior izquierda de cada cuadrado
array[1..n] of var 0..W-1: x;
array[1..n] of var 0..H-1: y;

% Restricción: cada cuadrado debe estar completamente dentro del rectángulo W*H
constraint forall(i in 1..n)(
    x[i] + sizes[i] <= W /\
    y[i] + sizes[i] <= H
);

% Restricción: ningún par de cuadrados se debe solapar 
constraint forall(i, j in 1..n where i < j)(
    x[i] + sizes[i] <= x[j] \/
    x[j] + sizes[j] <= x[i] \/
    y[i] + sizes[i] <= y[j] \/
    y[j] + sizes[j] <= y[i]
);

constraint W * H = sum(i in 1..n)(sizes[i] * sizes[i]);



%Restriccion para rompimiento de simetrias


constraint forall(i, j in 1..n where i < j /\ sizes[i] = sizes[j]) (
  lex_lesseq([x[i], y[i]], [x[j], y[j]])
);


% Estrategia de búsqueda
solve satisfy;


% Salida
output [
  "Coordenadas de los cuadrados:\n"
] ++
[
  "Cuadrado\(i):(x=\(x[i]),y=\(y[i])),tamano=\(sizes[i])\n"
  | i in 1..n
];
