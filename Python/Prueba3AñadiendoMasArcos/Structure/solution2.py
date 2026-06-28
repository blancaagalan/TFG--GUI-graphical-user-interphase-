import math

def createEmptySolution(instance):
    sol = {} # nueva solución vacía
    sol['instance'] = instance # referencia a la instancia (no se copia, es inmutable)
    sol['envios'] = []      # lista de envíos (dep, node, vtipo, ton)
    sol['of'] = 0.0            # valor de la función objetivo agregada
    return sol

def addToSolution(sol, dep, node, vtipo, ton):
    sol['envios'].append((dep, node, vtipo, ton)) # añadir un nuevo envío a la solución

def removeFromSolution(sol, idx):
    del sol['envios'][idx] # eliminar el envío en la posición idx

def evaluate(sol, Q_target, cost_target, pesos):
    """
    Evalúa la solución completa: calcula cantidad, coste, equidad, fiabilidad
    y la función objetivo agregada (suma ponderada de desviaciones normalizadas).
    El resultado se almacena en sol['of'] y también se devuelve.
    """
    inst = sol['instance']
    Q = 0.0 # cantidad total enviada
    coste = 0.0 # coste total de los envíos
    recibido = {j: 0.0 for j in inst['nodes']}
    used_arcs = set() # para calcular fiabilidad global

    for (dep, node, vtipo, ton) in sol['envios']:
        Q += ton
        recibido[node] += ton
        arco = (dep, node)
        if arco in inst['arcs']:
            dist, _, rel = inst['arcs'][arco]
            n_veh = math.ceil(ton / inst['veh_cap'][vtipo])
            coste += n_veh * inst['veh_cf'][vtipo] * dist + ton * inst['veh_cv'][vtipo] * dist
            used_arcs.add(arco) # registrar arco usado para fiabilidad

    # Equidad: máximo déficit proporcional (1 - y_j/d_j)
    eq = 0.0
    for j, d in inst['demand'].items(): #j es el nodo de demanda, d es su demanda
        if d > 0:
            eq = max(eq, 1.0 - recibido[j] / d)

    # Fiabilidad global: -ln(R)
    if len(used_arcs) == 0: # si no se usó ningún arco, consideramos fiabilidad perfecta (R=1) para evitar -inf
        gr = 0.0
    else:
        log_product = 0.0
        for arco in used_arcs:
            rel = inst['arcs'][arco][2] # fiabilidad del arco y el valor 2 es la posición de la tupla (dist, vel, rel)
            log_product += math.log(rel)
        gr = -log_product

    # Desviaciones respecto a las metas
    dv1 = max(0.0, Q_target - Q) if Q_target > 0 else 0.0 # cantidad es mejor cuanto mayor, así que la desviación es meta - cantidad, ademas esta fijada por total_demanda
    dv2 = max(0.0, coste - cost_target) if (cost_target is not None and cost_target > 0) else 0.0# coste es mejor cuanto menor, así que la desviación es coste - meta, ademas esta fijada por 1_000_000
    dv3 = max(0.0, eq - inst['t_Eq']) # equidad es mejor cuanto menor, así que la desviación es eq - meta, ademas esta fijada por 1e-4
    dv4 = max(0.0, inst['t_GR'] - gr) # fiabilidad es mejor cuanto mayor, así que la desviación es meta - gr, ademas esta fijada por 1.2

    # Función objetivo agregada normalizada
    obj = 0.0
    if Q_target > 0: 
        obj += pesos[0] * dv1 / Q_target
                                                        #if cost_target > 0
    if (cost_target is not None and cost_target > 0):
        obj += pesos[1] * dv2 / cost_target
    obj += pesos[2] * dv3 / inst['t_Eq'] # equidad siempre tiene meta fija
    if inst['t_GR'] > 0:
        obj += pesos[3] * dv4 / inst['t_GR'] # fiabilidad siempre tiene meta fija

    sol['of'] = obj
    return obj

def isFeasible(sol):
    """
    Comprueba si la solución cumple todas las restricciones:
    oferta, demanda, disponibilidad de vehículos y presupuesto.
    """
    inst = sol['instance']
    used_supply = {d: 0.0 for d in inst['depots']}
    received = {j: 0.0 for j in inst['nodes']}
    veh_used = {d: {'small':0, 'medium':0, 'large':0} for d in inst['depots']}
    total_cost = 0.0

    for (dep, node, vtype, tons) in sol['envios']:
        used_supply[dep] += tons
        received[node] += tons
        n_veh = math.ceil(tons / inst['veh_cap'][vtype])
        veh_used[dep][vtype] += n_veh
        key = (dep, node)
        if key not in inst['arcs']:
            return False
        dist, _, _ = inst['arcs'][key]
        total_cost += n_veh * inst['veh_cf'][vtype] * dist + tons * inst['veh_cv'][vtype] * dist

    for d in inst['depots']:
        if used_supply[d] > inst['supply'][d]:
            return False
        for vt in ['small','medium','large']:
            if veh_used[d][vt] > inst['veh_avail'][d][vt]:
                return False
    for j in inst['nodes']:
        if received[j] > inst['demand'][j]:
            return False
    if total_cost > inst['budget']:
        return False
    return True

def copySolution(sol):
    """
    Crea una copia independiente de la solución (nueva lista de envíos).
    """
    new_sol = {
        'instance': sol['instance'],
        'envios': list(sol['envios']),   # copia superficial de la lista de tuplas
        'of': sol['of']
    }
    return new_sol

def distanceToSol(sol, candidate):
    """
    Calcula la "distancia" de un envío candidato a la solución actual.
    Para el MDP era la suma de distancias a los elementos ya seleccionados.
    Aquí usaremos una métrica que combine coste bajo y alta fiabilidad,
    para guiar la selección voraz (LRC).
    candidate = (dep, node, vtype, tons)
    """
    inst = sol['instance']
    dep, node, vtype, tons = candidate
    arco = (dep, node)
    if arco not in inst['arcs']:
        return float('inf')
    dist, _, rel = inst['arcs'][arco]
    # Coste aproximado del envío
    n_veh = math.ceil(tons / inst['veh_cap'][vtype])
    approx_cost = n_veh * inst['veh_cf'][vtype] * dist + tons * inst['veh_cv'][vtype] * dist
    # Queremos minimizar coste y maximizar fiabilidad -> combinación lineal
    # Nota: esta función se usará en la fase constructiva (LRC) para evaluar cada candidato
    # Pondremos pesos (por ejemplo, 0.7 para coste, 0.3 para fiabilidad)
    w_cost = 0.7 # peso para coste
    w_rel = 0.3
    return w_cost * approx_cost + w_rel * (1 - rel)

def contains(sol, dep, node, vtype):
    """
    Comprueba si ya existe un envío exactamente igual en la solución.
    """
    for env in sol['envios']:
        if env[0] == dep and env[1] == node and env[2] == vtype:
            return True
    return False

def printSolution(sol):
    """
    Muestra la solución de forma legible.
    """
    print("Envíos realizados:")
    for env in sol['envios ']:
        dep, node, vtype, tons = env
        print(f"  D{dep} -> N{node} ({vtype}): {tons:.1f} t")
    print(f"Valor objetivo agregado: {sol['of']:.6f}")