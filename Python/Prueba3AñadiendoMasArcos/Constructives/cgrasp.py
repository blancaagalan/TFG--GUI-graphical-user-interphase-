import math
import random
from Structure import solution1

def construct(inst, alpha, Q_target=None, cost_target=None, weights=None): #si Q_target es None, se maximiza cantidad sin límite superior y weights se ignora (fase 1), si se especifica Q_target, se intenta alcanzar esa cantidad y weights se usa para evaluar candidatos (fase 2)
    """
    Fase constructiva GRASP.
    Construye una solución añadiendo envíos de forma voraz aleatorizada.
    Si Q_target es None, maximiza la cantidad distribuida sin límite superior
    (más allá de demandas y ofertas). Si se especifica, intenta alcanzar esa cantidad.
    weights: lista [w_Q, w_cost, w_eq, w_gr] para evaluar candidatos.
    """
    sol = solution1.createEmptySolution(inst) 
    rem_ofertas = inst['supply'].copy() # Estado de recursos (copias para ir actualizando)
    rem_demand = inst['demand'].copy()
    rem_veh = {d: inst['veh_avail'][d].copy() for d in inst['depositos']} # copia profunda de la disponibilidad de vehículos
    rem_presupuesto = inst['budget']
    total_sent = 0.0 # cantidad total enviada hasta ahora
    target = Q_target if Q_target is not None else sum(inst['demand'].values()) # si no hay target, el objetivo es enviar todo lo posible (hasta la suma de demandas)
    alpha = alpha if alpha >= 0 else random.random() # random.random() devuelve un float entre 0.0 y 1.0

    while True:
        # Construir lista de candidatos factibles en este paso, con su valor greedy
        candidates = createCandidateList(sol, rem_ofertas, rem_demand, rem_veh, rem_presupuesto, target - total_sent)
        if not candidates: # si no hay candidatos factibles, terminamos
            break  # no hay más envíos posibles
        # --- Evaluación de candidatos con normalización min‑max ---
        if weights is not None and weights[0] <= 0.99:   # Fase 2
            costs = [c['approx_cost'] for c in candidates]
            rels = [c['rel'] for c in candidates]
            c_min, c_max = min(costs), max(costs)
            r_min, r_max = min(rels), max(rels)

            for cand in candidates:
                if c_max > c_min:
                    cost_score = 1.0 - (cand['approx_cost'] - c_min) / (c_max - c_min)
                else:
                    cost_score = 1.0
                if r_max > r_min:
                    rel_score = (cand['rel'] - r_min) / (r_max - r_min)
                else:
                    rel_score = 1.0
                cand['greedy'] = weights[1] * cost_score + weights[3] * rel_score

        else:   # Fase 1
            for cand in candidates:
                cand['greedy'] = cand['tons']

        gmin = min(c['greedy'] for c in candidates)
        gmax = max(c['greedy'] for c in candidates)
        
        # Construir RCL
        threshold = gmax - alpha * (gmax - gmin) # si alpha=0, threshold=gmax (solo el mejor); si alpha=1, threshold=gmin (todos los factibles)
        rcl = [c for c in candidates if c['greedy'] >= threshold]  # candidatos con valor greedy suficientemente bueno

        # Selección aleatoria de la RCL
        chosen = random.choice(rcl)

        # Realizar el envío
        dep, node, vtipo, tons = chosen['dep'], chosen['node'], chosen['vtipo'], chosen['tons']
        solution1.addToSolution(sol, dep, node, vtipo, tons)
        # Actualizar recursos
        rem_ofertas[dep] -= tons # reducir la oferta restante en el depósito de origen
        rem_demand[node] -= tons #-= significa restar la cantidad enviada a la demanda restante del nodo de destino
        n_veh = math.ceil(tons / inst['veh_cap'][vtipo]) # calcular el número de vehículos necesarios para enviar esa cantidad con ese tipo de vehículo
        rem_veh[dep][vtipo] -= n_veh # reducir la cantidad de vehículos disponibles de ese tipo en el depósito de origen,teniendo el tipo de vehículo y el depósito, se accede a la cantidad de vehículos disponibles y se resta el número de vehículos necesarios para el envío
        arco = (dep, node)
        dist, _, _ = inst['arcs'][arco]
        ship_cost = n_veh * inst['veh_cf'][vtipo] * dist + tons * inst['veh_cv'][vtipo] * dist
        rem_presupuesto -= ship_cost
        total_sent += tons

        # Si alcanzamos el target, paramos (solo si Q_target fue especificado)
        if Q_target is not None and total_sent >= target - 1e-6: # si la cantidad enviada alcanza o supera el target (con un pequeño margen para evitar problemas de precisión), terminamosS
            break

    # La solución puede no ser factible según isFeasible (por ejemplo, si no se alcanzó Q_target
    # pero eso se gestionará en grasp). Aquí simplemente devolvemos la construcción.
    return sol


def createCandidateList(sol, rem_supply, rem_demand, rem_veh, rem_budget, remaining_q):
    """
    Genera todos los envíos factibles dados los recursos remanentes.
    Cada candidato es un diccionario con: dep, node, vtype, tons (máximo factible).
    """
    inst = sol['instance']
    candidates = []
    for (dep, node), (dist, vel, rel) in inst['arcs'].items():
        # Verificar recursos
        if rem_supply.get(dep, 0) <= 0: # si el depósito no tiene oferta restante, no es candidato
            continue
        if rem_demand.get(node, 0) <= 0:    # si el nodo de demanda no tiene demanda restante, no es candidato
            continue
        # Para cada tipo de vehículo disponible en este depósito y arco, calcular la cantidad máxima factible que se podría enviar, considerando oferta, demanda, capacidad de vehículos y presupuesto restante 
        for vtipo in ['small', 'medium', 'large']:
            if rem_veh[dep][vtipo] <= 0: # si no hay vehículos de este tipo disponibles en el depósito, no es candidato
                continue # continua con el siguiente tipo de vehículo, si no hay vehículos de este tipo disponibles, no se puede enviar con ese tipo, pero puede haber otros tipos disponibles
            cap = inst['veh_cap'][vtipo]
            max_tons_veh = cap * rem_veh[dep][vtipo]
            max_tons = min(rem_supply[dep], rem_demand[node], max_tons_veh)
            # Ajustar por remaining_q (si estamos en fase 2 y queremos control exacto)
            if remaining_q is not None and remaining_q < max_tons:
                max_tons = remaining_q
            # Comprobar primero si la cantidad máxima cabe en el presupuesto sin buscar binariamente
            n_max = math.ceil(max_tons / cap)
            cost_max = n_max * inst['veh_cf'][vtipo] * dist + max_tons * inst['veh_cv'][vtipo] * dist
            if cost_max <= rem_budget:
                feasible_tons = max_tons
            else:
                # Ajustar por presupuesto: búsqueda binaria para máxima cantidad factible
                lo, hi = 0.0, max_tons
                while hi - lo > 0.01:
                    mid = (lo + hi) / 2
                    n = math.ceil(mid / cap)
                    cost_mid = n * inst['veh_cf'][vtipo] * dist + mid * inst['veh_cv'][vtipo] * dist
                    if cost_mid <= rem_budget:
                        lo = mid
                    else:
                        hi = mid
                feasible_tons = lo
            if feasible_tons < 0.01: # si la cantidad factible es muy pequeña, no lo consideramos candidato
                continue
            # Si la cantidad restante a enviar es muy pequeña, enviar exactamente eso
            if remaining_q is not None and feasible_tons > remaining_q:
                feasible_tons = remaining_q
            if feasible_tons < 0.01:
                continue
            n = math.ceil(feasible_tons / cap) # número de vehículos necesarios para enviar la cantidad factible, se calcula dividiendo la cantidad factible entre la capacidad del vehículo y redondeando hacia arriba
            approx_cost = n * inst['veh_cf'][vtipo] * dist + feasible_tons * inst['veh_cv'][vtipo] * dist
            candidates.append({ # cada candidato es un diccionario con la información del envío factible
                'dep': dep,
                'node': node,
                'vtipo': vtipo,
                'tons': feasible_tons,
                'approx_cost': approx_cost,   # ← nuevo campo
                'rel': rel,                  # ← nuevo campo (la fiabilidad del arco)
                'greedy': 0.0  # se calculará después
            })
    return candidates


def greedyValue(candidate, inst, weights, cost_target):
    """
    Calcula el valor greedy de un candidato.
    Si weights[0] > 0.99 (fase 1, maximizar cantidad), devuelve las toneladas.
    En otro caso, combina coste (minimizar) y fiabilidad (maximizar).
    """
    dep, node, vtipo, tons = candidate['dep'], candidate['node'], candidate['vtipo'], candidate['tons']
    if weights is None or weights[0] > 0.99:
        # Fase 1: lo único que importa es cuánto puedo enviar
        return tons
    else:
        # Fase 2: combinamos coste y fiabilidad
        key = (dep, node)
        dist, _, rel = inst['arcs'][key]
        n_veh = math.ceil(tons / inst['veh_cap'][vtipo])
        approx_cost = n_veh * inst['veh_cf'][vtipo] * dist + tons * inst['veh_cv'][vtipo] * dist
        # Normalizar coste con el cost_target
        if cost_target and cost_target > 0:
            cost_norm = approx_cost / cost_target #target es el coste que queremos alcanzar, si el coste aproximado del candidato es igual al target, cost_norm=1; si es menor, cost_norm<1; si es mayor, cost_norm>1
        else:
            cost_norm = approx_cost / inst['budget']  # fallback
        # Cuanto menor coste, mejor; cuanto mayor fiabilidad, mejor
        # weights[1] = peso del coste, weights[3] = peso de la fiabilidad
        return weights[1] * (1 - cost_norm) + weights[3] * rel