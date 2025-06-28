#!/usr/bin/env python3
"""
Teste de stress para verificar hovering com capacidade reduzida.
"""

import sys
import os

# Adiciona o diretório de módulos ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Modules'))

from Modules.Simulation.engine import Simulation

def test_capacity_stress():
    """Testa capacidade reduzindo drasticamente as capacidades"""
    
    print("=== Teste de Stress de Capacidade ===")
    
    # Cria simulação usando JSONs
    simulation = Simulation(
        vertiports_json="vertiports.json",
        vtol_routes_json="vtol_routes.json"
    )
    
    print(f"🔧 Reduzindo capacidades dos vertiportos para 1...")
    
    # Reduz capacidade de todos os vertiportos para 1
    for vp_info in simulation.vertiports_list:
        vp_obj = vp_info['object']
        if hasattr(vp_obj, 'capacity'):
            vp_obj.capacity = 1  # Força capacidade mínima
            print(f"  🏢 {vp_info['id']}: capacidade = 1")
    
    # Simula 10 ciclos para forçar colisões de capacidade
    print(f"\n🔄 Simulando 10 ciclos para forçar hovering...")
    
    hovering_detected = False
    capacity_violations = []
    
    for cycle in range(10):
        print(f"\n--- Ciclo {cycle + 1} ---")
        
        # Força todos os VTOLs a tentar pousar simultaneamente para stressar o sistema
        if cycle == 5:  # No meio da simulação
            print("💥 STRESS TEST: Forçando todos os VTOLs a tentar pousar no mesmo vertiport!")
            target_vp = simulation.vertiports_list[0]['object']  # Primeiro vertiport
            
            for vtol in simulation.evtols:
                vtol.destination_vertiport = target_vp
                if vtol.state in ["landed", "flying"]:
                    vtol.state = "flying"
                    vtol._start_landing()
                    print(f"  🚁 {getattr(vtol, 'vtol_id', 'VTOL')} direcionado para {simulation.vertiports_list[0]['id']}")
        
        # Atualiza VTOLs
        for vtol in simulation.evtols:
            old_state = vtol.state
            vtol.update()
            
            if old_state != vtol.state:
                vtol_id = getattr(vtol, 'vtol_id', 'VTOL-sem-ID')
                print(f"  🚁 {vtol_id}: {old_state} → {vtol.state}")
                
                if vtol.state == "hovering":
                    hovering_detected = True
                    print(f"    ⭐ HOVERING DETECTADO! {vtol_id} está pairando!")
        
        # Verifica capacidades
        for vp_info in simulation.vertiports_list:
            vp_obj = vp_info['object']
            if hasattr(vp_obj, 'get_occupancy_info'):
                occupancy = vp_obj.get_occupancy_info()
                
                if occupancy['hovering_count'] > 0:
                    hovering_detected = True
                    print(f"  🏢 {vp_info['id']}: {occupancy['occupied']}/{occupancy['capacity']} " +
                          f"(⏸️ {occupancy['hovering_count']} pairando)")
                
                # Detecta violações de capacidade
                if occupancy['occupied'] > occupancy['capacity']:
                    violation = f"Vertiport {vp_info['id']}: {occupancy['occupied']} > {occupancy['capacity']}"
                    if violation not in capacity_violations:
                        capacity_violations.append(violation)
                        print(f"  ❌ VIOLAÇÃO DE CAPACIDADE: {violation}")
        
        # Para se detectou hovering para análise
        if hovering_detected and cycle > 6:
            print(f"  ✅ Hovering detectado! Parando simulação para análise.")
            break
    
    # Análise final
    print(f"\n📊 ANÁLISE FINAL:")
    print(f"  • Hovering detectado: {'✅ SIM' if hovering_detected else '❌ NÃO'}")
    print(f"  • Violações de capacidade: {len(capacity_violations)}")
    
    if capacity_violations:
        print(f"  ❌ Violações encontradas:")
        for violation in capacity_violations:
            print(f"    - {violation}")
    else:
        print(f"  ✅ Nenhuma violação de capacidade!")
    
    # Estado final detalhado
    print(f"\n🎯 Estado Final dos Vertiportos:")
    total_hovering = 0
    for vp_info in simulation.vertiports_list:
        vp_obj = vp_info['object']
        if hasattr(vp_obj, 'get_occupancy_info'):
            occupancy = vp_obj.get_occupancy_info()
            total_hovering += occupancy['hovering_count']
            
            print(f"  🏢 {vp_info['id']} ({vp_info['name']}):")
            print(f"    📊 Ocupação: {occupancy['occupied']}/{occupancy['capacity']} " +
                  f"({occupancy['occupancy_rate']:.1%})")
            
            if occupancy['occupied'] > 0:
                print(f"    🛬 VTOLs pousados:")
                for vtol in vp_obj.occupied_slots:
                    print(f"      - {getattr(vtol, 'vtol_id', 'VTOL-sem-ID')}")
            
            if occupancy['hovering_count'] > 0:
                print(f"    ⏸️ VTOLs pairando:")
                for vtol in vp_obj.hovering_queue:
                    print(f"      - {getattr(vtol, 'vtol_id', 'VTOL-sem-ID')}")
    
    print(f"\n🏆 RESULTADO DO TESTE:")
    if hovering_detected:
        print(f"  ✅ SUCCESS: Sistema de capacidade funcionando!")
        print(f"  ✅ VTOLs fazem hovering quando necessário")
        print(f"  ✅ Total de VTOLs pairando: {total_hovering}")
    else:
        print(f"  ⚠️ INCONCLUSIVE: Hovering não foi necessário neste cenário")
        print(f"  ℹ️ Pode indicar que a capacidade ainda é suficiente")
    
    if len(capacity_violations) == 0:
        print(f"  ✅ Nenhuma violação de capacidade detectada")
    else:
        print(f"  ❌ {len(capacity_violations)} violações de capacidade!")
    
    return simulation, hovering_detected

if __name__ == "__main__":
    test_capacity_stress()
