import os
import re
import glob
import random
import tempfile
from pathlib import Path
from subprocess import run, PIPE
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import openpyxl

# =====================
# Configuración
# =====================
MODEL_FILE = "rectangulo.mzn"
TEST_FOLDER = "tests"
RESULT_FOLDER = "resultados"
MINIZINC_PATH = "minizinc"  # Asume que está en el PATH

# Estrategias a probar
strategies = [
    ("", ""),  # Satisfacción sin heurísticas
    ("input_order", "indomain_min"),
    ("first_fail", "indomain_min"),
    ("first_fail", "indomain_median"),
    ("first_fail", "indomain_split"),
    ("dom_w_deg", "indomain_min"),
]

solvers = ["Gecode", "Chuffed"]

# =====================
# Funciones auxiliares
# =====================

def extraer_estadisticas(salida):
    print("Salida del solver:\n", salida)
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

def draw_solution(filename: str, H: int, W: int, sizes: list[int], solution_text: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    solution_text = solution_text.split("----------")[0]

    squares = []
    pattern = r"Cuadrado(\d+):\(x=(\d+),y=(\d+)\),tamano=(\d+)"
    matches = list(re.finditer(pattern, solution_text))

    if not matches:
        print(" No se detectaron coincidencias en la salida.")
        return

    for match in matches:
        i, x, y, size = map(int, match.groups())
        squares.append({"id": i, "x": x, "y": y, "size": size})

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect('equal')
    ax.set_xticks(range(W + 1))
    ax.set_yticks(range(H + 1))
    ax.grid(True)

    random.seed(42)
    colors = [plt.cm.tab20(i % 20) for i in range(len(squares))]

    for i, sq in enumerate(squares):
        rect = patches.Rectangle((sq["x"], sq["y"]), sq["size"], sq["size"],
                                 linewidth=1, edgecolor='black', facecolor=colors[i])
        ax.add_patch(rect)
        ax.text(sq["x"] + sq["size"]/2, sq["y"] + sq["size"]/2, f'{sq["id"]}',
                ha='center', va='center', fontsize=10, color='black', weight='bold')

    example_name = Path(filename).stem
    plt.suptitle(f"Ejemplo: {example_name}", fontsize=14, y=0.95)
    text_info = f"H = {H}   W = {W}   sizes = {sizes}"
    plt.title(text_info, fontsize=10)

    output_path = os.path.join(output_dir, f"{example_name}.png")
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return output_path

# =====================
# Excel y gráficos
# =====================
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Resultados"
sheet.append([
    "Archivo", "Solver", "VarHeur", "ValHeur",
    "initTime", "solveTime", "totalTime",
    "solutions", "nodes", "failures", "peakDepth"
])

datos_grafica = []

# =====================
# Bucle principal
# =====================
os.makedirs(RESULT_FOLDER, exist_ok=True)

for dzn_file in glob.glob(os.path.join(TEST_FOLDER, "*.dzn")):
    nombre_archivo = Path(dzn_file).stem

    with open(dzn_file, "r") as f:
        dzn_text = f.read()
        H = int(re.search(r"H\s*=\s*(\d+);", dzn_text).group(1))
        W = int(re.search(r"W\s*=\s*(\d+);", dzn_text).group(1))
        sizes = list(map(int, re.search(r"sizes\s*=\s*\[([0-9,\s]+)\];", dzn_text).group(1).split(',')))

    for solver in solvers:
        for var_heur, val_heur in strategies:
            with open(MODEL_FILE, "r", encoding="utf-8") as f:
                base_model = f.read()

            solve_line = "\nsolve satisfy;\n" if not var_heur else f"""
solve :: int_search(x ++ y, {var_heur}, {val_heur}, complete) satisfy;
"""

            with tempfile.NamedTemporaryFile(mode="w", suffix=".mzn", delete=False, encoding="utf-8") as tmp_file:
                tmp_model_path = tmp_file.name
                tmp_file.write(base_model + "\n" + solve_line)

            comando = [
                MINIZINC_PATH,
                "--solver", solver,
                "--statistics",
                "--all-solutions",
                tmp_model_path,
                dzn_file
            ]
            print(f"Ejecutando: {' '.join(comando)}")
            try:
                resultado = run(comando, capture_output=True, text=True, timeout=60)
                stats = extraer_estadisticas(resultado.stdout + resultado.stderr)

                sheet.append([
                    nombre_archivo, solver, var_heur or "satisfy", val_heur or "satisfy",
                    stats["initTime"], stats["solveTime"], stats["totalTime"],
                    int(stats["solutions"]), int(stats["nodes"]),
                    int(stats["failures"]), int(stats["peakDepth"])
                ])

                datos_grafica.append((
                    f"{solver}-{var_heur or 'satisfy'}-{val_heur or 'satisfy'}",
                    stats["totalTime"], stats["peakDepth"]
                ))

                if "Cuadrado" in resultado.stdout:
                    draw_solution(dzn_file, H, W, sizes, resultado.stdout, RESULT_FOLDER)

            except Exception as e:
                sheet.append([
                    nombre_archivo, solver, var_heur or "satisfy", val_heur or "satisfy",
                    "Error", "-", "-", "-", "-", "-", "-"
                ])
                print(f"❌ Error en {nombre_archivo} con {var_heur}/{val_heur}: {e}")

            finally:
                os.remove(tmp_model_path)

# Guardar Excel
excel_path = os.path.join(RESULT_FOLDER, "resultados.xlsx")
workbook.save(excel_path)
print(f"✅ Resultados guardados en {excel_path}")

# Gráfico
labels, total_times, peak_depths = zip(*datos_grafica)
x = range(len(labels))

plt.figure(figsize=(14, 6))
plt.bar(x, total_times, label="Total Time (s)", color="blue", alpha=0.6)
plt.plot(x, peak_depths, label="Peak Depth", color="red", marker="o", linestyle="--")
plt.xticks(x, labels, rotation=45, ha="right")
plt.xlabel("Estrategia")
plt.ylabel("Valores")
plt.title("Tiempos Totales y Profundidad Máxima por Estrategia")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULT_FOLDER, "grafica_comparativa.png"))
plt.show()
