import os
import subprocess
import re

# ======================
# Configuración
# ======================
MINIZINC_PATH = r"C:\Program Files\MiniZinc\minizinc.exe"  # <-- ajusta si es necesario
MODEL_FILE = "sudoku.mzn"
TEST_FOLDER = "tests"

# Estrategias a probar
strategies = [
    ("input_order", "indomain_min"),
    ("first_fail", "indomain_min"),
    ("first_fail", "indomain_median"),
    ("dom_w_deg", "indomain_min"),
]

# ======================
# Función para crear modelo temporal con estrategia inyectada
# ======================
def generar_modelo_temporal(base_path, var_heur, val_heur):
    with open(base_path, "r", encoding="utf-8") as f:
        texto = f.read()

    # Eliminar solve_annotation si está presente
    texto = "\n".join([line for line in texto.splitlines() if "solve_annotation" not in line])

    estrategia = f"solve :: int_search([tabla[i, j] | i in 1..9, j in 1..9], {var_heur}, {val_heur}, complete) satisfy;"
    texto_modificado = texto + "\n\n" + estrategia

    archivo_temp = f"temp_{var_heur}_{val_heur}.mzn"
    with open(archivo_temp, "w", encoding="utf-8") as f:
        f.write(texto_modificado)

    return archivo_temp

# ======================
# Extraer estadísticas desde la salida
# ======================
def extraer_estadisticas(salida):
    stats = {
        "time": "-",
        "nodes": "-",
        "failures": "-",
        "maxDepth": "-",
        "solved": "No"
    }

    if "===========" in salida:
        stats["solved"] = "Sí"

    patrones = {
        "time": r"^%%%mzn-stat: time=(.+)",
        "nodes": r"^%%%mzn-stat: nodes=(\d+)",
        "failures": r"^%%%mzn-stat: failures=(\d+)",
        "maxDepth": r"^%%%mzn-stat: maxDepth=(\d+)"
    }

    for clave, regex in patrones.items():
        match = re.search(regex, salida, re.MULTILINE)
        if match:
            stats[clave] = match.group(1)

    return stats

# ======================
# Ejecutar pruebas
# ======================
for dzn_file in os.listdir(TEST_FOLDER):
    if dzn_file.endswith(".dzn"):
        dzn_path = os.path.join(TEST_FOLDER, dzn_file)

        print(f"\n=== Archivo: {dzn_file} ===")

        for var_heur, val_heur in strategies:
            temp_model = generar_modelo_temporal(MODEL_FILE, var_heur, val_heur)

            comando = [
                MINIZINC_PATH,
                "--solver", "Gecode",
                "--statistics",
                temp_model,
                dzn_path
            ]

            try:
                resultado = subprocess.run(comando, capture_output=True, text=True, timeout=60)
                salida = resultado.stdout + resultado.stderr
                stats = extraer_estadisticas(salida)
                print(f"\n[ Estrategia: {var_heur}, {val_heur} ]")
                print(salida)
                # print(f"\n[ Estrategia: {var_heur}, {val_heur} ]")
                # print(f"  Solución encontrada: {stats['solved']}")
                # print(f"  Tiempo (s): {stats['time']}")
                # print(f"  Nodos explorados: {stats['nodes']}")
                # print(f"  Nodos fallidos: {stats['failures']}")
                # print(f"  Profundidad máxima: {stats['maxDepth']}")

            except subprocess.TimeoutExpired:
                print(f"\n[ Estrategia: {var_heur}, {val_heur} ]")
                print("  Error: tiempo límite excedido (timeout)")

            finally:
                os.remove(temp_model)
