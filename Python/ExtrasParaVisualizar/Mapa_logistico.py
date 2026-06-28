import sys
try:
    import folium 
except ImportError:
    print("Error: folium no está instalado. Instala con 'pip install folium' y vuelve a ejecutar.")
    sys.exit(1)
from folium import plugins
# 1. Diccionario con coordenadas reales (Latitud, Longitud)
nodos = {
    'D1 (Haneda)': (35.5494, 139.7798),
    'D2 (Narita)': (35.7720, 140.3929),
    'D3 (Yokohama)': (35.4503, 139.6644),
    'D4 (Tsuchiura)': (36.0835, 140.1983),
    'N1 (Fujisawa)': (35.3389, 139.4875),
    'N2 (Funabashi)': (35.6947, 139.9826),
    'N3 (Kasukabe)': (35.9751, 139.7544),
    'N4 (Kawagoe)': (35.9251, 139.4858),
    'N5 (Kawasaki)': (35.5308, 139.7029),
    'N6 (Hachioji)': (35.6581, 139.3244),
    'N9 (Chiba)': (35.6073, 140.1063),
    'N10 (Tokio)': (35.6895, 139.6917)
}

# 2. Creamos el mapa centrado en la zona de Kanto (Tokio)
m = folium.Map(location=[35.6895, 139.6917], zoom_start=9, tiles='CartoDB positron')

# 3. Dibujar los marcadores
# Los Depósitos irán en ROJO con icono de información. Los Nodos en AZUL.
for nombre, coord in nodos.items():
    if 'D' in nombre:
        folium.Marker(coord, tooltip=nombre, icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
    else:
        folium.CircleMarker(coord, tooltip=nombre, radius=8, color='blue', fill=True, fill_color='lightblue').add_to(m)

# 4. Definir las rutas normales (Arcos verdes)
# 4. Definir las rutas verdes con sus datos
rutas_verdes = [
    ('D1 (Haneda)', 'N2 (Funabashi)', 35, 0.85),
    ('D1 (Haneda)', 'N5 (Kawasaki)', 4, 0.78),
    ('D1 (Haneda)', 'N9 (Chiba)', 50, 0.89),
    ('D1 (Haneda)', 'N10 (Tokio)', 20, 0.97),
    ('D2 (Narita)', 'N2 (Funabashi)', 45, 0.99),
    ('D2 (Narita)', 'N9 (Chiba)', 35, 0.80),
    ('D3 (Yokohama)', 'N1 (Fujisawa)', 26, 0.99),
    ('D3 (Yokohama)', 'N5 (Kawasaki)', 20, 0.98),
    ('D3 (Yokohama)', 'N6 (Hachioji)', 50, 0.29),
    ('D4 (Tsuchiura)', 'N2 (Funabashi)', 67, 0.10),
    ('D4 (Tsuchiura)', 'N3 (Kasukabe)', 52, 0.52),
    ('D4 (Tsuchiura)', 'N10 (Tokio)', 70, 0.87)
]

# Dibujar las líneas y aplicar el Plugin de texto
# Dibujar las líneas verdes orientadas correctamente
# Dibujar las líneas verdes
for origen, destino, dist, fiab in rutas_verdes:
    
    coord_o = nodos[origen]
    coord_d = nodos[destino]
    
    # Mantenemos el truco para que no se lean del revés
    if coord_o[1] > coord_d[1]:
        coordenadas_dibujo = [coord_d, coord_o]
    else:
        coordenadas_dibujo = [coord_o, coord_d]
        
    # A. Creamos la línea verde
    linea_verde = folium.PolyLine(
        coordenadas_dibujo, 
        color='green', 
        weight=3, 
        opacity=0.6
    )
    linea_verde.add_to(m)
    
    # B. Texto limpio y CENTRADO AUTOMÁTICAMENTE
    texto_impreso = f"{dist} km ({int(fiab*100)}%)" # Ya no hay variables de "espacios"
    
    plugins.PolyLineTextPath(
        linea_verde,
        texto_impreso,
        repeat=False,
        center=True,  # <--- MAGIA: Centra el texto en la línea
        offset=16,
        attributes={'fill': 'darkgreen', 'font-weight': 'bold', 'font-size': '12'}
    ).add_to(m)
# 5. DIBUJAR LA RUTA AÑADIDA (Amarillo brillante)
# Ejemplo con tu ruta amarilla:
# La ruta sigue invertida para que se lea bien
ruta_amarilla = [nodos['N4 (Kawagoe)'], nodos['D3 (Yokohama)']]
linea_amarilla = folium.PolyLine(ruta_amarilla, color='#FFD700', weight=6)
linea_amarilla.add_to(m)

plugins.PolyLineTextPath(
    linea_amarilla,
    "45 km (75%)",    # <--- ADIÓS A LOS ESPACIOS
    repeat=False,
    center=True,      # <--- EL NUEVO TRUCO: Lo centra matemáticamente
    offset=18,
    attributes={'fill': 'black', 'font-weight': 'bold', 'font-size': '18'}
).add_to(m)
# 6. Guardar el resultado en un archivo interactivo
m.save("mapa_logistico_real4.html")
print("¡Éxito! Busca el archivo 'mapa_logistico_real4.html' en tu carpeta y hazle doble clic para abrirlo.")