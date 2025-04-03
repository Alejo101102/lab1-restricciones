import os
import subprocess
import re
import openpyxl

# ======================
# Configuración
# ======================
MINIZINC_PATH = "minizinc"
MODEL_FILE = "secuencia-test-2.mzn"
TEST_FOLDER = "tests2"

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
    "Archivo", "initTime", "solveTime", "totalTime", "solutions", "nodes", "failures", "peakDepth"
])

# ======================
# Ejecutar pruebas
# ======================
for dzn_file in os.listdir(TEST_FOLDER):
    if dzn_file.endswith(".dzn"):
        dzn_path = os.path.join(TEST_FOLDER, dzn_file)

        # Armar comando
        comando = [
            MINIZINC_PATH,
            "--solver", "Gecode",
            "--statistics",
            "--all-solutions",
            MODEL_FILE,
            dzn_path
        ]

        try:
            print("Comando:", " ".join(comando))
            resultado = subprocess.run(comando, capture_output=True, text=True, timeout=60)
            stats = extraer_estadisticas(resultado.stdout + resultado.stderr)

            # Guardar en Excel
            sheet.append([
                dzn_file, stats["initTime"], stats["solveTime"], stats["totalTime"],
                int(stats["solutions"]), int(stats["nodes"]), int(stats["failures"]), int(stats["peakDepth"])
            ])

        except subprocess.TimeoutExpired:
            sheet.append([dzn_file, "Timeout", "-", "-", "-", "-", "-", "-"])

# ======================
# Guardar archivo Excel
# ======================
output_file = "resultados-2.xlsx"
workbook.save(output_file)
print(f"Resultados guardados en {output_file}")
