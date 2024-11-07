from datetime import timedelta

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
