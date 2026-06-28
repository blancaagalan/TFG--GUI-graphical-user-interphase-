import random
from Structure import instance
from Algorithms import grasp
import math
import json
import time

pesos_modeloA = [
    (0.6, 0.2, 0.2),   # Coste dominante
    (0.2, 0.6, 0.2),   # Equidad dominante
    (0.2, 0.2, 0.6),   # Fiabilidad dominante
    (1/3, 1/3, 1/3)    # Equilibrado
]
inst = instance.createInstance()
start = time.perf_counter()          # ← inicio del cronómetro
resultados = []
for w_cost, w_eq, w_gr in pesos_modeloA:
    random.seed(123)
    sol, info = grasp.execute(inst, max_iter=100, max_no_improv=5000, alpha=0.3,
                              w_cost=w_cost, w_eq=w_eq, w_gr=w_gr)
    if info is not None:
        info['w_cost'] = w_cost
        info['w_eq'] = w_eq
        info['w_gr'] = w_gr
        resultados.append(info)

# Guardar en un archivo por si acaso
with open("resultados_modeloA.json", "w") as f:
    json.dump(resultados, f, indent=2)
print(f"\nTotal de configuraciones evaluadas: {len(resultados)}")
print("Resultados guardados en 'resultados_modeloA.json'")

end = time.perf_counter()            # ← fin del cronómetro
print(f"\nTiempo total de ejecución: {end - start:.2f} segundos")