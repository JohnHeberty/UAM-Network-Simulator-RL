#!/usr/bin/env python3
"""
Test script para verificar funcionalidade de capacidade de vertiportos.
Este script testa se VTOLs ficam pairando quando a capacidade do vertiport está lotada.
"""

import sys
import os

# Adiciona o diretório de módulos ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Modules'))

from Modules.Simulation.engine import Vertiport, VTOL, Network

def test_vertiport_capacity():
    """Testa a funcionalidade de capacidade dos vertiportos"""
    
    print("=== Teste de Capacidade dos Vertiportos ===")
    
    # Cria um vertiport com capacidade para 2 VTOLs
    vertiport = Vertiport(100, 100, capacity=2)
    network = Network()
    network.add_node(vertiport)
    
    print(f"Vertiport criado com capacidade: {vertiport.capacity}")
    print(f"Ocupação inicial: {vertiport.get_occupancy_info()}")
    
    # Cria 4 VTOLs
    vtols = []
    for i in range(4):
        vtol = VTOL(200 + i*20, 200, network=network)
        vtol.vtol_id = f"VTOL-{i+1}"
        vtol.destination_vertiport = vertiport
        vtols.append(vtol)
    
    print(f"\nCriados {len(vtols)} VTOLs:")
    for vtol in vtols:
        print(f"  - {vtol.vtol_id} em posição ({vtol.xo}, {vtol.yo})")
    
    # Testa se pode pousar
    print("\n--- Teste de Solicitação de Pouso ---")
    for i, vtol in enumerate(vtols):
        can_land = vertiport.request_landing(vtol)
        print(f"{vtol.vtol_id} solicitou pouso: {'✅ Autorizado' if can_land else '⏸️ Deve pairar'}")
        
        # Se autorizado, efetua o pouso
        if can_land:
            success = vertiport.land_vtol(vtol)
            if success:
                vtol.state = "landed"
                vtol.current_vertiport = vertiport
                print(f"  → {vtol.vtol_id} pousou com sucesso")
        
        print(f"  Ocupação: {vertiport.get_occupancy_info()}")
    
    # Mostra estado final
    print(f"\n--- Estado Final ---")
    occupancy = vertiport.get_occupancy_info()
    print(f"Capacidade total: {occupancy['capacity']}")
    print(f"VTOLs pousados: {occupancy['occupied']}")
    print(f"Vagas disponíveis: {occupancy['available']}")
    print(f"VTOLs pairando: {occupancy['hovering_count']}")
    print(f"Taxa de ocupação: {occupancy['occupancy_rate']:.1%}")
    
    # Lista VTOLs pousados
    print(f"\nVTOLs pousados no vertiport:")
    for vtol in vertiport.occupied_slots:
        print(f"  - {vtol.vtol_id}")
    
    # Lista VTOLs pairando
    print(f"\nVTOLs pairando (esperando vaga):")
    for vtol in vertiport.hovering_queue:
        print(f"  - {vtol.vtol_id}")
    
    # Testa decolagem
    print(f"\n--- Teste de Decolagem ---")
    if vertiport.occupied_slots:
        first_vtol = vertiport.occupied_slots[0]
        print(f"Decolando {first_vtol.vtol_id}...")
        success = vertiport.takeoff_vtol(first_vtol)
        if success:
            first_vtol.state = "taking_off"
            first_vtol.current_vertiport = None
            print(f"  → {first_vtol.vtol_id} decolou com sucesso")
        
        print(f"  Ocupação após decolagem: {vertiport.get_occupancy_info()}")
        
        # Verifica se algum VTOL pairando foi notificado
        if vertiport.hovering_queue:
            next_vtol = vertiport.hovering_queue[0]
            if hasattr(next_vtol, '_can_attempt_landing') and next_vtol._can_attempt_landing:
                print(f"  → {next_vtol.vtol_id} foi notificado para tentar pousar novamente")
    
    print("\n=== Teste Concluído ===")
    return vertiport, vtols

if __name__ == "__main__":
    test_vertiport_capacity()
