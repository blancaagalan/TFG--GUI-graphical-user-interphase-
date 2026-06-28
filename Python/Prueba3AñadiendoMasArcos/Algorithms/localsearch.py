import math
from Structure import solution1

def localSearch(sol, Q_target, cost_target, weights, max_no_mejora=5000): # max_no_mejora es el número máximo de iteraciones sin mejora antes de detener la búsqueda local
    """
    Búsqueda local para mejorar una solución factible.
    No modifica la cantidad total Q (fijada a Q_target).
    """
    inst = sol['instance']
    # Función interna para evaluar una solución y devolver su objetivo agregado
    def eval_obj(s): # evalúa la solución s y devuelve su función objetivo agregada según los pesos y metas dados, se basa en la función solution1.evaluate para obtener los valores de Q, coste, eq y gr, y luego llama a solution1.aggregatedObjective para calcular el valor agregado de la función objetivo
        Q, coste, eq, gr = solution1.evaluate(s) # type: ignore # se ignora el tipo porque solution1.evaluate devuelve una tupla de 4 valores, pero aquí solo nos interesa el valor agregado que se calcula a partir de esos 4 valores, por lo que no es necesario especificar el tipo exacto de retorno de solution1.evaluate
        return solution1.aggregatedObjective(Q, coste, eq, gr, Q_target, cost_target, weights, inst)

    current_sol = solution1.copySolution(sol)
    current_obj = eval_obj(current_sol)
    best_sol = solution1.copySolution(current_sol)
    best_obj = current_obj
    no_improv = 0

    while no_improv < max_no_mejora:
        improved = False

        # --- Movimiento 1: Reasignar toneladas entre dos envíos al mismo nodo ---
        # Agrupamos índices por nodo de demanda
        by_node = {}
        for idx, env in enumerate(current_sol['envios']):
            node = env[1]
            by_node.setdefault(node, []).append(idx)

        for node, indices in by_node.items():
            if len(indices) < 2:
                continue
            for i in range(len(indices)):
                for j in range(i+1, len(indices)):
                    idx1, idx2 = indices[i], indices[j]
                    dep1, node1, vt1, t1 = current_sol['envios'][idx1] # dep1 es el depósito de origen del envío idx1, node1 es el nodo de demanda del envío idx1, vt1 es el tipo de vehículo del envío idx1, t1 es la cantidad enviada en el envío idx1
                    dep2, node2, vt2, t2 = current_sol['envios'][idx2]
                    # Probar a transferir delta toneladas desde idx1 a idx2 basadas en porcentaje
                    deltas = [
                        max(1, int(t1 * 0.1)),
                        max(1, int(t1 * 0.25)),
                        max(1, int(t1 * 0.5))
                    ]
                    for delta in deltas:
                        if delta > t1:
                            continue
                        # Crear nueva solución modificando solo esos dos envíos
                        new_sol = solution1.copySolution(current_sol)
                        new_sol['envios'][idx1] = (dep1, node1, vt1, t1 - delta)
                        new_sol['envios'][idx2] = (dep2, node2, vt2, t2 + delta)
                        if solution1.isFeasible(new_sol):
                            obj_new = eval_obj(new_sol)
                            if obj_new < current_obj - 1e-9:
                                current_sol = new_sol
                                current_obj = obj_new
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

        if not improved:
            # --- Movimiento 2: Cambiar tipo de vehículo o depósito de un envío ---
            for idx, env in enumerate(current_sol['envios']):
                dep, node, vt, tons = env
                # Cambiar tipo de vehículo (mismo depósito, mismo nodo)
                for new_vt in ['small', 'medium', 'large']:
                    if new_vt == vt:
                        continue
                    new_sol = solution1.copySolution(current_sol)
                    new_sol['envios'][idx] = (dep, node, new_vt, tons)
                    if solution1.isFeasible(new_sol):
                        obj_new = eval_obj(new_sol)
                        if obj_new < current_obj - 1e-9:
                            current_sol = new_sol
                            current_obj = obj_new
                            improved = True
                            break
                if improved:
                    break
                # Cambiar depósito (mismo nodo, mismo tipo)
                for new_dep in inst['depositos']:
                    if new_dep == dep:
                        continue
                    if (new_dep, node) not in inst['arcs']:
                        continue
                    new_sol = solution1.copySolution(current_sol)
                    new_sol['envios'][idx] = (new_dep, node, vt, tons)
                    if solution1.isFeasible(new_sol):
                        obj_new = eval_obj(new_sol)
                        if obj_new < current_obj - 1e-9:
                            current_sol = new_sol
                            current_obj = obj_new
                            improved = True
                            break
                if improved:
                    break

        if not improved:
            # --- Movimiento 3: Eliminar envío pequeño y redistribuir su carga ---
            if len(current_sol['envios']) > 1:
                # Buscar el envío con menor tonelaje
                min_idx = None
                min_tons = float('inf') #float('inf') es un valor especial que representa infinito, se usa aquí para inicializar min_tons con un valor muy grande, de modo que cualquier envío real tendrá menos toneladas que este valor inicial 
                for idx, env in enumerate(current_sol['envios']):
                    if env[3] < min_tons:
                        min_tons = env[3]
                        min_idx = idx
                if min_tons < 10:   # umbral de 10 toneladas
                    dep, node, vt, tons = current_sol['envios'][min_idx]
                    # Buscar otros envíos al mismo nodo
                    others = [i for i, env in enumerate(current_sol['envios'])
                              if i != min_idx and env[1] == node]
                    if others:
                        # Primero eliminamos el envío pequeño
                        new_sol = solution1.copySolution(current_sol)
                        del new_sol['envios'][min_idx]
                        # Volvemos a calcular los envíos al mismo nodo (ya sin el eliminado)
                        others_new = [i for i, env in enumerate(new_sol['envios']) if env[1] == node]
                        for oidx in others_new:
                            o_dep, o_node, o_vt, o_tons = new_sol['envios'][oidx]
                            tentative = o_tons + tons
                            test_sol = solution1.copySolution(new_sol)
                            test_sol['envios'][oidx] = (o_dep, o_node, o_vt, tentative)
                            if solution1.isFeasible(test_sol):
                                obj_new = eval_obj(test_sol)
                                if obj_new < current_obj - 1e-9:
                                    current_sol = test_sol
                                    current_obj = obj_new
                                    improved = True
                                    break                       
                                 # Si no se pudo redistribuir, no se hace nada (no improved)
    
        if improved:
            best_sol = solution1.copySolution(current_sol)
            best_obj = current_obj
            no_improv = 0
        else:
            break  # Si no hubo mejora en ningún movimiento, hemos alcanzado un óptimo local y terminamos.

    return best_sol, best_obj