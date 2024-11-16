from datetime import timedelta
import pandas as pd
from scipy.spatial.distance import pdist
import numpy as np

categorias_crime = {
    "homicidio": [110, 113],
    "crime sexual": [121, 122, 815, 820, 821, 812, 813, 822, 845, 850, 860, 760, 762],
    "roubo": [210, 220, 310, 320, 510, 520, 433, 330, 331, 410, 420, 421, 350, 351, 352, 353, 450, 451, 452, 453, 341, 343, 345, 440, 441, 442, 443, 444, 445, 470, 471, 472, 473, 474, 475, 480, 485, 487, 491, 522, 349, 446],
    "agressao grave": [230, 231, 235, 236, 250, 251, 761, 926],
    "agressao leve": [435, 436, 437, 622, 623, 624, 625, 626, 627, 647, 763, 928, 930],
    "vandalismo": [648, 924, 740, 745, 753, 886, 888, 755, 884, 756],
    "sequestro": [910, 920, 922],
    "golpes": [940, 662, 664, 666]
}

def obter_cat_crime(codigo_crime):
    for categoria, codigos in categorias_crime.items():
        if codigo_crime in codigos:
            return categoria
    return "Indefinido"

def comparar_categorias(cat1, cat2):
    peso = 0
    if 'agressao' in cat1 and 'agressao' in cat2:
        peso = 0.5
    if cat1 == cat2:
        peso = 1
    if (cat1 == 'agressao grave' and cat2 == 'homicidio') or (cat1 == 'homicidio' and cat2 == 'agressao grave'):
        peso = 0.75

    return peso

# transformar o horario militar do dataset para timedelta, para facilitar calculo da diferença de horario
def militar_para_timedelta(horario):
    
    # garantir que horario é string e preencher com 0 para ter 4 casas
    horario = str(horario).zfill(4)
    
    if not horario.isdigit() or len(horario) != 4:
        return None  # Retorna None para valores inválidos
    
    horas = int(horario[:2])
    minutos = int(horario[2:])
    return timedelta(hours=horas, minutes=minutos)

from datetime import timedelta

# caso entre os horarios exista a passagem de um dia (tem uma meia noite no meio), a função calcula o valor passando pela meia noite:
# Por exemplo 19:00 e 4:00, de forma direta dá 15:00:00, mas passando pela meia noite resulta em 9:00:00
def diferenca_horario(horario1, horario2):
    diferenca_direta = abs(horario1 - horario2)
    
    diferenca_via_meia_noite = timedelta(days=1) - diferenca_direta
    
    return min(diferenca_direta, diferenca_via_meia_noite)

def gerar_perfil(idade, sexo, descendencia):
    if idade == 0:
        idade = None
    if pd.isna(sexo):
        sexo = None
    if pd.isna(descendencia):
        descendencia = None
    perfil = {
        'idade': idade,
        'sexo': sexo,
        'descendencia': descendencia
    }
    return perfil

# retorna peso de comparacao entre os perfis de vitima
def comparar_vitimas(vitima1, vitima2):
    peso_idade = 0
    peso_sexo = 0
    peso_descendencia = 0

    if vitima1['idade'] == None or vitima2['idade'] == None:
        peso_idade = 0.5
    else:
        peso_idade = 1 - (abs(vitima1['idade'] - vitima2['idade']) / 100)

    if vitima1['sexo'] == None or vitima2['sexo'] == None:
        peso_sexo = 0.5
    elif vitima1['sexo'].strip() == vitima2['sexo'].strip():
        peso_sexo = 1
    
    if vitima1['descendencia'] == None or vitima2['descendencia'] == None:
        peso_descendencia = 0.5
    elif vitima1['descendencia'].strip() == vitima2['descendencia'].strip():
        peso_descendencia = 1

    peso_perfil = peso_idade * 0.40 + peso_sexo * 0.30 + peso_descendencia * 0.30

    return peso_perfil

def comparar_mocodes(mocodes1, mocodes2):

    if '1501' in mocodes1:
        mocodes1.remove('1501')
    if '1501' in mocodes2:
        mocodes2.remove('1501')

    set1 = set(mocodes1)
    set2 = set(mocodes2)

    mocodes_em_comum = set1.intersection(set2)

    total_mocodes = set1.union(set2)

    if not total_mocodes:
        return 0

    peso_mocodes = len(mocodes_em_comum) / len(total_mocodes)

    return peso_mocodes

armas_categorias = {
    "armas de fogo automaticas": [108.0, 114.0, 115.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0],
    "armas de fogo semiautomaticas": [109.0, 110.0, 111.0, 113.0, 116.0, 124.0, 125.0],
    "armas de fogo": [101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0],
    "objetos cortantes": [200.0, 201.0, 202.0, 203.0, 204.0, 205.0, 206.0, 207.0, 208.0, 209.0, 210.0, 212.0, 213.0, 214.0, 215.0, 216.0, 217.0, 218.0, 219.0, 220.0, 221.0, 223.0],
    "objetos contundentes": [211.0, 301.0, 300.0, 302.0, 303.0, 304.0, 305.0, 306.0, 308.0, 310.0, 312.0, 509.0, 514.0],
    "explosivos e substancias quimicas": [501.0, 502.0, 503.0, 504.0, 505.0, 506.0, 507.0, 510.0, 512.0],
    "força fisica e ameacas": [400.0, 513.0, 515.0],
    "outros": [307.0, 500.0, 508.0, 511.0, 516.0]
}

def obter_cat_arma(codigo_arma):
    for categoria, codigos in armas_categorias.items():
        if codigo_arma in codigos:
            return categoria
    return 'Indefinido'

def comparar_tipos_arma(tipo1, tipo2):
    peso = 0
    if tipo1 == tipo2 and (tipo1 !=  'Indefinido' or tipo2 !=  'Indefinido') :
        peso = 1
    #automaticas e semiautomaticas
    elif (tipo1 == "armas de fogo automaticas" and tipo2 == "armas de fogo semiautomaticas") or (tipo1 == "armas de fogo semiautomaticas" and tipo2 == "armas de fogo automaticas"):
        peso = 0.75
    #arma de fogo e outras subcategorias de armas de fogo
    elif ('armas' in tipo1 and 'armas' in tipo2):
        peso = 0.5
    #armas cortantes ou contundentes
    elif ('objetos' in tipo1 and 'objetos' in tipo2):
        peso = 0.5
    #arma de fogo e objetos cortantes ou contundentes
    elif ('armas' in tipo1 and 'objetos' in tipo2) or ('armas' in tipo2 and 'objetos' in tipo1):
        peso = 0.25

    return peso

def comparar_crimes_secundarios(crimes1, crimes2):
    set1 = set(crimes1)
    set2 = set(crimes2)

    crimes_em_comum = set1.intersection(set2)
    todos_crimes = set1.union(set2)

    if not todos_crimes:
        return 0
    
    peso_crimes = len(crimes_em_comum) / len(todos_crimes)

    return peso_crimes

def obter_categorias_secundarias(codigos):

    codigos = [codigos['Crm Cd 2'], codigos['Crm Cd 3'], codigos['Crm Cd 4']]
    codigos = [codigo for codigo in codigos if pd.notna(codigo)]
    
    categorias = []
    for codigo in codigos:
        for categoria, lista_codigos in categorias_crime.items():
            if codigo in lista_codigos:
                categorias.append(categoria)
                break

    return list(set(categorias))

def extrair_informacoes_comunidade(n, subgrafo_comunidade):
    
    n_vertices = len(subgrafo_comunidade.vs)
    n_arestas = len(subgrafo_comunidade.es)
    coordenadas = [(v['latitude'], v['longitude']) for v in subgrafo_comunidade.vs]

    soma_pesos = sum(subgrafo_comunidade.es['weight'])

    densidade = 0
    if n_vertices > 1:
        densidade = 2 * soma_pesos / (n_vertices * (n_vertices - 1))

    pontos = np.array(coordenadas)
    distancia_media = np.mean(pdist(pontos)) if len(pontos) > 1 else 0
    densidade_espacial = 1 / (distancia_media * 111) if distancia_media > 0 else 0# 111 pois o pdist devolve em graus de latitude que equivalem a 111 aproximadamente

    crimes_comunidade = {}
    armas_comunidade = {}
    horarios_comunidade = {'Manha': 0, 'Tarde': 0, 'Noite': 0, 'Madrugada': 0}
    areas = set()
    subareas = set()

    for v in subgrafo_comunidade.vs:
        categoria = v['cat_crime']
        arma = v['cat_arma']

        areas.add(v['area'])
        subareas.add(int(v['cod_subarea']))
        
        # Atualiza a contagem de categorias de crime
        if categoria in crimes_comunidade:
            crimes_comunidade[categoria] += 1
        else:
            crimes_comunidade[categoria] = 1

        # Atualiza a contagem de tipo de arma
        if arma in armas_comunidade:
            armas_comunidade[arma] += 1
        else:
            armas_comunidade[arma] = 1

        
        hora = int(v['horario'].total_seconds() // 3600) % 24  # Extrai a hora de timedelta
        if 6 <= hora < 12:  
            horarios_comunidade['Manha'] += 1
        elif 12 <= hora < 18:  
            horarios_comunidade['Tarde'] += 1
        elif 18 <= hora < 24:  
            horarios_comunidade['Noite'] += 1
        else: 
            horarios_comunidade['Madrugada'] += 1

    # Calcula a média das coordenadas
    centro_lat = sum(subgrafo_comunidade.vs['latitude']) / n_vertices
    centro_lon = sum(subgrafo_comunidade.vs['longitude']) / n_vertices

    # Calcula a porcentagem de cada categoria
    total_crimes = n_vertices
    porcentagens_crimes = {categoria: round((count / total_crimes), 3) for categoria, count in crimes_comunidade.items()}
    porcentagens_armas = {arma: round((count /total_crimes), 3) for arma, count in armas_comunidade.items()}
    porcentagens_horarios = {periodo: round((count / total_crimes), 3) for periodo, count in horarios_comunidade.items()}

    # Exibe os resultados com porcentagens
    comunidade_dados = {
            'Comunidade': n,
            'Tamanho': n_vertices,
            'Densidade': densidade,
            'Densidade Espacial': densidade_espacial,
            'Fator escolha': n_vertices * densidade * densidade_espacial,
            'Lat': centro_lat,
            'Lon': centro_lon,
            'Porcentagem Crimes': porcentagens_crimes,
            'Porcentagem Armas': porcentagens_armas,
            'Porcentagem Horarios': porcentagens_horarios,
            'Areas': areas,
            'Subareas': subareas,
        }
    
    """if comunidade_dados['Tamanho'] > 20:
        print(f'Comunidade {comunidade_dados["Comunidade"]}:')
        print(f'\tTamanho: {comunidade_dados["Tamanho"]} - D: {comunidade_dados["Densidade"]} - DE: {comunidade_dados["Densidade Espacial"]}')
        print(f'\t{comunidade_dados["Areas"]}')
        print(f'\t{comunidade_dados["Subareas"]}')
        print(f'\t{comunidade_dados["Porcentagem Crimes"]}')
        print(f'\t{comunidade_dados["Porcentagem Armas"]}')
        print(f'\t{comunidade_dados["Porcentagem Horarios"]}')
        print()"""
    
    return comunidade_dados