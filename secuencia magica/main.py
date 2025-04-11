import os
import subprocess

# ======================
# Configuración
# ======================
MINIZINC_PATH = "minizinc"
MODEL_FILE = "secuencia.mzn"

def ejecutar_minizinc(n):
    comando = [
        MINIZINC_PATH,
        "--solver", "Gecode",  # Puedes cambiar el solver si deseas
        "--all-solutions",
        MODEL_FILE,
        f"-D n={n}"
    ]
    
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=60)
        soluciones = [line for line in resultado.stdout.strip().split("\n") if line and not line.startswith("-") and not line.startswith("=")]
        num_soluciones = len(soluciones)
        
        print(f"\n--- SOLUCIONES PARA n={n} ---\n")
        for sol in soluciones:
            print(sol)
        print(f"\nNúmero total de soluciones: {num_soluciones}\n")
    except subprocess.TimeoutExpired:
        print("Error: La ejecución excedió el tiempo límite.")
    except FileNotFoundError:
        print("Error: MiniZinc no encontrado en la ruta especificada.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    n = int(input("Ingrese el valor de n: "))
    ejecutar_minizinc(n)
