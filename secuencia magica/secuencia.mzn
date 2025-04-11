% ==============================
% MiniZinc - Modelo Secuencia Mágica
% ==============================

% ==============================
% Parámetros
% ==============================

int: n;  % Tamaño del conjunto de variables

% ==============================
% Variables
% ==============================

array[0..n-1] of var 0..n-1: x;  
% x[i] representa cuántas veces aparece el número i en la secuencia.
% Debe estar en el rango [0, n-1].

% ==============================
% Restricciones
% ==============================

% Restricción 1: Cada número i debe aparecer exactamente x[i] veces en la secuencia.
constraint forall(i in 0..n-1)(count(x, i) == x[i]);

% Restricción Redundancia 1: La suma total de las ocurrencias debe ser igual a n.
constraint sum(x) = n;

% Restricción Redundancia 2: Ecuación de balance sobre los valores de x.
constraint sum(i in 1..n)((i-2) * x[i-1]) = 0;

% ==============================
% Resolución 
% ==============================

%solve :: int_search(x, input_order, indomain_split) satisfy;
%solve :: int_search(x, input_order, indomain_random) satisfy;
solve satisfy;


% ==============================
% Salida de resultados
% ==============================

output ["x = [" ++ join(", ", [show(x[i]) | i in 0..n-1]) ++ "]\n"];
% Se imprimen todas las soluciones encontradas, cada una en una línea nueva.
