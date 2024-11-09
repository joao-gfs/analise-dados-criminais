from datetime import timedelta
import pandas as pd

categorias_crime = {
    "homicidio": [110, 113],
    "crime sexual": [121, 122, 815, 820, 821, 812, 813, 822, 845, 850, 860, 760, 762],
    "roubo": [210, 220, 310, 320, 510, 520, 433, 330, 331, 410, 420, 421, 350, 351, 352, 353, 
              450, 451, 452, 453, 341, 343, 345, 440, 441, 442, 443, 444, 445, 470, 471, 472, 
              473, 474, 475, 480, 485, 487, 491, 522, 349, 446],
    "agressao grave": [230, 231, 235, 236, 250, 251, 761, 926],
    "agressao leve": [435, 436, 437, 622, 623, 624, 625, 626, 627, 647, 763, 928, 930],
    "vandalismo": [648, 924, 740, 745, 753, 886, 888, 755, 884, 756],
    "sequestro": [910, 920, 922],
    "golpes": [940, 662, 664, 666]
}

def obter_categoria(codigo_crime):
    for categoria, codigos in categorias_crime.items():
        if codigo_crime in codigos:
            return categoria
    return "Indefinido"

def comparar_categorias(cat1, cat2):
    peso = 0
    if 'agressao' in cat1 and 'agressao' in cat2:
        peso = 0.75
    if cat1 == cat2:
        peso = 1
    if (cat1 == 'agressao grave' and cat2 == 'homicidio') or (cat1 == 'homicidio' and cat2 == 'agressao grave'):
        peso == 0.25

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

