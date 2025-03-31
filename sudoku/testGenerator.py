import os
import subprocess
import re
import openpyxl
import matplotlib.pyplot as plt
import tempfile

# ======================
# Configuración
# ======================
MINIZINC_PATH = r"C:\Program Files\MiniZinc\minizinc.exe"
MODEL_FILE = "sudoku-test.mzn"
TEST_FOLDER = "tests"

# Estrategias a probar
strategies = [
    ("", ""),  # Satisfacción sin heurísticas
    ("input_order", "indomain_min"),
    ("first_fail", "indomain_min"),
    ("first_fail", "indomain_median"),
    ("first_fail", "indomain_split"),
    ("dom_w_deg", "indomain_min"),
]

# Solvers a usar
solvers = ["Gecode", "Chuffed"]

# ======================
# Extraer estadísticas desde la salida
# ======================
def extraer_estadisticas(salida):
    stats = {}
    patrones = {
        "initTime": r"^%%%mzn-stat: initTime=(.+)",
        "solveTime": r"^%%%mzn-stat: solveTime=(.+)",
        "solutions": r"^%%%mzn-stat: solutions=(\d+)",
        "nSolutions": r"^%%%mzn-stat: nSolutions=(\d+)",
        "nodes": r"^%%%mzn-stat: nodes=(\d+)",
        "failures": r"^%%%mzn-stat: failures=(\d+)",
        "peakDepth": r"^%%%mzn-stat: peakDepth=(\d+)"
    }

    for clave, regex in patrones.items():
        match = re.search(regex, salida, re.MULTILINE)
        stats[clave] = float(match.group(1)) if match else 0.0

    if stats["solutions"] == 0.0 and stats["nSolutions"] > 0.0:
        stats["solutions"] = stats["nSolutions"]

    stats["totalTime"] = stats["initTime"] + stats["solveTime"]
    return stats

# ======================
# Crear archivo Excel
# ======================
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Resultados"
sheet.append([
    "Archivo", "Solver", "Estrategia (var_heur)", "Estrategia (val_heur)",
    "initTime", "solveTime", "totalTime", "solutions", "nodes", "failures", "peakDepth"
])

datos_grafica = []

# ======================
# Ejecutar pruebas
# ======================
for dzn_file in os.listdir(TEST_FOLDER):
    if dzn_file.endswith(".dzn"):
        dzn_path = os.path.join(TEST_FOLDER, dzn_file)

        for solver in solvers:
            for var_heur, val_heur in strategies:
                with open(MODEL_FILE, "r", encoding="utf-8") as f:
                    base_model = f.read()

                # Generar la línea solve según la estrategia
                if not var_heur or not val_heur:
                    solve_line = "\nsolve satisfy;\n"
                else:
                    solve_line = f"""
solve :: int_search(
  [tabla[i, j] | i in 1..9, j in 1..9],
  {var_heur},
  {val_heur},
  complete
) satisfy;
"""

                # Crear archivo temporal con la línea solve
                with tempfile.NamedTemporaryFile(mode="w", suffix=".mzn", delete=False, encoding="utf-8") as tmp_file:
                    tmp_model_path = tmp_file.name
                    tmp_file.write(base_model + "\n" + solve_line)

                # Armar comando
                comando = [
                    MINIZINC_PATH,
                    "--solver", solver,
                    "--statistics",
                    "--all-solutions",
                    tmp_model_path,
                    dzn_path
                ]

                try:
                    print("Comando:", " ".join(comando))
                    resultado = subprocess.run(comando, capture_output=True, text=True, timeout=60)
                    stats = extraer_estadisticas(resultado.stdout + resultado.stderr)

                    # Guardar en Excel
                    sheet.append([
                        dzn_file, solver, var_heur or "satisfy", val_heur or "satisfy",
                        stats["initTime"], stats["solveTime"], stats["totalTime"],
                        int(stats["solutions"]), int(stats["nodes"]),
                        int(stats["failures"]), int(stats["peakDepth"])
                    ])

                    datos_grafica.append((
                        f"{solver}-{var_heur or 'satisfy'}-{val_heur or 'satisfy'}",
                        stats["totalTime"], stats["peakDepth"]
                    ))

                except subprocess.TimeoutExpired:
                    sheet.append([
                        dzn_file, solver, var_heur or "satisfy", val_heur or "satisfy",
                        "Timeout", "-", "-", "-", "-", "-", "-"
                    ])

                finally:
                    os.remove(tmp_model_path)  # Eliminar el archivo temporal

# ======================
# Guardar archivo Excel
# ======================
output_file = "resultados.xlsx"
workbook.save(output_file)
print(f"Resultados guardados en {output_file}")

# ======================
# Generar gráfica
# ======================
etiquetas, total_times, peak_depths = zip(*datos_grafica)

x = range(len(etiquetas))
plt.figure(figsize=(12, 6))

plt.bar(x, total_times, label="Total Time (s)", color="blue", alpha=0.6)
plt.plot(x, peak_depths, label="Peak Depth", color="red", marker="o", linestyle="--")

plt.xticks(x, etiquetas, rotation=45, ha="right")
plt.xlabel("Estrategia")
plt.ylabel("Valores")
plt.title("Tiempos Totales y Profundidad Máxima por Estrategia")
plt.legend()
plt.tight_layout()
plt.savefig("grafica_tiempos_y_profundidad.png")
plt.show()

