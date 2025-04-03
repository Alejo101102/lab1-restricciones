% ==============================
% Parámetros
% ==============================

int: n;  % Tamaño del conjunto de variables
bool: use_restriccion_1;  % Activar/Desactivar Restricción 1
bool: use_redundancia_1;  % Activar/Desactivar Restricción Redundante 1
bool: use_redundancia_2;  % Activar/Desactivar Restricción Redundante 2

% ==============================
% Variables
% ==============================

array[0..n-1] of var 0..n-1: x;  

% ==============================
% Restricciones
% ==============================

% Restricción 1: Cada número i debe aparecer exactamente x[i] veces en la secuencia.
constraint use_restriccion_1 -> forall(i in 0..n-1)(count(x, i) == x[i]);

% Restricción Redundancia 1: La suma total de las ocurrencias debe ser igual a n.
constraint use_redundancia_1 -> (sum(x) = n);

% Restricción Redundancia 2: Ecuación de balance sobre los valores de x.
constraint use_redundancia_2 -> (sum(i in 1..n)((i-2) * x[i-1]) = 0);

% ==============================
% Resolución 
% ==============================

%solve satisfy;

% ==============================
% Salida de resultados
% ==============================

output ["x = [" ++ join(", ", [show(x[i]) | i in 0..n-1]) ++ "]\n"];
