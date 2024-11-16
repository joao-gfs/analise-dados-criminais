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
DISTANCIA_OCORRENCIAS = 200

# quantidade de ocorrencias para teste
Q_OCC = 5000

print('Lendo csv')
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

print('Criando grafo')
# inicializa o grafo com o número total de vértices (criar o grafo diretamente das arestas pode causar erros, principalmente desconsiderar vértices sem arestas.)
g = ig.Graph(n=len(coord_ocorrencias))

#dados das ocorrencias que serão levados em conta na formação das arestas
g.vs['latitude'] = latitudes
g.vs['longitude'] = longitudes
g.vs['horario'] = [fa.militar_para_timedelta(x) for x in df['TIME OCC']] # transformar horarios em timedelta (facilita cálculos)
g.vs['cat_crime'] = [fa.obter_cat_crime(codigo) for codigo in df['Crm Cd']]
g.vs['mocodes'] = [str(x).split() for x in df['Mocodes']]
g.vs['cat_arma'] = [fa.obter_cat_arma(codigo) for codigo in df['Weapon Used Cd']]
g.vs['crm_cods'] = df.apply(fa.obter_categorias_secundarias, axis=1)
g.vs['perfil_vitima'] = df.apply(lambda row: fa.gerar_perfil(row['Vict Age'], row['Vict Sex'], row['Vict Descent']), axis=1).tolist()

# dados que serão usados nas análises de dados das comunidades
g.vs['cod_area'] = np.array(df['AREA'])
g.vs['area'] = np.array(df['AREA NAME'])
g.vs['cod_subarea'] = np.array(df['Rpt Dist No'])

print('Criando arestas')
# para todas as ocorrências, encontrar os vizinhos na distância do raio escolhisdos
for i, coord in enumerate(coords_rad):
    if i % 200 == 0:
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
            peso_crm_cds = 0 # ok

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

            '''if peso_crm_cds > 0:
                print(vi['crm_cods'], vj['crm_cods'], peso_crm_cds)'''

            peso_final = peso_distancia * 0.25 + peso_horario * 0.1 + peso_crime * 0.25 + peso_mocodes * 0.1 + peso_vitima * 0.1 + peso_arma * 0.15 + peso_crm_cds * 0.05

            '''print(f'D: {peso_distancia} - H: {peso_horario}')
            print(f'C: {peso_crime} - M: {peso_mocodes}')
            print(f'V: {peso_vitima} - A: {peso_arma}')
            print(f'S: {peso_crm_cds}')
            print(f'Peso final: {peso_final}')
            print()'''

            # adiciona as arestas e pesos, além dos outros atributos
            g.add_edge(i, j, weight=peso_final)
print(i)

# converter dados de volta para strings
g.vs['horario'] = [str(horario) for horario in g.vs['horario']]
g.vs['mocodes'] = [",".join(mocodes) if mocodes else "" for mocodes in g.vs['mocodes']]

print('Detectando comunidades')
# aplica o algoritmo de Louvain para identificar as comunidades
communities = g.community_multilevel(weights=g.es['weight'], resolution=0.9)

g.vs['comunidade'] = communities.membership

print('Salvando as comunidades')
# exibir as comunidades
comunidades_dados = []
for i, community in enumerate(communities):
    subgrafo = g.induced_subgraph(community)
    infos = fa.extrair_informacoes_comunidade(i, subgrafo)
    comunidades_dados.append(infos)

df_comunidades = pd.DataFrame(comunidades_dados)
df_comunidades.to_csv('dados/comunidades.csv', index=False)

print("Dados exportados para 'comunidades.csv'")

g.write_graphml(f"grafos_modelados/grafo_{DISTANCIA_OCORRENCIAS}m_{Q_OCC}_occ_90_res.graphml")