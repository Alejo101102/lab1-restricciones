% ==============================
% MiniZinc - Modelo Kakuro
% ==============================

% --------------------------------
% Inclusión de librerías
% --------------------------------
include "globals.mzn";

% --------------------------------
% Parámetro: Tamaño del tablero
% --------------------------------
int: N;

% --------------------------------
% Parámetros del tablero
% --------------------------------
% Tipo de celda:
% 0 = negra (obstáculo)
% 1 = jugable (para ingresar valores del 1 al 9)
% 2 = pista (suma horizontal y/o vertical)
array[1..N, 1..N] of int: cell_type;

% Valor de la suma horizontal en cada celda (si es pista)
array[1..N, 1..N] of int: horizontal_sum;

% Valor de la suma vertical en cada celda (si es pista)
array[1..N, 1..N] of int: vertical_sum;

% ==============================
% Variables
% ==============================

% Tablero con valores de 0 a 9 (0 si la celda no es jugable)
array[1..N, 1..N] of var 0..9: grid;

% ==============================
% Restricciones
% ==============================

% -----------------------------
% Valores permitidos en celdas jugables
% -----------------------------
constraint
  forall(i, j in 1..N where cell_type[i,j] = 1) (
    grid[i,j] >= 1 /\ grid[i,j] <= 9
  );

% Las demás celdas deben tener valor 0
constraint
  forall(i, j in 1..N where cell_type[i,j] != 1) (
    grid[i,j] = 0
  );

% -----------------------------
% Funciones auxiliares
% -----------------------------

% Obtener bloque horizontal desde una pista
function array[int] of var 1..9: get_h_block(int: i, int: j) =
  [ grid[i,k] | k in j+1..N where
    cell_type[i,k] = 1 /\ forall(l in j+1..k-1)(cell_type[i,l] = 1)
  ];

% Obtener bloque vertical desde una pista
function array[int] of var 1..9: get_v_block(int: i, int: j) =
  [ grid[k,j] | k in i+1..N where
    cell_type[k,j] = 1 /\ forall(l in i+1..k-1)(cell_type[l,j] = 1)
  ];

% -----------------------------
% Restricciones de pistas (sumas)
% -----------------------------

% Restricciones horizontales
constraint
  forall(i, j in 1..N where horizontal_sum[i,j] > 0) (
    let { array[int] of var 1..9: block = get_h_block(i,j) } in
      sum(block) = horizontal_sum[i,j] /\ alldifferent(block)
  );

% Restricciones verticales
constraint
  forall(i, j in 1..N where vertical_sum[i,j] > 0) (
    let { array[int] of var 1..9: block = get_v_block(i,j) } in
      sum(block) = vertical_sum[i,j] /\ alldifferent(block)
  );

% -----------------------------
% Restricciones adicionales de validación
% -----------------------------
% Comprobar que la suma es posible según la longitud del bloque
constraint
  forall(i, j in 1..N where horizontal_sum[i,j] > 0) (
    let {
      int: n = length(get_h_block(i,j))
    } in
      horizontal_sum[i,j] >= n*(n+1) div 2 /\  % suma mínima
      horizontal_sum[i,j] <= n*(19 - n) div 2  % suma máxima
  );
  
constraint
  forall(i, j in 1..N where vertical_sum[i,j] > 0) (
    let {
      int: n = length(get_v_block(i,j))
    } in
      vertical_sum[i,j] >= n*(n+1) div 2 /\  % suma mínima
      vertical_sum[i,j] <= n*(19 - n) div 2  % suma máxima
  );



% ==============================
% Estrategia de búsqueda
% ==============================
solve satisfy;

% ==============================
% Salida de resultados
% ==============================

% - Muestra:
%   " X " para celdas negras (obstáculo)
%   "/v"  para pistas solo verticales
%   "h\\" para pistas solo horizontales
%   "h/v" para pistas dobles
%   número (1..9) para celdas jugables
output [
  if fix(cell_type[i,j]) = 1 then
    " " ++ show(grid[i,j]) ++ " " ++ (if j = N then "\n" else "" endif)
  elseif fix(cell_type[i,j]) = 2 then
    let {
      string: h = if horizontal_sum[i,j] > 0 then show(horizontal_sum[i,j]) else "" endif,
      string: v = if vertical_sum[i,j] > 0 then show(vertical_sum[i,j]) else "" endif,
      string: pista = if h != "" /\ v != "" then h ++ "/" ++ v
                      else if h != "" then h ++ "\\"  % solo horizontal
                      else if v != "" then "/" ++ v   % solo vertical
                      else " ."
                      endif endif endif
    } in
      pista ++ (if j = N then "\n" else " " endif)
  else
    " X " ++ (if j = N then "\n" else "" endif)
  endif
  | i,j in 1..N
];
