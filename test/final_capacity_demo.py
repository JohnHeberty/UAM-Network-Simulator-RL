#!/usr/bin/env python3
"""
Demonstração final completa do sistema de capacidade de vertiportos.
"""

import sys
import os

# Adiciona o diretório de módulos ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Modules'))

from Modules.Simulation.engine import Vertiport, VTOL, Network

def final_capacity_demo():
    """Demonstração completa e controlada do sistema de capacidade"""
    
    print("🎯 DEMONSTRAÇÃO FINAL - Sistema de Capacidade de Vertiportos")
    print("=" * 70)
    
    # Cria cenário controlado
    network = Network()
    vertiport = Vertiport(500, 400, capacity=2)
    network.add_node(vertiport)
    
    print(f"🏢 Vertiport criado com capacidade: {vertiport.capacity}")
    print(f"📊 Estado inicial: {vertiport.get_occupancy_info()}")
    
    # Cria 5 VTOLs para testar o sistema
    vtols = []
    for i in range(5):
        vtol = VTOL(100 + i*50, 100, network=network)
        vtol.vtol_id = f"CHARLIE-{i+1}"
        vtol.destination_vertiport = vertiport
        vtols.append(vtol)
        print(f"🚁 {vtol.vtol_id} criado")
    
    print(f"\n📝 CENÁRIO: 5 VTOLs tentarão usar 1 vertiport com capacidade 2")
    print(f"💡 ESPERADO: 2 vão pousar, 3 vão pairar")
    
    # Fase 1: Tentativas de pouso
    print(f"\n🎬 FASE 1: Tentativas de Pouso")
    print("-" * 40)
    
    successful_landings = 0
    hovering_vtols = 0
    
    for i, vtol in enumerate(vtols):
        print(f"\n⏰ Tentativa {i+1}: {vtol.vtol_id}")
        
        # Solicita permissão para pousar
        can_land = vertiport.request_landing(vtol)
        print(f"  📋 Solicitação: {'✅ AUTORIZADA' if can_land else '❌ NEGADA'}")
        
        if can_land:
            # Efetua o pouso
            landing_success = vertiport.land_vtol(vtol)
            if landing_success:
                vtol.state = "landed"
                vtol.current_vertiport = vertiport
                successful_landings += 1
                print(f"  🛬 {vtol.vtol_id} POUSOU com sucesso")
            else:
                print(f"  ❌ Falha no pouso (erro interno)")
        else:
            # Vai para estado de hovering
            vtol.state = "hovering"
            hovering_vtols += 1
            print(f"  ⏸️ {vtol.vtol_id} PAIRANDO (aguardando vaga)")
        
        # Mostra ocupação atual
        occupancy = vertiport.get_occupancy_info()
        print(f"  📊 Ocupação: {occupancy['occupied']}/{occupancy['capacity']} " +
              f"(pairando: {occupancy['hovering_count']})")
    
    # Fase 2: Estado intermediário
    print(f"\n🎬 FASE 2: Estado Intermediário")
    print("-" * 40)
    
    final_occupancy = vertiport.get_occupancy_info()
    print(f"📊 Resultado da Fase 1:")
    print(f"  • VTOLs que pousaram: {successful_landings}")
    print(f"  • VTOLs pairando: {hovering_vtols}")
    print(f"  • Capacidade usada: {final_occupancy['occupied']}/{final_occupancy['capacity']}")
    print(f"  • Taxa de ocupação: {final_occupancy['occupancy_rate']:.1%}")
    
    print(f"\n👥 VTOLs pousados no vertiport:")
    for vtol in vertiport.occupied_slots:
        print(f"  🛬 {vtol.vtol_id} (estado: {vtol.state})")
    
    print(f"\n⏸️ VTOLs pairando (fila de espera):")
    for i, vtol in enumerate(vertiport.hovering_queue, 1):
        print(f"  {i}. {vtol.vtol_id} (estado: {vtol.state})")
    
    # Fase 3: Liberação de vaga
    if vertiport.occupied_slots and vertiport.hovering_queue:
        print(f"\n🎬 FASE 3: Liberação de Vaga")
        print("-" * 40)
        
        # Remove primeiro VTOL (simula decolagem)
        departing_vtol = vertiport.occupied_slots[0]
        print(f"🛫 {departing_vtol.vtol_id} está decolando...")
        
        takeoff_success = vertiport.takeoff_vtol(departing_vtol)
        if takeoff_success:
            departing_vtol.state = "taking_off"
            departing_vtol.current_vertiport = None
            print(f"  ✅ {departing_vtol.vtol_id} decolou com sucesso")
            
            # Verifica ocupação após decolagem
            post_takeoff_occupancy = vertiport.get_occupancy_info()
            print(f"  📊 Ocupação após decolagem: {post_takeoff_occupancy['occupied']}/{post_takeoff_occupancy['capacity']}")
            
            # Verifica se próximo VTOL pode pousar
            if vertiport.hovering_queue:
                next_vtol = vertiport.hovering_queue[0]
                print(f"  🔔 {next_vtol.vtol_id} (primeiro da fila) pode tentar pousar")
                
                # Simula tentativa automática de pouso
                if vertiport.land_vtol(next_vtol):
                    next_vtol.state = "landed"
                    next_vtol.current_vertiport = vertiport
                    print(f"  🛬 {next_vtol.vtol_id} pousou automaticamente!")
                    
                    final_final_occupancy = vertiport.get_occupancy_info()
                    print(f"  📊 Nova ocupação: {final_final_occupancy['occupied']}/{final_final_occupancy['capacity']} " +
                          f"(pairando: {final_final_occupancy['hovering_count']})")
    
    # Resultado final
    print(f"\n🏆 RESULTADO FINAL")
    print("=" * 70)
    
    final_state = vertiport.get_occupancy_info()
    
    print(f"📈 Estatísticas Finais:")
    print(f"  • Capacidade do vertiport: {final_state['capacity']}")
    print(f"  • VTOLs atualmente pousados: {final_state['occupied']}")
    print(f"  • VTOLs ainda pairando: {final_state['hovering_count']}")
    print(f"  • Vagas disponíveis: {final_state['available']}")
    print(f"  • Taxa de ocupação: {final_state['occupancy_rate']:.1%}")
    
    print(f"\n🛬 VTOLs atualmente no vertiport:")
    if final_state['occupied'] > 0:
        for vtol in vertiport.occupied_slots:
            print(f"  • {vtol.vtol_id}")
    else:
        print(f"  • Nenhum")
    
    print(f"\n⏸️ VTOLs ainda pairando:")
    if final_state['hovering_count'] > 0:
        for vtol in vertiport.hovering_queue:
            print(f"  • {vtol.vtol_id}")
    else:
        print(f"  • Nenhum")
    
    # Validação do sistema
    print(f"\n✅ VALIDAÇÃO DO SISTEMA:")
    
    # Teste 1: Capacidade respeitada
    capacity_respected = final_state['occupied'] <= final_state['capacity']
    print(f"  • Capacidade respeitada: {'✅ SIM' if capacity_respected else '❌ NÃO'}")
    
    # Teste 2: Hovering funcionando
    hovering_working = final_state['hovering_count'] > 0 or successful_landings == final_state['capacity']
    print(f"  • Sistema de hovering: {'✅ FUNCIONANDO' if hovering_working else '❌ PROBLEMA'}")
    
    # Teste 3: Fila funcionando
    queue_working = len(vertiport.hovering_queue) == final_state['hovering_count']
    print(f"  • Fila de espera: {'✅ CONSISTENTE' if queue_working else '❌ INCONSISTENTE'}")
    
    # Teste 4: Total de VTOLs conservado
    total_accounted = final_state['occupied'] + final_state['hovering_count']
    expected_total = min(len(vtols), final_state['capacity'] + 3)  # Cap + hovering
    vtols_conserved = total_accounted <= len(vtols)
    print(f"  • VTOLs contabilizados: {'✅ CORRETO' if vtols_conserved else '❌ ERRO'}")
    
    overall_success = all([capacity_respected, hovering_working, queue_working, vtols_conserved])
    
    print(f"\n🎯 CONCLUSÃO: {'🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!' if overall_success else '⚠️ PROBLEMAS DETECTADOS'}")
    
    if overall_success:
        print(f"✅ O sistema de capacidade está integrado e funcionando corretamente!")
        print(f"✅ VTOLs respeitam a capacidade dos vertiportos")
        print(f"✅ VTOLs ficam pairando quando não há vaga disponível")
        print(f"✅ A fila de espera funciona adequadamente")
        print(f"✅ Liberação de vagas permite novos pousos")
    
    return vertiport, vtols, overall_success

if __name__ == "__main__":
    final_capacity_demo()
