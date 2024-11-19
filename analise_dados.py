# Este arquivo é dedicado às funções de analise das comunidades já identificadas no main.py
# O objetivo é gerar um relatório complementar à visualização do grafo modelado

import pandas as pd
import ast

def descrever_comunidades(areas_prioritarias, areas_atencao, pontos_focais):
    
    # Imprimir os dataframes com títulos
    if areas_prioritarias is not None:
        imprimir_dataframe("Áreas Prioritárias", areas_prioritarias)
    if areas_atencao is not None:
        imprimir_dataframe("Áreas de Atenção", areas_atencao)
    if pontos_focais is not None:
        imprimir_dataframe("Pontos Focais", pontos_focais)

def imprimir_dataframe(titulo, dataframe):
    print(f"\n{'=' * 50}")
    print(f"{titulo.upper()}")
    print(f"{'=' * 50}\n")
    for index, row in dataframe.iterrows():

        areas_ordenadas = sorted(row['Areas']) if isinstance(row['Areas'], set) else row['Areas']
        subareas_ordenadas = sorted(row['Subareas']) if isinstance(row['Subareas'], set) else row['Subareas']
        
        print(f"Ponto no mapa: {row['Comunidade']}")
        print(f"Localização Central: {row['Lat']:.6f}, {row['Lon']:.6f}")
        print(f"Áreas: {', '.join(map(str, areas_ordenadas))}")
        print(f"Subáreas: {', '.join(map(str, subareas_ordenadas))}")

        # Verificar e ordenar porcentagens
        porcentagem_crimes = row['Porcentagem Crimes'] if isinstance(row['Porcentagem Crimes'], dict) else ast.literal_eval(row['Porcentagem Crimes'])
        porcentagem_armas = row['Porcentagem Armas'] if isinstance(row['Porcentagem Armas'], dict) else ast.literal_eval(row['Porcentagem Armas'])
        porcentagem_horarios = row['Porcentagem Horarios'] if isinstance(row['Porcentagem Horarios'], dict) else ast.literal_eval(row['Porcentagem Horarios'])
        
        print("\nCrimes:")
        for crime, pct in sorted(porcentagem_crimes.items(), key=lambda x: x[1], reverse=True):
            print(f"  {crime}: {pct * 100:.2f}%")
        
        print("\nArmas Usadas:")
        for arma, pct in sorted(porcentagem_armas.items(), key=lambda x: x[1], reverse=True):
            if  arma == 'Indefinido':
                continue
            print(f"  {arma}: {pct * 100:.2f}%")
        
        print("\nPeríodos do Dia:")
        for horario, pct in sorted(porcentagem_horarios.items(), key=lambda x: x[1], reverse=True):
            print(f"  {horario}: {pct * 100:.2f}%")
        
        print("\n" + "-" * 50 + "\n")