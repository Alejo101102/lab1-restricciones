El proyecto está organizado en carpetas, cada una correspondiente a un punto del taller. Dentro de cada carpeta se incluye: 

- Un modelo (.mzn) 

- Una subcarpeta llamada test las cuales tienen todas las pruebas (.dzn) a ejecutar. 

También hay un script de Python en el cual ayuda a tomar métricas como tiempo de inicio, finalizar, nodos, fallos y demás, además de exportar un Excel con las métricas y una imagen que las representa. 

Para ejecutar el script se debe tener en cuenta de que debemos estar dentro de la carpeta correspondiente. Por ejemplo, si estamos trabajando Visual Studio Code en la terminal se debe ver algo en la consola como:

taller1>reunión

Si no estás dentro de la carpeta correcta, el script no funcionará o generará errores.

La estructura del proyecto está conformado de la siguiente manera:

Taller1/
│
├── acertijo magico/
│
│   ├── tests/
│   │
│   ├── acertijo.mzn
│
├── kakuro/
│
│   ├── tests/
│   │
│   ├── kakuro.mzn
│
├── rectangulo
│
│   ├── tests/
│   │
│   ├── rectangulo.mzn
│
├── reunion/
│
│   ├── tests/
│   │
│   ├── reunion.mzn
│
├── secuencia magica/
│
│   ├── tests/
│   │
│   ├── secuencia.mzn
│
├── sudoku/
│
│   ├── tests/
│   │
│   ├── sudoku.mzn
│
├── InformeTaller1.pdf
│
└── README.txt
