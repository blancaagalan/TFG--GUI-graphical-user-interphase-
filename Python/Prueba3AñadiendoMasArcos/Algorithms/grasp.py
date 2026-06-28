import random
import math
from Structure import solution1
from Constructives import cgrasp
from Algorithms import localsearch

def execute(inst, max_iter=100, max_no_improv=5000, alpha=0.3,
            w_cost=0.333, w_eq=0.333, w_gr=0.334):
    """
    Ejecuta el GRASP lexicográfico completo.
    - max_iter: iteraciones de GRASP en cada fase.
    - max_no_improv: límite de iteraciones sin mejora en búsqueda local.
    - alpha: parámetro de la LRC (0.3 = 30% mejores candidatos).
    - w_cost, w_eq, w_gr: pesos para Fase 2 (la cantidad ya está fijada).
    """
    print("=== FASE 1: Maximizar cantidad distribuida ===")
    best_Q_sol = None
    best_Q = 0.0

    # Fase 1: peso total en cantidad -> [1.0, 0, 0, 0]
    for it in range(max_iter):
        # Construcción sin Q_target, se intenta distribuir lo máximo posible
        sol = cgrasp.construct(inst, alpha, Q_target=None, cost_target=None, weights=[1.0,0.0,0.0,0.0])
        Q = sum(env[3] for env in sol['envios'])
        if Q > best_Q:
            best_Q = Q
            best_Q_sol = solution1.copySolution(sol)
            print(f"  Iter {it+1}: nueva mejor cantidad = {best_Q:.1f} t")
    Q_max = best_Q #Q_max es la cantidad máxima alcanzable en la Fase 1, se guarda para usarla como Q_target en la Fase 2
    print(f"Cantidad máxima alcanzable: {Q_max:.1f} t (demanda total: {inst['total_demanda']} t)")

    # --- Calcular meta de coste (cost_min) para la Fase 2 ---
    print("\nCalculando meta de coste (cost_min)...")
    best_cost = float('inf')
    for it in range(max_iter):
        # Construcción con peso total en coste, pero forzando Q_target = Q_max
        sol = cgrasp.construct(inst, alpha, Q_target=Q_max, cost_target=None,
                               weights=[0.0, 1.0, 0.0, 0.0]) # en esta construcción se intenta alcanzar la cantidad máxima pero con el menor coste posible, el peso para coste es 1.0 y para los demás es 0.0, por lo que la función greedy se basará únicamente en el coste aproximado de cada candidato
        Q_sol = sum(env[3] for env in sol['envios'])
        if abs(Q_sol - Q_max) < 0.01:  # debe alcanzar Q_max
            Q_sol, cost_sol, _, _ = solution1.evaluate(sol) # type: ignore # se evalúa la solución para obtener su coste total, aunque también devuelve Q_sol, eq y gr, aquí solo nos interesa el coste para determinar la meta de coste
            if cost_sol < best_cost:
                best_cost = cost_sol
    cost_target = best_cost if best_cost < float('inf') else inst['budget'] / 2 # si no se encontró ninguna solución que alcance Q_max, ponemos un target de coste razonable (la mitad del presupuesto)
    print(f"Meta de coste: {cost_target:.2f} USD")

    # --- Fase 2: Optimizar coste, equidad y fiabilidad ---
    print("\n=== FASE 2: Optimizar coste, equidad y fiabilidad ===")
    weights2 = [0.0, w_cost, w_eq, w_gr]  # Q ya fijado
    best_sol2 = None
    best_obj2 = float('inf')

    for it in range(max_iter):
        sol = cgrasp.construct(inst, alpha, Q_target=Q_max, cost_target=cost_target,
                               weights=weights2)
        Q_sol = sum(env[3] for env in sol['envios'])
        if Q_sol < Q_max * 0.99:   # admite hasta un 1% menos de la cantidad máxima
            continue
        # Búsqueda local
        sol_impr, obj_impr = localsearch.localSearch(sol, Q_max, cost_target, weights2, max_no_improv)
        if obj_impr < best_obj2:
            best_obj2 = obj_impr
            best_sol2 = solution1.copySolution(sol_impr)
            print(f"  Iter {it+1}: mejor obj agregado = {obj_impr:.6f}")

    # --- Resultados finales ---
    print("\n======================================")
    print("        RESULTADOS FINALES")
    print("======================================")
    if best_sol2 is not None:
        # Calcular atributos para mostrar
        Q_final, cost_final, eq_final, gr_final = solution1.evaluate(best_sol2)
        print(f"Cantidad distribuida: {Q_final:.1f} t")
        print(f"Coste total: {cost_final:.2f} USD")
        print(f"Equidad (max déficit): {eq_final:.4f}")
        print(f"Fiabilidad global R: {math.exp(-gr_final):.4f}  (-ln R = {gr_final:.4f})")
        print(f"Objetivo agregado: {best_obj2:.6f}")
        best_sol2['of'] = best_obj2
        solution1.printSolution(best_sol2)
    else:
        print("No se encontró ninguna solución factible en Fase 2.")
    total_veh = {'small': 0, 'medium': 0, 'large': 0}
    if best_sol2 is not None:
        for env in best_sol2['envios']:
            dep, node, vt, tons = env
            n_veh = math.ceil(tons / inst['veh_cap'][vt])
            total_veh[vt] += n_veh
        # --- NUEVO: Desglose de vehículos por nodo ---
    veh_por_nodo = {}
    for node in inst['nodes']:
        veh_por_nodo[node] = {'small': 0, 'medium': 0, 'large': 0}
    if best_sol2 is not None:
        for env in best_sol2['envios']:
            dep, node, vt, tons = env
            n_veh = math.ceil(tons / inst['veh_cap'][vt])
            veh_por_nodo[node][vt] += n_veh

        # 1. El chivato: Esto te dirá el valor exacto y el TIPO de dato
        #print(f"DEBUGGING -> gr_final vale: {gr_final} | Tipo: {type(gr_final)}")

        # 2. El parche de seguridad
        # Si resulta que es None, lo forzamos a 0.0 para que la matemática no explote
        if gr_final is None:
            gr_final = 0.0
            
        # 3. Forzamos a que sea un número decimal (float) por si acaso era texto
        gr_seguro = float(gr_final)

        info = {
            'Q': Q_final,
            'coste': cost_final,
            'eq': eq_final,
            'gr': gr_final,
            'R': math.exp(-gr_seguro),
            'obj': best_obj2,
            'small': total_veh['small'],
            'medium': total_veh['medium'],
            'large': total_veh['large'],
            'veh_por_nodo': veh_por_nodo,   # ← nuevo
            'w_cost': w_cost,
            'w_eq': w_eq,
            'w_gr': w_gr
        }
    else:
        info = None
    return best_sol2, info
   