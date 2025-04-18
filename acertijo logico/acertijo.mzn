% ==============================
% MiniZinc - Acertijo Lógico
% ==============================

% --------------------------------
% Inclusión de librerías
% --------------------------------
include "globals.mzn";  % Para la restricción alldifferent

% ==============================
% Definiciones
% ==============================
enum Nombres = {Juan, Oscar, Dario};
enum Apellidos = {Gonzalez, Garcia, Lopez};
enum Generos = {Clasica, Pop, Jazz};

% ==============================
% Variables
% ==============================
array[Nombres] of var 24..26: Edad;
array[Nombres] of var Apellidos: Apellido;
array[Nombres] of var Generos: Genero;

% ==============================
% Restricciones Generales
% ==============================

% Todas las edades, apellidos y gustos deben ser distintos
constraint alldifferent([Edad[n] | n in Nombres]);
constraint alldifferent([Apellido[n] | n in Nombres]);
constraint alldifferent([Genero[n] | n in Nombres]);

% ==============================
% Pistas del Enunciado
% ==============================

% 1. Juan es más viejo que González, a quien le gusta la música clásica
constraint
  forall(n in Nombres) (
    (Apellido[n] == Gonzalez) -> (Edad[Juan] > Edad[n] /\ Genero[n] == Clasica)
  );

% 2. El fan del pop, que no es García, no tiene 24 años
constraint
  exists(n in Nombres) (
    Genero[n] == Pop /\ Apellido[n] != Garcia /\ Edad[n] != 24
  );

% 3. Oscar, quien no es López, tiene 25
constraint Edad[Oscar] == 25;
constraint Apellido[Oscar] != Lopez;

% 4. La música favorita de Darío no es el jazz
constraint Genero[Dario] != Jazz;

% ==============================
% Estrategia de Búsqueda
% ==============================
solve :: int_search(
  [Edad[n] | n in Nombres],
  dom_w_deg,
  indomain_min
) satisfy;

% ==============================
% Salida de Resultados
% ==============================
output [
  show(n) ++ ": " ++ show(Edad[n]) ++ " años, " ++ show(Apellido[n]) ++
  ", le gusta la música " ++ show(Genero[n]) ++ "\n"
  | n in Nombres
];
