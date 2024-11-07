import funcoes_auxiliares as fa
import igraph as ig
import pandas as pd
import numpy as np
from math import exp
from sklearn.neighbors import BallTree
from geopy.distance import geodesic
import matplotlib.pyplot as plt

# valor de ajuste para calculo não linear da distancia temporal
ALPHA_TEMPO = 0.15
# Distancia máxima para conexão de ocorrencias (vertices)
DISTANCIA_OCORRENCIAS = 1000

# carrega os dados do dataset já filtrado
df = pd.read_csv('dataset-filtrado.csv')
df = df.head(5000) # grafo menor para testes, remover na aplicação real

# extração dos atributos uteis
latitudes = np.array(df['LAT'])
longitudes = np.array(df['LON'])
horarios = [fa.militar_para_timedelta(x) for x in df['TIME OCC']] # transformar horarios em timedelta (facilita cálculos)

# junta os grafos
dados_ocorrencias = np.column_stack((latitudes, longitudes))

# converte latitudes e longitudes para radianos para usar na BallTree
coords_rad = np.radians(dados_ocorrencias)

# BallTree é uma estrutura de dados que permite fazer busca eficiente com base na distância entre os nós.
# ela atende bem nosso uso pois temos uma distância máxima como critério de criação de arestas
ball_tree = BallTree(coords_rad, metric='haversine')

# define o raio de distância máxima para criar arestas num vértice (em radianos)
raio_radianos = DISTANCIA_OCORRENCIAS / 6371000

# listas para as arestas e pesos 
arestas = []
pesos = []

# para todas as ocorrências, encontrar os vizinhos na distância do raio escolhisdos
for i, coord in enumerate(coords_rad):
    if i % 1000 == 0:
        print(i)

    indices = ball_tree.query_radius([coord], r=raio_radianos)[0]
    for j in indices:
        if i < j:  # evita duplicação de arestas
            peso_final = 0
            peso_dist = 0
            peso_time = 0
            peso_crime = 0
            peso_mocodes = 0
            peso_vitima = 0
            peso_arma = 0
            peso_crm_cds = 0
   
            dist_metros = geodesic(dados_ocorrencias[i], dados_ocorrencias[j]).meters
            peso_dist = 1 - (dist_metros / DISTANCIA_OCORRENCIAS)

            diferenca_horario = fa.diferenca_horario(horarios[i], horarios[j])
            print(horarios[i], horarios[j])
            print(diferenca_horario)
            # Calcula o peso do horário com uma função exponencial
            peso_time = exp(-ALPHA_TEMPO * (diferenca_horario.total_seconds() / 3600))
            print(f'D = {peso_dist} - T = {peso_time}')

            peso_final = peso_dist * 0.3 + peso_time * 0.1 + peso_crime * 0.2 * peso_vitima * 0.1 + peso_arma * 0.15 + peso_crm_cds * 0.05
            arestas.append((i, j))
            pesos.append(peso_final)

# inicializa o grafo com o número total de vértices (criar diretamente das arestas pode causar erros, principalmente de ignorar vértices sem arestas.)
g = ig.Graph(n=len(dados_ocorrencias))

# adiciona as arestas e pesos, além dos outros atributos
g.add_edges(arestas)
g.es['weight'] = pesos

g.vs['latitude'] = latitudes
g.vs['longitude'] = longitudes
g.vs['horario'] = horarios

# aplica o algoritmo de Louvain para identificar as comunidades
communities = g.community_multilevel(weights=g.es['weight'])

# exibir as comunidades
for i, community in enumerate(communities):
    print(f"Comunidade {i}: {community}")

g.write_graphml("grafo_comunidades.graphml")