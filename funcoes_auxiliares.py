from datetime import timedelta
import pandas as pd
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