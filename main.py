import funcoes_auxiliares as fa
import igraph as ig
import pandas as pd
import numpy as np
from math import exp
from sklearn.neighbors import BallTree
from geopy.distance import geodesic

# valor de ajuste para calculo não linear da distancia temporal
ALPHA_TEMPO = 0.15
# Distancia máxima para conexão de ocorrencias (vertices)
DISTANCIA_OCORRENCIAS = 250

# quantidade de ocorrencias para teste
Q_OCC = 50000

# carrega os dados do dataset já filtrado
df = pd.read_csv('dados/dataset-filtrado.csv')
df = df.head(Q_OCC) # grafo menor para testes, remover na aplicação real

latitudes = np.array(df['LAT'])
longitudes = np.array(df['LON'])

#junta os dados em tuplas
coord_ocorrencias = np.column_stack((latitudes, longitudes))

# converte latitudes e longitudes para radianos para usar na BallTree
coords_rad = np.radians(coord_ocorrencias)

# BallTree é uma estrutura de dados que permite fazer busca eficiente com base na distância entre os nós.
# ela atende bem nosso uso pois temos uma distância máxima como critério de criação de arestas
ball_tree = BallTree(coords_rad, metric='haversine')

# define o raio de distância máxima para criar arestas num vértice (em radianos)
raio_radianos = DISTANCIA_OCORRENCIAS / 6371000

# inicializa o grafo com o número total de vértices (criar diretamente das arestas pode causar erros, principalmente de ignorar vértices sem arestas.)
g = ig.Graph(n=len(coord_ocorrencias))
g.vs['latitude'] = latitudes
g.vs['longitude'] = longitudes
g.vs['horario'] = [fa.militar_para_timedelta(x) for x in df['TIME OCC']] # transformar horarios em timedelta (facilita cálculos)
g.vs['cat_crime'] = [fa.obter_cat_crime(codigo) for codigo in df['Crm Cd']]
g.vs['mocodes'] = [str(x).split() for x in df['Mocodes']]
g.vs['cat_arma'] = [fa.obter_cat_arma(codigo) for codigo in df['Weapon Used Cd']]
g.vs['crm_cods'] = df.apply(fa.obter_categorias_secundarias, axis=1)
g.vs['perfil_vitima'] = df.apply(lambda row: fa.gerar_perfil(row['Vict Age'], row['Vict Sex'], row['Vict Descent']), axis=1).tolist()

# listas para as arestas e pesos 
arestas = []
pesos = []

# para todas as ocorrências, encontrar os vizinhos na distância do raio escolhisdos
for i, coord in enumerate(coords_rad):
    if i % 1000 == 0:
        print(i)

    vi = g.vs[i]

    indices = ball_tree.query_radius([coord], r=raio_radianos)[0]
    for j in indices:
        if i < j:  # evita duplicação de arestas
            peso_final = 0
            peso_distancia = 0 # ok
            peso_horario = 0 # ok
            peso_crime = 0 # ok
            peso_mocodes = 0 # ok
            peso_vitima = 0 # ok
            peso_arma = 0 # ok
            peso_crm_cds = 0

            vj = g.vs[j]

            dist_metros = geodesic((vi['latitude'], vi['longitude']), (vj['latitude'], vj['longitude'])).meters
            peso_distancia = 1 - (dist_metros / DISTANCIA_OCORRENCIAS)

            diferenca_horario = fa.diferenca_horario(vi['horario'], vj['horario'])

            # calcula o peso do horário com uma função exponencial, que é não linear
            # o calculo não linear faz com que horarios mais próximos gerem proporcionalmente mais peso
            peso_horario = exp(-ALPHA_TEMPO * (diferenca_horario.total_seconds() / 3600))
 
            peso_vitima = fa.comparar_vitimas(vi['perfil_vitima'], vj['perfil_vitima'])

            peso_crime = fa.comparar_categorias(vi['cat_crime'], vj['cat_crime'])

            peso_mocodes = fa.comparar_mocodes(vi['mocodes'], vj['mocodes'])
            
            peso_arma = fa.comparar_tipos_arma(vi['cat_arma'], vj['cat_arma'])

            peso_crm_cds = fa.comparar_crimes_secundarios(vi['crm_cods'], vj['crm_cods'])

            if peso_crm_cds > 0:
                print(vi['crm_cods'], vj['crm_cods'], peso_crm_cds)

            peso_final = peso_distancia * 0.3 + peso_horario * 0.1 + peso_crime * 0.2 + peso_mocodes * 0.1 + peso_vitima * 0.1 + peso_arma * 0.15 + peso_crm_cds * 0.05
            arestas.append((i, j))
            pesos.append(peso_final)

# converter dados de volta para strings
g.vs['horario'] = [str(horario) for horario in g.vs['horario']]
g.vs['mocodes'] = [",".join(mocodes) if mocodes else "" for mocodes in g.vs['mocodes']]

# Salvar o grafo em formato GraphML
g.write_graphml(f"grafos_modelados/grafo_{DISTANCIA_OCORRENCIAS}m_{Q_OCC}_ocorrencias.graphml")

# adiciona as arestas e pesos, além dos outros atributos
g.add_edges(arestas)
g.es['weight'] = pesos

# aplica o algoritmo de Louvain para identificar as comunidades
communities = g.community_multilevel(weights=g.es['weight'])

g.vs['comunidade'] = communities.membership
# exibir as comunidades
#for i, community in enumerate(communities):
#    print(f"Comunidade {i}: {community}")

g.write_graphml(f"grafos_modelados/grafo_{DISTANCIA_OCORRENCIAS}m_{Q_OCC}_ocorrencias.graphml")