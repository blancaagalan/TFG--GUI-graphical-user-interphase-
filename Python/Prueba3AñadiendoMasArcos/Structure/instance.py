def createInstance():
    instance = {}

    # Conjuntos básicos
    instance['depositos'] = [1, 2, 3, 4]
    instance['nodes'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Oferta y demanda agregadas (en toneladas)
    #instance['supply'] = {1: 1300, 2: 520, 3: 310, 4: 1270} #Sumandole comida mas medicinas
    instance['supply'] = {1: 1100, 2: 440, 3: 230, 4: 1270}

    #instance['demand'] = {1: 85, 2: 125, 3: 45, 4: 70, 5: 300, #Sumandole comida mas medicinas
                     # 6: 115, 7: 40, 8: 250, 9: 195, 10: 1800}
    instance['demand'] = {1: 75, 2: 105, 3: 40, 4: 60, 5: 255,
                      6: 95, 7: 35, 8: 225, 9: 165, 10: 1530}
    instance['total_demanda'] = sum(instance['demand'].values())

    # Disponibilidad de vehículos por depósito
    instance['veh_avail'] = {
        1: {'small': 50, 'medium': 30, 'large': 20},
        2: {'small': 12, 'medium': 8,  'large': 2},
        3: {'small': 7,  'medium': 13, 'large': 2},
        4: {'small': 50, 'medium': 30, 'large': 20},
    }

    # Características de los vehículos
    instance['veh_cap'] = {'small': 5, 'medium': 15, 'large': 25}
    instance['veh_cf'] = {'small': 20, 'medium': 50, 'large': 70}
    instance['veh_cv'] = {'small': 1.0, 'medium': 1.1, 'large': 1.3}

    # Arcos directos DEPÓSITO -> NODO DE DEMANDA (solo orígenes en depósitos)
    # Formato: (deposito, nodo) -> (dist, vel, fiabilidad)
    arcs_list = [
        (1, 2, 35, 90, 0.85),
        (1, 5, 4, 50, 0.78),
        (1, 9, 50, 90, 0.89),
        (1, 10, 20, 90, 0.97),
        (2, 2, 45, 50, 0.99),
        (2, 9, 35, 90, 0.80),
        (3, 1, 26, 50, 0.99),
        (3, 5, 20, 70, 0.98),
        (3, 6, 50, 70, 0.29),
        (3, 4, 45, 70, 0.75),   # arco añadido para conectar N4
        (4, 2, 67, 90, 0.10),
        (4, 3, 52, 90, 0.52),
        (4, 10, 70, 90, 0.87),
        # Arcos adicionales para garantizar cobertura total
        (1, 7, 140, 80, 0.70),   # D1->N7 (Kofu)
        (4, 7, 180, 70, 0.65),   # D4->N7
        (1, 8, 120, 85, 0.80),   # D1->N8 (Saitama)
        (2, 8, 95, 80, 0.85),    # D2->N8
        (4, 8, 60, 90, 0.90),    # D4->N8
    ]
    instance['arcs'] = {}
    for (orig, dest, dist, vel, fiab) in arcs_list:
        instance['arcs'][(orig, dest)] = (dist, vel, fiab)

    # Presupuesto y metas
    instance['budget'] = 1_000_000  # USD
    instance['t_Eq'] = 1e-4     # meta equidad (muy pequeña)
    instance['t_GR'] = 1.2      # meta -ln(R_global)

    return instance
