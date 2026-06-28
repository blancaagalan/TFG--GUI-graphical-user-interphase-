import time
import random
import math
from Structure import instance
from Algorithms import grasp
from Structure import solution1

if __name__ == '__main__':
    random.seed(123)
    inst = instance.createInstance()

    start = time.perf_counter()          # ← inicio del cronómetro
    sol,_ = grasp.execute(inst, max_iter=100, max_no_improv=5000, alpha=0.3,
                    w_cost=0.2, w_eq=0.3, w_gr=0.5)
    if sol is not None:
        Q, cost, eq, gr = solution1.evaluate(sol)
        # Guardar en archivo
        with open("resultadoCambioCantidadAyudas.txt", "w") as f:
            f.write(f"Cantidad distribuida: {Q:.1f} t\n")
            f.write(f"Coste total: {cost:.2f} USD\n")
            f.write(f"Equidad (max déficit): {eq:.4f}\n")
            f.write(f"Fiabilidad global R: {math.exp(-gr):.4f}  (-ln R = {gr:.4f})\n")
            f.write("Envíos:\n")
            for env in sol['envios']:
                f.write(f"  D{env[0]} -> N{env[1]} ({env[2]}): {env[3]:.1f} t\n")
    end = time.perf_counter()            # ← fin del cronómetro

    print(f"\nTiempo total de ejecución: {end - start:.2f} segundos")
    