#!/usr/bin/env python3
"""
Demo script showing how to configure VTOL and Person drawing sizes.

This script demonstrates how the global variables PERSON_DRAW_SIZE and VTOL_DRAW_SIZE
can be modified to customize the appearance of entities in the simulation.
"""

import sys
import os

# Adiciona o diretório de módulos ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Modules'))

# Importa o módulo e modifica os tamanhos antes da simulação
from Modules.Simulation import engine

def demo_custom_sizes():
    """Demonstra como customizar os tamanhos de desenho"""
    
    print("=== Configuração de Tamanhos de Desenho ===")
    print(f"Tamanho padrão de Pessoas: {engine.PERSON_DRAW_SIZE}")
    print(f"Tamanho padrão de VTOLs: {engine.VTOL_DRAW_SIZE}")
    
    # Exemplo 1: Pessoas maiores, VTOLs menores
    print("\n--- Exemplo 1: Pessoas maiores (5), VTOLs menores (6) ---")
    engine.PERSON_DRAW_SIZE = 5
    engine.VTOL_DRAW_SIZE = 6
    print(f"Novo tamanho de Pessoas: {engine.PERSON_DRAW_SIZE}")
    print(f"Novo tamanho de VTOLs: {engine.VTOL_DRAW_SIZE}")
    
    # Exemplo 2: Ambos maiores
    print("\n--- Exemplo 2: Ambos maiores (Pessoas: 7, VTOLs: 12) ---")
    engine.PERSON_DRAW_SIZE = 7
    engine.VTOL_DRAW_SIZE = 12
    print(f"Novo tamanho de Pessoas: {engine.PERSON_DRAW_SIZE}")
    print(f"Novo tamanho de VTOLs: {engine.VTOL_DRAW_SIZE}")
    
    # Exemplo 3: Ambos menores
    print("\n--- Exemplo 3: Ambos menores (Pessoas: 2, VTOLs: 4) ---")
    engine.PERSON_DRAW_SIZE = 2
    engine.VTOL_DRAW_SIZE = 4
    print(f"Novo tamanho de Pessoas: {engine.PERSON_DRAW_SIZE}")
    print(f"Novo tamanho de VTOLs: {engine.VTOL_DRAW_SIZE}")
    
    # Restaura valores padrão
    print("\n--- Restaurando valores padrão ---")
    engine.PERSON_DRAW_SIZE = 3
    engine.VTOL_DRAW_SIZE = 8
    print(f"Tamanho de Pessoas restaurado: {engine.PERSON_DRAW_SIZE}")
    print(f"Tamanho de VTOLs restaurado: {engine.VTOL_DRAW_SIZE}")
    
    print("\n=== Configuração concluída ===")
    print("Para usar essas configurações na simulação:")
    print("1. Modifique as variáveis engine.PERSON_DRAW_SIZE e engine.VTOL_DRAW_SIZE")
    print("2. Execute a simulação normalmente")
    print("3. As entidades serão desenhadas com os novos tamanhos")

if __name__ == "__main__":
    demo_custom_sizes()
