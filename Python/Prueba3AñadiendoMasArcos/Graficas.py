import json
import matplotlib.pyplot as plt #nos la descargamos para poder hacer las gráficas
import numpy as np
import math
def sanitize_filename(name):
    return name.replace(" ", "_").replace(".", "").replace("á", "a").replace("í", "i").replace("ó", "o")


# Cargar resultados reales desde el JSON generado por main.py
with open("resultados_modeloA.json", "r") as f:
    resultados = json.load(f)

# Normalización para radar (1 = mejor)
min_cost = min(d['coste'] for d in resultados)
max_cost = max(d['coste'] for d in resultados)
min_eq = min(d['eq'] for d in resultados)
max_eq = max(d['eq'] for d in resultados)
min_R = min(d['R'] for d in resultados)
max_R = max(d['R'] for d in resultados)

def norm_cost(c): return 1 - (c - min_cost)/(max_cost - min_cost) if max_cost>min_cost else 1
def norm_eq(e):   return 1 - (e - min_eq)/(max_eq - min_eq) if max_eq>min_eq else 1
def norm_R(r):    return (r - min_R)/(max_R - min_R) if max_R>min_R else 1

radar_vals = []
leyendas = ['Cuando el coste domina', 'Cuando la equidad domina', 'Cuando la fiabilidad domina', 'Equilibrado']
for d in resultados:
    radar_vals.append([norm_cost(d['coste']), norm_eq(d['eq']), norm_R(d['R'])])

# Nombres de los nodos de demanda
nombres_nodos = {
    1: 'Fujisawa', 2: 'Funabashi', 3: 'Kasukabe', 4: 'Kawagoe', 5: 'Kawasaki',
    6: 'Hachioji', 7: 'Kofu', 8: 'Saitama', 9: 'Chiba', 10: 'Tokio'
}

# Radar
def radar_plot(etiquetas, valores, leyendas, titulo):
    N = len(etiquetas)
    angulos = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angulos += angulos[:1]
    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    
    colores_radar = ['#b83b30', '#1a7f64', '#7d3c98', '#2c3e50']
    for i, val in enumerate(valores):
        val += val[:1]
        ax.plot(angulos, val, 'o-', linewidth=2, color=colores_radar[i], label=leyendas[i])
        ax.fill(angulos, val, color=colores_radar[i], alpha=0.08)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(etiquetas)
    ax.set_title(titulo, y=1.08, fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.1))
    plt.tight_layout()
    plt.savefig('fig5_1_radar.png', dpi=150)
    plt.close()

radar_plot(['Coste', 'Inequidad', 'Fiabilidad'], radar_vals, leyendas, 'Modelo A - Radar de criterios')

# Figura 5.2: Coste vs Inequidad
plt.figure(figsize=(7,5))
colores_scatter = ['#b83b30', '#1a7f64', '#7d3c98', '#2c3e50']
for i, d in enumerate(resultados):
    plt.scatter(d['coste'], d['eq'], color=colores_scatter[i], s=120, label=leyendas[i], alpha=0.85, edgecolors='#7f8c8d', linewidths=0.8)
    # Evitar superposición en las anotaciones desplazándolas ligeramente
    offset_y = 0.002 if i % 2 == 0 else -0.005
    plt.annotate(leyendas[i], (d['coste'], d['eq']), textcoords="offset points", xytext=(5, 5 + offset_y * 1000), fontsize=9, fontweight='bold')
plt.xlabel('Coste total (USD)', fontsize=10)
plt.ylabel('Inequidad (máx. déficit)', fontsize=10)
plt.title('Frente Coste vs Inequidad - Modelo A', fontsize=12, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig('fig5_2_coste_equidad.png', dpi=150)
plt.close()

# Figura 5.3: Composición de la flota
x = np.arange(len(leyendas))
ancho = 0.45
small = [d['small'] for d in resultados]
medium = [d['medium'] for d in resultados]
large = [d['large'] for d in resultados]

plt.figure(figsize=(8,5))
plt.bar(x, small, width=ancho, label='S - Pequeño (5t)', color='#b0c4de', edgecolor='#7f8c8d', linewidth=0.5)
plt.bar(x, medium, width=ancho, bottom=small, label='M - Mediano (15t)', color='#4682b4', edgecolor='#7f8c8d', linewidth=0.5)
plt.bar(x, large, width=ancho, bottom=np.array(small)+np.array(medium), label='L - Grande (25t)', color='#1f4e79', edgecolor='#7f8c8d', linewidth=0.5)
plt.xticks(x, leyendas)
plt.ylabel('Número de vehículos', fontsize=10)
plt.title('Composición de la flota por configuración - Modelo A', fontsize=12, fontweight='bold')
plt.legend(frameon=True, facecolor='white', edgecolor='none')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('fig5_3_flota.png', dpi=150)
plt.close()

# ============================================================
# NUEVAS FIGURAS: Vehículos por nodo para cada configuración
# ============================================================

for idx, d in enumerate(resultados):
    conf_name = leyendas[idx]
    veh_nodo = d['veh_por_nodo']   # dict: node -> {'small': x, 'medium': y, 'large': z}
    nodes = sorted(veh_nodo.keys(), key=int) # Ordenar numéricamente N1, N2, ..., N10
    small_vals = [veh_nodo[n]['small'] for n in nodes]
    medium_vals = [veh_nodo[n]['medium'] for n in nodes]
    large_vals = [veh_nodo[n]['large'] for n in nodes]
    
    # Figura A: valores absolutos
    x_pos = np.arange(len(nodes))
    width = 0.5
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x_pos, small_vals, width, label='S - Pequeño (5t)', color='#b0c4de', edgecolor='#7f8c8d', linewidth=0.5)
    ax.bar(x_pos, medium_vals, width, bottom=small_vals, label='M - Mediano (15t)', color='#4682b4', edgecolor='#7f8c8d', linewidth=0.5)
    ax.bar(x_pos, large_vals, width, bottom=np.array(small_vals)+np.array(medium_vals), label='L - Grande (25t)', color='#1f4e79', edgecolor='#7f8c8d', linewidth=0.5)
    ax.set_xlabel('Nodo de demanda', fontsize=10)
    ax.set_ylabel('Número de vehículos', fontsize=10)
    ax.set_title(f'Vehículos por nodo - {conf_name} (absoluto)', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'N{n} ({nombres_nodos[int(n)]})' for n in nodes], rotation=30, ha='right', fontsize=9)
    ax.legend(frameon=True, facecolor='white')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'fig_veh_nodo_abs_{sanitize_filename(conf_name)}.png', dpi=150)
    plt.close()

    # Figura B: porcentajes
    totals = [small_vals[i] + medium_vals[i] + large_vals[i] for i in range(len(nodes))]
    small_pct = [small_vals[i]/totals[i]*100 if totals[i]>0 else 0 for i in range(len(nodes))]
    medium_pct = [medium_vals[i]/totals[i]*100 if totals[i]>0 else 0 for i in range(len(nodes))]
    large_pct = [large_vals[i]/totals[i]*100 if totals[i]>0 else 0 for i in range(len(nodes))]
    
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x_pos, small_pct, width, label='S - Pequeño (5t)', color='#b0c4de', edgecolor='#7f8c8d', linewidth=0.5)
    ax.bar(x_pos, medium_pct, width, bottom=small_pct, label='M - Mediano (15t)', color='#4682b4', edgecolor='#7f8c8d', linewidth=0.5)
    ax.bar(x_pos, large_pct, width, bottom=np.array(small_pct)+np.array(medium_pct), label='L - Grande (25t)', color='#1f4e79', edgecolor='#7f8c8d', linewidth=0.5)
    ax.set_xlabel('Nodo de demanda', fontsize=10)
    ax.set_ylabel('Porcentaje de vehículos (%)', fontsize=10)
    ax.set_title(f'Vehículos por nodo - {conf_name} (porcentaje)', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'N{n} ({nombres_nodos[int(n)]})' for n in nodes], rotation=30, ha='right', fontsize=9)
    ax.legend(frameon=True, facecolor='white')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'fig_veh_nodo_pct_{sanitize_filename(conf_name)}.png', dpi=150)
    plt.close()


