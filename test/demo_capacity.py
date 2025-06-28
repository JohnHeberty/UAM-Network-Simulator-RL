#!/usr/bin/env python3
"""
Demonstração visual da funcionalidade de capacidade dos vertiportos.
Este script simula VTOLs chegando a um vertiport com capacidade limitada.
"""

import sys
import os
import time

# Adiciona o diretório src ao PATH para importar módulos
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from Modules.Simulation.engine import Vertiport, VTOL, Network

def simulate_capacity_scenario():
    """Simula cenário onde múltiplos VTOLs tentam usar um vertiport com capacidade limitada"""
    
    print("=== Simulação de Capacidade de Vertiport ===")
    
    # Cria vertiport com capacidade para apenas 1 VTOL
    vertiport = Vertiport(500, 400, capacity=1)
    network = Network()
    network.add_node(vertiport)
    
    print(f"🏢 Vertiport criado na posição (500, 400) com capacidade: {vertiport.capacity}")
    
    # Cria 3 VTOLs que vão tentar usar o mesmo vertiport
    vtols = []
    positions = [(300, 300), (700, 300), (500, 200)]
    
    for i, (x, y) in enumerate(positions):
        vtol = VTOL(x, y, network=network)
        vtol.vtol_id = f"ALPHA-{i+1}"
        vtol.destination_vertiport = vertiport
        vtol.is_circulating = False  # Para que pare no vertiport
        vtols.append(vtol)
        print(f"🚁 {vtol.vtol_id} criado na posição ({x}, {y})")
    
    # Simula chegadas sequenciais
    print(f"\n--- Simulação de Chegadas ---")
    
    # VTOL 1 chega primeiro
    print(f"\n⏰ T=0: {vtols[0].vtol_id} tenta pousar...")
    vtols[0]._start_landing()
    if vtols[0].state == "landing":
        # Simula conclusão do pouso
        if vertiport.land_vtol(vtols[0]):
            vtols[0].state = "landed"
            vtols[0].current_vertiport = vertiport
            print(f"  ✅ {vtols[0].vtol_id} pousou com sucesso")
        else:
            vtols[0]._start_hovering()
            print(f"  ⏸️ {vtols[0].vtol_id} deve pairar")
    
    print(f"  📊 Ocupação: {vertiport.get_occupancy_info()}")
    
    # VTOL 2 chega depois
    print(f"\n⏰ T=30: {vtols[1].vtol_id} tenta pousar...")
    vtols[1]._start_landing()
    if vtols[1].state == "landing":
        if vertiport.land_vtol(vtols[1]):
            vtols[1].state = "landed"
            vtols[1].current_vertiport = vertiport
            print(f"  ✅ {vtols[1].vtol_id} pousou com sucesso")
        else:
            vtols[1]._start_hovering()
            print(f"  ⏸️ {vtols[1].vtol_id} deve pairar")
    
    print(f"  📊 Ocupação: {vertiport.get_occupancy_info()}")
    
    # VTOL 3 chega por último
    print(f"\n⏰ T=60: {vtols[2].vtol_id} tenta pousar...")
    vtols[2]._start_landing()
    if vtols[2].state == "landing":
        if vertiport.land_vtol(vtols[2]):
            vtols[2].state = "landed"
            vtols[2].current_vertiport = vertiport
            print(f"  ✅ {vtols[2].vtol_id} pousou com sucesso")
        else:
            vtols[2]._start_hovering()
            print(f"  ⏸️ {vtols[2].vtol_id} deve pairar")
    
    print(f"  📊 Ocupação: {vertiport.get_occupancy_info()}")
    
    # Mostra situação atual
    print(f"\n--- Situação Atual ---")
    print(f"VTOLs pousados:")
    for vtol in vertiport.occupied_slots:
        print(f"  🛬 {vtol.vtol_id} (estado: {vtol.state})")
    
    print(f"VTOLs pairando:")
    for vtol in vertiport.hovering_queue:
        print(f"  🔄 {vtol.vtol_id} (estado: {vtol.state})")
    
    # Simula decolagem
    if vertiport.occupied_slots:
        departing_vtol = vertiport.occupied_slots[0]
        print(f"\n⏰ T=120: {departing_vtol.vtol_id} decola...")
        departing_vtol._start_takeoff()
        print(f"  🛫 {departing_vtol.vtol_id} iniciou decolagem")
        print(f"  📊 Ocupação após decolagem: {vertiport.get_occupancy_info()}")
        
        # Verifica se próximo VTOL pode pousar
        if vertiport.hovering_queue:
            next_vtol = vertiport.hovering_queue[0]
            print(f"  🔔 {next_vtol.vtol_id} foi notificado para tentar pousar")
            
            # Simula tentativa de pouso
            if vertiport.land_vtol(next_vtol):
                next_vtol.state = "landed"
                next_vtol.current_vertiport = vertiport
                print(f"  ✅ {next_vtol.vtol_id} conseguiu pousar!")
                print(f"  📊 Nova ocupação: {vertiport.get_occupancy_info()}")
    
    print(f"\n--- Estado Final ---")
    occupancy = vertiport.get_occupancy_info()
    print(f"📈 Relatório de Capacidade:")
    print(f"  • Capacidade total: {occupancy['capacity']}")
    print(f"  • VTOLs pousados: {occupancy['occupied']}")
    print(f"  • Vagas livres: {occupancy['available']}")
    print(f"  • VTOLs pairando: {occupancy['hovering_count']}")
    print(f"  • Taxa de ocupação: {occupancy['occupancy_rate']:.1%}")
    
    print(f"\n🎯 Conclusão:")
    if occupancy['hovering_count'] > 0:
        print(f"  ✅ Sistema funcionando corretamente!")
        print(f"  ✅ VTOLs estão pairando quando capacidade está cheia")
        print(f"  ✅ Fila de espera está funcionando")
    else:
        print(f"  ⚠️ Todos os VTOLs conseguiram pousar")
    
    return vertiport, vtols

def test_multiple_vertiports():
    """Testa cenário com múltiplos vertiportos com capacidades diferentes"""
    
    print(f"\n=== Teste com Múltiplos Vertiportos ===")
    
    # Cria rede com 3 vertiportos de capacidades diferentes
    network = Network()
    vertiports = []
    
    # Vertiport pequeno (cap 1)
    vp1 = Vertiport(200, 200, capacity=1)
    network.add_node(vp1)
    vertiports.append(("Pequeno", vp1))
    
    # Vertiport médio (cap 2)
    vp2 = Vertiport(500, 200, capacity=2)
    network.add_node(vp2)
    vertiports.append(("Médio", vp2))
    
    # Vertiport grande (cap 4)
    vp3 = Vertiport(800, 200, capacity=4)
    network.add_node(vp3)
    vertiports.append(("Grande", vp3))
    
    print("🏢 Vertiportos criados:")
    for name, vp in vertiports:
        print(f"  • {name}: capacidade {vp.capacity}")
    
    # Conecta os vertiportos
    network.add_link(vp1, vp2)
    network.add_link(vp2, vp3)
    
    # Cria VTOLs e testa capacidades
    print(f"\n📊 Testando capacidades:")
    for name, vp in vertiports:
        print(f"\n--- Vertiport {name} ---")
        
        # Tenta adicionar VTOLs até exceder capacidade
        vtols_created = []
        for i in range(vp.capacity + 2):  # Cria 2 VTOLs a mais que a capacidade
            vtol = VTOL(100, 100, network=network)
            vtol.vtol_id = f"{name[0]}{i+1}"
            
            if vp.request_landing(vtol):
                vp.land_vtol(vtol)
                vtol.state = "landed"
                vtol.current_vertiport = vp
                status = "✅ Pousado"
            else:
                status = "⏸️ Pairando"
            
            vtols_created.append(vtol)
            print(f"  {vtol.vtol_id}: {status}")
        
        occupancy = vp.get_occupancy_info()
        print(f"  📊 Ocupação: {occupancy['occupied']}/{occupancy['capacity']} " +
              f"(pairando: {occupancy['hovering_count']})")
    
    print(f"\n🎯 Teste de múltiplos vertiportos concluído!")

if __name__ == "__main__":
    simulate_capacity_scenario()
    test_multiple_vertiports()
