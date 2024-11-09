import igraph as ig

# Carregar o grafo a partir de um arquivo .graphml
grafo = ig.Graph.Read_GraphMLz('grafos_modelados/grafo_50k.graphml.gz')

# Aplicar o algoritmo de Louvain para detecção de comunidades
comunidades = grafo.community_multilevel()

# Exibir as comunidades detectadas
j = 0
for i, comunidade in enumerate(comunidades):
    if len(comunidade) > 100:
        j += 1
        print(f"Comunidade {i}: {comunidade}")

print(f'{j} pontos detectados')

# Opcional: Salvar as comunidades como atributo dos vértices para visualização
grafo.vs["comunidade"] = comunidades.membership

# Salvar o grafo atualizado com as comunidades de volta em um novo arquivo .graphml
grafo.write_graphml("grafos_modelados/grafo_com_comunidades.graphml")
