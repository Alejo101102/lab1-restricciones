import subprocess
import re
import openpyxl
import matplotlib.pyplot as plt

# ======================
# Configuración
# ======================
MINIZINC_PATH = r"C:\Program Files\MiniZinc\minizinc.exe"
MODEL_FILE = r".\acertijo.mzn"

strategies = [
    ("", ""),  # Satisfacción sin heurísticas
    ("input_order", "indomain_min"),
    ("first_fail", "indomain_min"),
    ("first_fail", "indomain_median"),
    ("first_fail", "indomain_split"),
    ("dom_w_deg", "indomain_min"),
]

solvers = ["Gecode", "Chuffed"]

# ======================
# Extraer estadísticas
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
# Crear Excel
# ======================
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Resultados"
sheet.append([
    "Modelo", "Solver", "Estrategia (var_heur)", "Estrategia (val_heur)",
    "initTime", "solveTime", "totalTime", "solutions", "nodes", "failures", "peakDepth"
])

datos_grafica = []

# ======================
# Ejecutar combinaciones
# ======================
for solver in solvers:
    for var_heur, val_heur in strategies:
        # Asegúrate que el archivo acertijo.mzn tenga un bloque solve adecuado para cada combinación

        comando = [
            MINIZINC_PATH,
            "--solver", solver,
            "--statistics",
            "--all-solutions",
            MODEL_FILE
        ]

        print(f"Ejecutando: {solver} - {var_heur or 'satisfy'} / {val_heur or 'satisfy'}")
        try:
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Mostrar salida para depuración
            print(resultado.stdout)
            print(resultado.stderr)

            stats = extraer_estadisticas(resultado.stdout + resultado.stderr)

            sheet.append([
                "acertijo.mzn", solver, var_heur or "satisfy", val_heur or "satisfy",
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
                "acertijo.mzn", solver, var_heur or "satisfy", val_heur or "satisfy",
                "Timeout", "-", "-", "-", "-", "-", "-"
            ])

# ======================
# Guardar resultados
# ======================
output_file = "resultados_acertijo.xlsx"
workbook.save(output_file)
print(f"Resultados guardados en {output_file}")

# ======================
# Gráfica
# ======================
if datos_grafica:
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
    plt.savefig("grafica_acertijo.png")
    plt.show()
