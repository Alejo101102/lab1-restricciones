include "globals.mzn";  % Importa alldifferent

enum Nombres = {Juan, Oscar, Dario};
enum Apellidos = {Gonzalez, Garcia, Lopez};
enum Musicas = {Clasica, Pop, Jazz};

array[Nombres] of var 24..26: Edad;
array[Nombres] of var Apellidos: Apellido;
array[Nombres] of var Musicas: Musica;

% Todas las edades, apellidos y gustos deben ser distintos
constraint alldifferent([Edad[n] | n in Nombres]);
constraint alldifferent([Apellido[n] | n in Nombres]);
constraint alldifferent([Musica[n] | n in Nombres]);

% 1. Juan es más viejo que González, a quien le gusta la música clásica
constraint
  forall(n in Nombres) (
    (Apellido[n] == Gonzalez) -> (Edad[Juan] > Edad[n] /\ Musica[n] == Clasica)
  );

% 2. El fan del pop, que no es García, no tiene 24 años
constraint
  exists(n in Nombres) (
    Musica[n] == Pop /\ Apellido[n] != Garcia /\ Edad[n] != 24
  );

% 3. Oscar, quien no es López, tiene 25
constraint Edad[Oscar] == 25;
constraint Apellido[Oscar] != Lopez;

% 4. La música favorita de Darío no es el jazz
constraint Musica[Dario] != Jazz;

solve satisfy;

output [
  show(n) ++ ": " ++ show(Edad[n]) ++ " años, " ++ show(Apellido[n]) ++
  ", le gusta la música " ++ show(Musica[n]) ++ "\n"
  | n in Nombres
];