import os
import subprocess
import re
import openpyxl
import matplotlib.pyplot as plt

# ======================
# Configuración
# ======================
MINIZINC_PATH = r"C:\Program Files\MiniZinc\minizinc.exe"
MODEL_FILE = "sudoku-test.mzn"
TEST_FOLDER = "tests"

# Estrategias a probar
strategies = [
    ("input_order", "indomain_min"),
    ("first_fail", "indomain_min"),
    ("first_fail", "indomain_median"),
    ("dom_w_deg", "indomain_min"),
]

# Lista de solvers a probar
solvers = ["Gecode", "Chuffed", "CBC"]

# ======================
# Extraer estadísticas desde la salida
# ======================
def extraer_estadisticas(salida):
    stats = {}
    
    patrones = {
        "initTime": r"^%%%mzn-stat: initTime=(.+)",
        "solveTime": r"^%%%mzn-stat: solveTime=(.+)",
        "solutions": r"^%%%mzn-stat: solutions=(\d+)",
        "nodes": r"^%%%mzn-stat: nodes=(\d+)",
        "failures": r"^%%%mzn-stat: failures=(\d+)",
        "peakDepth": r"^%%%mzn-stat: peakDepth=(\d+)"
    }

    for clave, regex in patrones.items():
        match = re.search(regex, salida, re.MULTILINE)
        stats[clave] = float(match.group(1)) if match else 0.0
    
    stats["totalTime"] = stats["initTime"] + stats["solveTime"]
    return stats

# ======================
# Crear archivo Excel
# ======================
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Resultados"
sheet.append(["Archivo", "Solver", "Estrategia (var_heur)", "Estrategia (val_heur)", 
              "initTime", "solveTime", "totalTime", "solutions", "nodes", "failures", "peakDepth",])

datos_grafica = []  # Para almacenar datos de la gráfica

# ======================
# Ejecutar pruebas
# ======================
for dzn_file in os.listdir(TEST_FOLDER):
    if dzn_file.endswith(".dzn"):
        dzn_path = os.path.join(TEST_FOLDER, dzn_file)

        for solver in solvers:
            for var_heur, val_heur in strategies:
                comando = [
                    MINIZINC_PATH,
                    "--solver", solver,
                    "--statistics",
                    "--all-solutions",
                    MODEL_FILE,
                    dzn_path
                ]

                try:
                    resultado = subprocess.run(comando, capture_output=True, text=True, timeout=60)
                    stats = extraer_estadisticas(resultado.stdout + resultado.stderr)
                    
                    # Agregar datos al archivo Excel
                    sheet.append([
                        dzn_file, solver, var_heur, val_heur,
                        stats["initTime"], stats["solveTime"], stats["totalTime"],
                        int(stats["solutions"]), int(stats["nodes"]), int(stats["failures"]), int(stats["peakDepth"])
                    ])

                    # Guardar datos para la gráfica
                    datos_grafica.append((f"{solver}-{var_heur}-{val_heur}", stats["totalTime"], stats["peakDepth"]))

                except subprocess.TimeoutExpired:
                    sheet.append([dzn_file, solver, var_heur, val_heur, "Timeout", "-", "-", "-", "-", "-", "-"])

# Guardar el archivo Excel
output_file = "resultados.xlsx"
workbook.save(output_file)
print(f"Resultados guardados en {output_file}")

# ======================
# Generar gráfica
# ======================
etiquetas, total_times, peak_depths = zip(*datos_grafica)

x = range(len(etiquetas))
plt.figure(figsize=(12, 6))

# Gráfica de tiempos totales
plt.bar(x, total_times, label="Total Time (s)", color="blue", alpha=0.6)

# Gráfica de profundidad máxima
plt.plot(x, peak_depths, label="Peak Depth", color="red", marker="o", linestyle="--")

plt.xticks(x, etiquetas, rotation=45)
plt.xlabel("Estrategia")
plt.ylabel("Valores")
plt.title("Tiempos Totales y Profundidad Máxima por Estrategia")
plt.legend()
plt.tight_layout()
plt.savefig("grafica_tiempos_y_profundidad.png")
plt.show()
