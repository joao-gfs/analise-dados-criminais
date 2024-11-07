import igraph as ig
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from sklearn.neighbors import BallTree
from geopy.distance import geodesic
import matplotlib.pyplot as plt

DISTANCIA_OCORRENCIAS = 1000

# Carrega os dados das coordenadas
df = pd.read_csv('grafo-filtrado.csv')
df = df.head(5000)

latitudes = np.array(df['LAT'])
longitudes = np.array(df['LON'])
horarios = np.array(df['TIME OCC'])

dados_ocorrencias = np.column_stack((latitudes, longitudes))

# Converte latitudes e longitudes para radianos para usar na BallTree
coords_rad = np.radians(dados_ocorrencias)

# Cria uma BallTree para consultas rápidas de vizinhos em coordenadas geográficas
tree = BallTree(coords_rad, metric='haversine')

# Define o raio de 500 metros em radianos (500m / Raio da Terra em metros)
raio = DISTANCIA_OCORRENCIAS / 6371000  # Corrigido para 500 metros

# Inicializa listas para as arestas e pesos (necessárias para igraph)
arestas = []
pesos = []

# Para cada ocorrência, encontre os vizinhos dentro de 500 metros
for i, coord in enumerate(coords_rad):
    if i % 1000 == 0:
        print(i)

    indices = tree.query_radius([coord], r=raio)[0]
    for j in indices:
        if i < j:  # Evita duplicação de arestas em grafos não direcionados
            peso = 0
            peso_dist = 0
            peso_time = 0
            peso_crime = 0
            peso_vitima = 0
            peso_arma = 0
            peso_crm_cds = 0
   
            dist_metros = geodesic(dados_ocorrencias[i], dados_ocorrencias[j]).meters
            peso_dist = 1 - (dist_metros / DISTANCIA_OCORRENCIAS)

            diferenca_horario = abs(horarios[i] - horarios[j])
            peso_time = 1 - ((diferenca_horario.total_seconds() / 3600) / 24)

            

            peso = peso_dist * 0.3 + peso_time * 0.1 + peso_crime * 0.2 * peso_vitima * 0.1 + peso_arma * 0.15 + peso_crm_cds * 0.05
            arestas.append((i, j))
            pesos.append(peso)

# Inicializa o grafo com o número total de vértices
g = ig.Graph(n=len(dados_ocorrencias))

# Adiciona as arestas com os pesos
g.add_edges(arestas)
g.es['weight'] = pesos

g.vs['latitude'] = latitudes
g.vs['longitude'] = longitudes

# Aplicar o algoritmo de Louvain
communities = g.community_multilevel(weights=g.es['weight'])

# Exibir as comunidades
for i, community in enumerate(communities):
    print(f"Comunidade {i}: {community}")

g.write_graphml("grafo_gephi.graphml")

# Define layout personalizado usando as coordenadas originais em graus
layout_custom = [tuple(coord) for coord in dados_ocorrencias]
# Configuração do estilo de visualização
visual_style = {
    "layout": layout_custom,               # Usa o layout personalizado
    "vertex_size": 5,
    "vertex_label": list(range(len(dados_ocorrencias))),  # Usa índices como rótulo dos vértices
    "edge_width": [max(1, w / 50) for w in pesos],  # Ajusta a largura das arestas
    "bbox": (600, 600),
    "margin": 40
}

# Visualiza o grafo e salva a imagem
plot = ig.plot(g, **visual_style)
plot.save("grafo.png")

# Exibe a imagem usando matplotlib
img = plt.imread("grafo.png")
#plt.imshow(img)
#plt.axis('off')
#plt.show()

def militar_para_timedelta(horario):
    # Converte o horário para string, para garantir que tenhamos 4 caracteres
    horas = int(horario[:2])
    minutos = int(horario[2:])
    # Converte para timedelta
    return timedelta(hours=horas, minutes=minutos)