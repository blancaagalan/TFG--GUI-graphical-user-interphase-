import time
import random
import math
import sys
from Structure import instance
from Algorithms import grasp
from Structure import solution1

if __name__ == '__main__':
    random.seed(123)
    inst = instance.createInstance()

    # 1. Redirigir toda la salida de grasp a un archivo de log
    log_file = open("log_grasp.txt", "w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = log_file

    start = time.perf_counter()

    try:
        # 2. Ejecutar GRASP (todos los prints se escriben en log_grasp.txt)
        sol, _ = grasp.execute(inst, max_iter=100, max_no_improv=5000, alpha=0.3,
                               w_cost=0.2, w_eq=0.3, w_gr=0.5)
    except Exception as e:
        # Si ocurre un error, restaurar salida estándar y mostrarlo en consola
        sys.stdout = original_stdout
        print(f"Error durante la ejecución: {e}")
        log_file.close()
        exit(1)
    finally:
        # Restaurar siempre la salida original
        sys.stdout = original_stdout
        log_file.close()

    end = time.perf_counter()

    # 3. Procesar la solución (salida por consola y archivo de resultados)
    if sol is not None:
        Q, cost, eq, gr = solution1.evaluate(sol)
        # Guardar archivo de resumen (como lo tenías)
        with open("resultadoCambioCantidadAyudas.txt", "w") as f:
            f.write(f"Cantidad distribuida: {Q:.1f} t\n")
            f.write(f"Coste total: {cost:.2f} USD\n")
            f.write(f"Equidad (max déficit): {eq:.4f}\n")
            f.write(f"Fiabilidad global R: {math.exp(-gr):.4f}  (-ln R = {gr:.4f})\n")
            f.write("Envíos:\n")
            for env in sol['envios']:
                f.write(f"  D{env[0]} -> N{env[1]} ({env[2]}): {env[3]:.1f} t\n")
        print("Ejecución completada. Resultados guardados en 'log_grasp.txt' y 'resultadoCambioCantidadAyudas.txt'")
    else:
        print("No se encontró solución factible.")

    print(f"Tiempo total de ejecución: {end - start:.2f} segundos")