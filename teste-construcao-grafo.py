import igraph as ig
import numpy as np
from sklearn.neighbors import BallTree
from geopy.distance import geodesic
import matplotlib.pyplot as plt

# Exemplo de coordenadas e atributos das ocorrências
dados_ocorrencias = np.array([
    [33.71249000148497, -118.66288282473724],
    [33.71249000148466, -118.66288282473800],
    [34.32850437252595, -118.2435964279404],
    [34.546464654464, -118.243546312135]
])

codigos_ocorrencia = ["C001", "C002", "C003", "C004"]  # Códigos de ocorrência
areas = ["Area1", "Area1", "Area2", "Area3"]            # Área correspondente a cada ocorrência
subareas = ["Sub1", "Sub2", "Sub1", "Sub3"]             # Subárea correspondente a cada ocorrência

# Converte latitudes e longitudes para radianos para usar na BallTree
coords_rad = np.radians(dados_ocorrencias)

# Cria uma BallTree para consultas rápidas de vizinhos em coordenadas geográficas
tree = BallTree(coords_rad, metric='haversine')

# Define o raio de 500 metros em radianos (500m / Raio da Terra em metros)
raio = 500 / 6371000  # Corrigido para 500 metros

# Inicializa listas para as arestas e pesos (necessárias para igraph)
arestas = []
pesos = []

# Para cada ocorrência, encontre os vizinhos dentro de 500 metros
for i, coord in enumerate(coords_rad):
    # Encontre índices de vizinhos dentro do raio (exclui o próprio ponto)
    indices = tree.query_radius([coord], r=raio)[0]
    for j in indices:
        if i < j:  # Evita duplicação de arestas em grafos não direcionados
            # Calcula a distância exata em metros entre os pontos (opcional)
            dist_metros = geodesic(dados_ocorrencias[i], dados_ocorrencias[j]).meters
            arestas.append((i, j))
            pesos.append(dist_metros)

# Inicializa o grafo com o número total de vértices
g = ig.Graph(n=len(dados_ocorrencias))

# Adiciona as arestas com os pesos
g.add_edges(arestas)
g.es['weight'] = pesos

# Adiciona os atributos aos nós
g.vs["codigo_ocorrencia"] = codigos_ocorrencia
g.vs["area"] = areas
g.vs["subarea"] = subareas

# Ajustes no layout e no estilo visual
layout = g.layout("kk")  # Usa um layout alternativo (Kamada-Kawai)

# Configuração do estilo de visualização
visual_style = {
    "layout": layout,
    "vertex_size": 40,
    "vertex_label": g.vs["codigo_ocorrencia"],  # Usa o código de ocorrência como rótulo
    "edge_width": [max(1, w / 500) for w in pesos],  # Ajusta a largura das arestas para evitar excessos
    "bbox": (600, 600),
    "margin": 40
}

# Visualiza o grafo e salva a imagem
plot = ig.plot(g, **visual_style)
plot.save("grafo.png")

# Exibe a imagem usando matplotlib
img = plt.imread("grafo.png")
plt.imshow(img)
plt.axis('off')
plt.show()
