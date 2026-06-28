import folium
from branca.element import Template, MacroElement  # Necesario para dibujar la leyenda

# 1. Diccionario con coordenadas reales (Latitud, Longitud)
# 1. Diccionario con coordenadas reales (Latitud, Longitud) ajustadas
nodos = {
    'D1 (Haneda)': (35.5494, 139.7798),
    'D2 (Narita)': (35.7776, 140.3186),   # <--- Ajustado sobre la ciudad de Narita
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
    'N10 (Tokio)': (35.6812, 139.7671)    # <--- Ajustado sobre el centro (Tokyo Station)
}
# 2. Creamos el mapa centrado en la zona de Kanto (Tokio)
m = folium.Map(location=[35.6895, 139.6917], zoom_start=9, tiles='CartoDB positron')

# 3. Dibujar los marcadores
for nombre, coord in nodos.items():
    if 'D' in nombre:
        folium.Marker(coord, tooltip=nombre, icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
    else:
        folium.CircleMarker(coord, tooltip=nombre, radius=8, color='blue', fill=True, fill_color='lightblue').add_to(m)

# 4. Definir las rutas normales (Arcos verdes originales)
rutas_verdes_originales = [
    ('D1 (Haneda)', 'N2 (Funabashi)'), ('D1 (Haneda)', 'N5 (Kawasaki)'), 
    ('D1 (Haneda)', 'N9 (Chiba)'), ('D1 (Haneda)', 'N10 (Tokio)'),
    ('D2 (Narita)', 'N2 (Funabashi)'), ('D2 (Narita)', 'N9 (Chiba)'),
    ('D3 (Yokohama)', 'N1 (Fujisawa)'), ('D3 (Yokohama)', 'N5 (Kawasaki)'), 
    ('D3 (Yokohama)', 'N6 (Hachioji)'),
    ('D4 (Tsuchiura)', 'N2 (Funabashi)'), ('D4 (Tsuchiura)', 'N3 (Kasukabe)'), 
    ('D4 (Tsuchiura)', 'N10 (Tokio)')
]

for origen, destino in rutas_verdes_originales:
    folium.PolyLine([nodos[origen], nodos[destino]], color='green', weight=3, opacity=0.6).add_to(m)

# 5. DIBUJAR LAS NUEVAS RUTAS TAMBIÉN EN VERDE
# Recuperamos la lista de las que antes eran amarillas
nuevas_rutas = [
    ('N4 (Kawagoe)', 'D3 (Yokohama)', 45, 0.75),
    ('D1 (Haneda)', 'N7 (Kofu)', 140, 0.70),
    ('D4 (Tsuchiura)', 'N7 (Kofu)', 180, 0.65),
    ('D1 (Haneda)', 'N8 (Saitama)', 120, 0.80),
    ('D2 (Narita)', 'N8 (Saitama)', 95, 0.85),
    ('D4 (Tsuchiura)', 'N8 (Saitama)', 60, 0.90)
]

for origen, destino, dist, fiab in nuevas_rutas:
    coord_o = nodos[origen]
    coord_d = nodos[destino]
    
    # Control de orientación para que las letras no salgan al revés
    if coord_o[1] > coord_d[1]:
        coordenadas_dibujo = [coord_d, coord_o]
    else:
        coordenadas_dibujo = [coord_o, coord_d]

    texto_flotante = f"{dist} km | Fiabilidad: {int(fiab*100)}%"
    
    folium.PolyLine(
        coordenadas_dibujo, 
        color='green',  # <--- CAMBIADO A VERDE
        weight=3, 
        opacity=0.6,
        tooltip=texto_flotante
    ).add_to(m)


# 6. AÑADIR LEYENDA FLOTANTE ACTUALIZADA
leyenda_html = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed; 
    bottom: 50px; 
    left: 50px; 
    width: 250px; 
    height: 120px; 
    background-color: white; 
    border:2px solid grey; 
    z-index:9999; 
    font-size:14px;
    border-radius: 8px;
    padding: 10px;
    box-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    ">
    <b>Leyenda de la Red</b><br>
    <div style="margin-top: 8px;">
        <span style="display:inline-block; width:12px; height:12px; background-color:red; border-radius:50%; margin-right:5px;"></span> Depósito de suministro
    </div>
    <div style="margin-top: 5px;">
        <span style="display:inline-block; width:12px; height:12px; background-color:lightblue; border:2px solid blue; border-radius:50%; margin-right:5px;"></span> Nodo de demanda
    </div>
    <div style="margin-top: 5px;">
        <span style="display:inline-block; width:20px; height:4px; background-color:green; margin-right:5px; vertical-align:middle;"></span> Rutas directas
    </div>
</div>
{% endmacro %}
"""
macro = MacroElement()
macro._template = Template(leyenda_html)
m.get_root().add_child(macro)


# 7. Guardar el resultado
m.save("mapa_logisticointro.html")
print("¡Éxito! Ejecutado con todas las rutas en verde y la leyenda actualizada a 'Rutas directas'.")