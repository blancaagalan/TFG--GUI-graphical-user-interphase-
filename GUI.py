import os
import sys
import math
import random
import time
import pandas as pd
import folium
from folium import plugins
from branca.element import Template, MacroElement

# Ensure Streamlit is imported
try:
    import streamlit as st
except ImportError:
    st = None

# Add Python/Prueba3AñadiendoMasArcos to path
sys.path.append(os.path.abspath('Python/Prueba3AñadiendoMasArcos'))

try:
    from Structure import instance, solution1
    from Algorithms import grasp
except ImportError as e:
    st.error(f"Error importando módulos del solucionador: {e}")

# Geographic Coordinates (Lat, Lon) for Kanto Network
nodos_coords = {
    'D1 (Haneda)': (35.5494, 139.7798),
    'D2 (Narita)': (35.7776, 140.3186),
    'D3 (Yokohama)': (35.4503, 139.6644),
    'D4 (Tsuchiura)': (36.0835, 140.1983),
    'N1 (Fujisawa)': (35.3389, 139.4875),
    'N2 (Funabashi)': (35.6947, 139.9826),
    'N3 (Kasukabe)': (35.9751, 139.7544),
    'N4 (Kawagoe)': (35.9251, 139.4858),
    'N5 (Kawasaki)': (35.5308, 139.7029),
    'N6 (Hachioji)': (35.6581, 139.3244),
    'N7 (Kofu)': (35.6638, 138.5683),     
    'N8 (Saitama)': (35.8617, 139.6455),  
    'N9 (Chiba)': (35.6073, 140.1063),
    'N10 (Tokio)': (35.6812, 139.7671)
}

dep_names = {1: 'D1 (Haneda)', 2: 'D2 (Narita)', 3: 'D3 (Yokohama)', 4: 'D4 (Tsuchiura)'}
node_names = {
    1: 'N1 (Fujisawa)', 2: 'N2 (Funabashi)', 3: 'N3 (Kasukabe)', 4: 'N4 (Kawagoe)', 5: 'N5 (Kawasaki)',
    6: 'N6 (Hachioji)', 7: 'N7 (Kofu)', 8: 'N8 (Saitama)', 9: 'N9 (Chiba)', 10: 'N10 (Tokio)'
}

def generate_map_html(sol, inst, display_title, subtitle):
    # Center map in Kanto
    m = folium.Map(location=[35.72, 139.60], zoom_start=9, tiles='CartoDB positron')
    
    # Add Markers
    for nombre, coord in nodos_coords.items():
        if 'D' in nombre:
            folium.Marker(
                coord, 
                tooltip=nombre, 
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        else:
            folium.CircleMarker(
                coord, 
                tooltip=nombre, 
                radius=8, 
                color='#1E90FF', 
                fill=True, 
                fill_color='#87CEFA',
                fill_opacity=0.8
            ).add_to(m)
            
    # Group shipments
    rutas_dict = {}
    for (dep_idx, node_idx, vt, tons) in sol['envios']:
        if tons < 0.01:
            continue
        key = (dep_idx, node_idx)
        if key not in rutas_dict:
            rutas_dict[key] = {'tons': 0.0, 'small': 0, 'medium': 0, 'large': 0}
        rutas_dict[key]['tons'] += tons
        n_veh = math.ceil(tons / inst['veh_cap'][vt])
        rutas_dict[key][vt] += n_veh
        
    # Draw routes
    for (dep_idx, node_idx), info in rutas_dict.items():
        orig_name = dep_names[dep_idx]
        dest_name = node_names[node_idx]
        coord_o = nodos_coords[orig_name]
        coord_d = nodos_coords[dest_name]
        
        # Orient west to east for label readability
        if coord_o[1] > coord_d[1]:
            coordenadas_dibujo = [coord_d, coord_o]
        else:
            coordenadas_dibujo = [coord_o, coord_d]
            
        dist, _, _ = inst['arcs'][(dep_idx, node_idx)]
        cant = info['tons']
        s = info['small']
        m_v = info['medium']
        l = info['large']
        
        veh_txt = []
        if s > 0: veh_txt.append(f"{s}P")
        if m_v > 0: veh_txt.append(f"{m_v}M")
        if l > 0: veh_txt.append(f"{l}G")
        veh_str = "+".join(veh_txt)
        
        tooltip_txt = f"<b>Ruta:</b> {orig_name} &rarr; {dest_name}<br><b>Cantidad:</b> {cant:.1f} t<br><b>Vehículos:</b> {veh_str}<br><b>Distancia:</b> {dist} km"
        
        # Thickness proportional to flow
        grosor = 2 + (cant / 150.0)
        if grosor > 10: grosor = 10
        
        linea = folium.PolyLine(
            coordenadas_dibujo,
            color='#4B0082', # Indigo
            weight=grosor,
            opacity=0.75,
            tooltip=tooltip_txt
        )
        linea.add_to(m)
        
        # Text overlay
        texto_path = f"{cant:.0f} t"
        plugins.PolyLineTextPath(
            linea,
            texto_path,
            repeat=False,
            center=True,
            offset=12,
            attributes={'fill': '#4B0082', 'font-weight': 'bold', 'font-size': '11'}
        ).add_to(m)
        
    # Floating legend Element
    leyenda_html = f"""
    {{% macro html(this, kwargs) %}}
    <div style="
        position: fixed; 
        bottom: 30px; 
        left: 30px; 
        width: 320px; 
        height: 160px; 
        background-color: white; 
        border: 2px solid #ccc; 
        z-index: 9999; 
        font-size: 13px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        ">
        <b style="font-size: 14px; color: #333;">{display_title}</b><br>
        <span style="color: #666; font-size: 11px; font-style: italic;">{subtitle}</span>
        <div style="margin-top: 10px;">
            <span style="display:inline-block; width:12px; height:12px; background-color:red; border-radius:50%; margin-right:8px;"></span> Depósito de Suministro (Origen)
        </div>
        <div style="margin-top: 5px;">
            <span style="display:inline-block; width:12px; height:12px; background-color:#87CEFA; border:2px solid #1E90FF; border-radius:50%; margin-right:8px;"></span> Centro Regional (Demanda)
        </div>
        <div style="margin-top: 5px;">
            <span style="display:inline-block; width:22px; height:4px; background-color:#4B0082; margin-right:8px; vertical-align:middle;"></span> Ruta Activa (Grosor &prop; Flujo)
        </div>
        <div style="margin-top: 8px; font-size: 10px; color: #777; border-top: 1px solid #eee; padding-top: 5px;">
            Vehículos: P (Pequeño, 5t) | M (Mediano, 15t) | G (Grande, 25t)
        </div>
    </div>
    {{% endmacro %}}
    """
    macro = MacroElement()
    macro._template = Template(leyenda_html)
    m.get_root().add_child(macro)
    
    return m._repr_html_()

def main_gui():
    st.set_page_config(page_title="OptiRoute-Kanto GRASP", page_icon="🚚", layout="wide")
    
    # Custom CSS for rich aesthetics
    st.markdown("""
    <style>
    .main-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .subtitle {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 16px;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #3B82F6;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='main-title'>🚚 OptiRoute-Kanto</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Planificador Multiobjetivo Interactivo para la Distribución de Ayuda Humanitaria (Metaheurística GRASP)</div>", unsafe_allow_html=True)
    
    # Initialize session state for inputs
    if 'w_cost' not in st.session_state:
        st.session_state.w_cost = 0.33
    if 'w_eq' not in st.session_state:
        st.session_state.w_eq = 0.33
    if 'w_gr' not in st.session_state:
        st.session_state.w_gr = 0.34
    if 'alpha' not in st.session_state:
        st.session_state.alpha = 0.3
    if 'max_iter' not in st.session_state:
        st.session_state.max_iter = 400
        
    # Sidebar
    st.sidebar.header("⚙️ Parámetros del Modelo")
    
    # Presets Section
    st.sidebar.subheader("📌 Escenarios Preconfigurados")
    col_p1, col_p2, col_p3 = st.sidebar.columns(3)
    if col_p1.button("C- 1"):
        st.session_state.w_cost = 0.55
        st.session_state.w_eq = 0.40
        st.session_state.w_gr = 0.05
        st.session_state.alpha = 0.3
    if col_p2.button("R- 2"):
        st.session_state.w_cost = 0.65
        st.session_state.w_eq = 0.10
        st.session_state.w_gr = 0.25
        st.session_state.alpha = 0.3
    if col_p3.button("C- 2"):
        st.session_state.w_cost = 0.30
        st.session_state.w_eq = 0.05
        st.session_state.w_gr = 0.65
        st.session_state.alpha = 0.3
        
    st.sidebar.markdown("---")
    
    # Sliders
    st.sidebar.subheader("⚖️ Pesos de la Segunda Fase")
    w_cost = st.sidebar.slider("Peso Coste (w_Cost)", 0.0, 1.0, step=0.01, key="w_cost")
    w_eq = st.sidebar.slider("Peso Equidad (w_Eq)", 0.0, 1.0, step=0.01, key="w_eq")
    w_gr = st.sidebar.slider("Peso Fiabilidad (w_GR)", 0.0, 1.0, step=0.01, key="w_gr")
    
    # Real-time normalization
    w_sum = w_cost + w_eq + w_gr
    if w_sum > 0:
        w_cost_n = w_cost / w_sum
        w_eq_n = w_eq / w_sum
        w_gr_n = w_gr / w_sum
    else:
        w_cost_n, w_eq_n, w_gr_n = 0.33, 0.33, 0.34
        
    st.sidebar.markdown(f"**Pesos Normalizados (Suma = 1.0):**")
    st.sidebar.markdown(f"- 💰 Coste: `{w_cost_n:.3f}`")
    st.sidebar.markdown(f"- ⚖️ Equidad: `{w_eq_n:.3f}`")
    st.sidebar.markdown(f"- 🛡️ Fiabilidad: `{w_gr_n:.3f}`")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Configuración GRASP")
    alpha = st.sidebar.slider("Parámetro de codicia (alpha)", 0.0, 1.0, step=0.05, key="alpha")
    max_iter = st.sidebar.slider("Iteraciones Máximas", 50, 1000, step=50, key="max_iter")
    
    # Execution Button
    run_grasp = st.sidebar.button("🚀 EJECUTAR OPTIMIZACIÓN GRASP", use_container_width=True)
    
    # Initial execution state
    inst = instance.createInstance()
    
    # Default Solver Run if not executed yet
    if 'solution' not in st.session_state or run_grasp:
        random.seed(123)
        # Suppress prints
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        t0 = time.time()
        sol, _ = grasp.execute(inst, max_iter=max_iter, max_no_improv=5000, alpha=alpha,
                               w_cost=w_cost_n, w_eq=w_eq_n, w_gr=w_gr_n)
        t_exec = time.time() - t0
        sys.stdout = old_stdout
        
        st.session_state.solution = sol
        st.session_state.t_exec = t_exec
        st.session_state.cur_weights = (w_cost_n, w_eq_n, w_gr_n)
        st.session_state.cur_params = (alpha, max_iter)
        if run_grasp:
            st.toast("¡GRASP optimizado con éxito!", icon="✅")
            
    sol = st.session_state.solution
    t_exec = st.session_state.t_exec
    c_w = st.session_state.cur_weights
    c_p = st.session_state.cur_params
    
    # ------------------ MAIN SCREEN ------------------
    
    # Metrics Banner
    st.subheader("📊 Indicadores de Rendimiento de la Solución")
    col1, col2, col3, col4 = st.columns(4)
    
    # Evaluate solution metrics dynamically
    cant_entregada, coste_total, equidad_val, gr_val = solution1.evaluate(sol)
    fiab_val = math.exp(-gr_val)
    
    # Total tonnage delivered
    col1.metric("📦 Ayuda Entregada", f"{cant_entregada:.1f} t", "100% Cobertura")
    
    # Cost
    col2.metric("💰 Coste Total", f"${coste_total:.2f} USD")
    
    # Equity (Max deficit)
    col3.metric("⚖️ Inequidad (Max Déficit)", f"{equidad_val:.4f}", "Perfecta Equidad" if equidad_val < 1e-4 else None)
    
    # Reliability
    neg_ln_r = gr_val
    col4.metric("🛡️ Fiabilidad Global (R)", f"{fiab_val*100:.3f} %", f"-ln R = {neg_ln_r:.3f}")
    
    st.markdown(f"<small>Calculado en <b>{t_exec:.3f} segundos</b> usando GRASP ({c_p[1]} iteraciones, &alpha;={c_p[0]})</small>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Tabs
    tab_map, tab_table, tab_fleet = st.tabs(["🗺️ Mapa Interactivo de Rutas", "📋 Desglose de Envíos", "🚛 Resumen de Flota"])
    
    with tab_map:
        st.write("El grosor de las líneas representa la cantidad de ayuda transportada. Coloca el cursor sobre las líneas para ver distancias y vehículos.")
        w_c, w_e, w_g = c_w
        title_map = f"Pesos: Coste={w_c:.2f}, Equidad={w_e:.2f}, Fiabilidad={w_g:.2f}"
        map_html = generate_map_html(sol, inst, "Mapa de Distribución Dinámico", title_map)
        st.components.v1.html(map_html, height=600, scrolling=False)
        
    with tab_table:
        st.subheader("Desglose operativo de envíos por ruta y tipo de vehículo")
        
        # Build route table data
        routes_data = []
        
        # Group by origin and destination
        grouped_routes = {}
        for (orig_idx, dest_idx, vt, tons) in sol['envios']:
            if tons < 0.01:
                continue
            orig = dep_names[orig_idx]
            dest = node_names[dest_idx]
            n_veh = math.ceil(tons / inst['veh_cap'][vt])
            
            key = (orig, dest)
            if key not in grouped_routes:
                grouped_routes[key] = {'small': (0, 0.0), 'medium': (0, 0.0), 'large': (0, 0.0)}
            grouped_routes[key][vt] = (n_veh, tons)
            
        # Format for dataframe
        for (orig, dest), data in sorted(grouped_routes.items(), key=lambda x: (x[0][0], x[0][1])):
            s_veh, s_t = data['small']
            m_veh, m_t = data['medium']
            l_veh, l_t = data['large']
            total_t = s_t + m_t + l_t
            
            routes_data.append({
                "Origen": orig,
                "Destino": dest,
                "Veh. Pequeños": s_veh if s_veh > 0 else 0,
                "t Pequeños": s_t if s_t > 0 else 0.0,
                "Veh. Medianos": m_veh if m_veh > 0 else 0,
                "t Medianos": m_t if m_t > 0 else 0.0,
                "Veh. Grandes": l_veh if l_veh > 0 else 0,
                "t Grandes": l_t if l_t > 0 else 0.0,
                "Total t": total_t
            })
            
        df = pd.DataFrame(routes_data)
        if not df.empty:
            st.dataframe(
                df.style.format({
                    "t Pequeños": "{:.1f}",
                    "t Medianos": "{:.1f}",
                    "t Grandes": "{:.1f}",
                    "Total t": "{:.1f}"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay envíos en este escenario.")
            
    with tab_fleet:
        st.subheader("🚛 Uso Total de la Flota de Vehículos")
        
        # Calculate total vehicle counts
        total_veh = {'small': 0, 'medium': 0, 'large': 0}
        total_tons = {'small': 0.0, 'medium': 0.0, 'large': 0.0}
        
        for (orig_idx, dest_idx, vt, tons) in sol['envios']:
            if tons < 0.01:
                continue
            n_veh = math.ceil(tons / inst['veh_cap'][vt])
            total_veh[vt] += n_veh
            total_tons[vt] += tons
            
        col_f1, col_f2, col_f3 = st.columns(3)
        
        col_f1.metric("🚚 Vehículos Pequeños (5t)", f"{total_veh['small']} unidades", f"{total_tons['small']:.1f} toneladas")
        col_f2.metric("🚛 Vehículos Medianos (15t)", f"{total_veh['medium']} unidades", f"{total_tons['medium']:.1f} toneladas")
        col_f3.metric("🛞 Vehículos Grandes (25t)", f"{total_veh['large']} unidades", f"{total_tons['large']:.1f} toneladas")
        
        # Total vehicles sum
        total_all_veh = sum(total_veh.values())
        st.info(f"**Total de camiones en carretera:** {total_all_veh} vehículos utilizados para transportar {cant_entregada:.1f} toneladas de ayuda.")

if __name__ == '__main__':
    if st is None:
        print("Error: streamlit is not installed. Run 'pip install streamlit' and run using 'streamlit run GUI.py'")
    else:
        main_gui()
