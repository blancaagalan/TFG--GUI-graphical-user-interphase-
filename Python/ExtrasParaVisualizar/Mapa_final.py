import folium
from folium import plugins
from branca.element import Template, MacroElement

# 1. Diccionario con coordenadas reales (Latitud, Longitud)
nodos = {
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

# 2. Creamos el mapa centrado en la zona de Kanto (Tokio)
m = folium.Map(location=[35.72, 139.60], zoom_start=9, tiles='CartoDB positron')

# 3. Dibujar los marcadores de nodos (círculos limpios, sin etiquetas de texto estáticas)
for nombre, coord in nodos.items():
    if 'D' in nombre:
        # Depósitos en rojo con pin estándar
        folium.Marker(
            coord,
            tooltip=nombre,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    else:
        # Nodos de demanda en azul
        folium.CircleMarker(
            coord, 
            tooltip=nombre, 
            radius=7, 
            color='#1E90FF', 
            fill=True, 
            fill_color='#87CEFA',
            fill_opacity=0.8,
            weight=2
        ).add_to(m)

# 4. Definición de las rutas ACTIVAS en la solución Equilibrada (seed 123)
# Estructura: (Origen, Destino, Cantidad t, Vehículos Small, Vehículos Medium, Vehículos Large, Distancia km)
rutas_activas = [
    ('D1 (Haneda)', 'N5 (Kawasaki)', 255.0, 0, 17, 0, 4),
    ('D1 (Haneda)', 'N7 (Kofu)', 35.0, 7, 0, 0, 140),
    ('D1 (Haneda)', 'N9 (Chiba)', 165.0, 0, 11, 0, 50),
    ('D1 (Haneda)', 'N10 (Tokio)', 645.0, 29, 0, 20, 20),
    ('D2 (Narita)', 'N2 (Funabashi)', 105.0, 0, 4, 2, 45),
    ('D3 (Yokohama)', 'N1 (Fujisawa)', 75.0, 0, 5, 0, 26),
    ('D3 (Yokohama)', 'N4 (Kawagoe)', 60.0, 2, 0, 2, 45),
    ('D3 (Yokohama)', 'N6 (Hachioji)', 95.0, 4, 5, 0, 50),
    ('D4 (Tsuchiura)', 'N3 (Kasukabe)', 40.0, 8, 0, 0, 52),
    ('D4 (Tsuchiura)', 'N8 (Saitama)', 225.0, 0, 5, 6, 60),
    ('D4 (Tsuchiura)', 'N10 (Tokio)', 885.0, 35, 24, 14, 70)
]

for orig, dest, cant, s, m_v, l, dist in rutas_activas:
    coord_o = nodos[orig]
    coord_d = nodos[dest]
    
    # Orientación de la línea de oeste a este para centrar el texto correctamente
    if coord_o[1] > coord_d[1]:
        coordenadas_dibujo = [coord_d, coord_o]
    else:
        coordenadas_dibujo = [coord_o, coord_d]
        
    # Texto de información en hover
    veh_txt = []
    if s > 0: veh_txt.append(f"{s}P")
    if m_v > 0: veh_txt.append(f"{m_v}M")
    if l > 0: veh_txt.append(f"{l}G")
    veh_str = "+".join(veh_txt)
    tooltip_txt = f"<b>Ruta:</b> {orig} &rarr; {dest}<br><b>Cantidad:</b> {cant:.1f} t<br><b>Vehículos:</b> {veh_str}<br><b>Distancia:</b> {dist} km"
    
    # Grosor de la línea proporcional al flujo
    grosor = 2 + (cant / 150.0)
    if grosor > 10: grosor = 10
    
    linea = folium.PolyLine(
        coordenadas_dibujo,
        color='#4B0082', # Índigo
        weight=grosor,
        opacity=0.7,
        tooltip=tooltip_txt
    )
    linea.add_to(m)
    
    # Solo mostrar toneladas en el mapa, sin vehículos ni nombres, manteniendo el mapa limpio
    texto_path = f"{cant:.0f} t"
    plugins.PolyLineTextPath(
        linea,
        texto_path,
        repeat=False,
        center=True,
        offset=12,
        attributes={'fill': '#4B0082', 'font-weight': 'bold', 'font-size': '10'}
    ).add_to(m)

# 5. Leyenda flotante
leyenda_html = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed; 
    bottom: 30px; 
    left: 30px; 
    width: 280px; 
    height: 140px; 
    background-color: white; 
    border: 2px solid #ccc; 
    z-index: 9999; 
    font-size: 13px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 3px 3px 6px rgba(0,0,0,0.2);
    ">
    <b style="font-size: 14px; color: #333;">Mapa de Distribución Óptimo</b><br>
    <span style="color: #666; font-size: 11px; font-style: italic;">Configuración Equilibrada (Compromiso)</span>
    <div style="margin-top: 10px;">
        <span style="display:inline-block; width:10px; height:10px; background-color:#d9534f; border:2px solid #7a2825; border-radius:50%; margin-right:8px;"></span> Depósito (Origen)
    </div>
    <div style="margin-top: 5px;">
        <span style="display:inline-block; width:10px; height:10px; background-color:#87CEFA; border:2px solid #1E90FF; border-radius:50%; margin-right:8px;"></span> Centro Regional (Demanda)
    </div>
    <div style="margin-top: 5px;">
        <span style="display:inline-block; width:22px; height:3px; background-color:#4B0082; margin-right:8px; vertical-align:middle;"></span> Ruta Activa (Grosor &prop; Flujo)
    </div>
</div>
{% endmacro %}
"""
macro = MacroElement()
macro._template = Template(leyenda_html)
m.get_root().add_child(macro)

# 6. Guardar mapa interactivo
m.save("c:/Documentos/TFG/TFG/Python/ExtrasParaVisualizar/mapa_logistifinal.html")
print("Updated Mapa_final.py and saved mapa_logistifinal.html")
