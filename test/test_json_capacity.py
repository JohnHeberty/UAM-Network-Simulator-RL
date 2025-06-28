#!/usr/bin/env python3
"""
Teste de capacidade usando configuração JSON real.
"""

# Define path to data directory
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'data')

import sys
import os
import time

# Adiciona o diretório de módulos ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Modules'))

from Modules.Simulation.engine import Simulation

def test_json_capacity():
    """Testa capacidade usando VTOLs e vertiportos do JSON"""
    
    print("=== Teste de Capacidade com Configuração JSON ===")
    
    # Cria simulação usando JSONs
    simulation = Simulation(
        vertiports_json=os.path.join(data_path, "vertiports.json"),
        vtol_routes_json=os.path.join(data_path, "vtol_routes.json")
    )
    
    print(f"📍 Simulação criada com {len(simulation.vertiports_list)} vertiportos")
    print(f"🚁 Simulação criada com {len(simulation.evtols)} VTOLs")
    
    # Mostra capacidades dos vertiportos
    print(f"\n--- Capacidades dos Vertiportos ---")
    for vp_info in simulation.vertiports_list:
        vp_obj = vp_info['object']
        if hasattr(vp_obj, 'capacity'):
            occupancy = vp_obj.get_occupancy_info()
            print(f"🏢 {vp_info['id']} ({vp_info['name']}): " +
                  f"capacidade {occupancy['capacity']}, " +
                  f"ocupação {occupancy['occupied']}/{occupancy['capacity']}")
        else:
            print(f"🏢 {vp_info['id']} ({vp_info['name']}): sem controle de capacidade")
    
    # Verifica estado inicial dos VTOLs
    print(f"\n--- Estado Inicial dos VTOLs ---")
    for vtol in simulation.evtols:
        if hasattr(vtol, 'vtol_id'):
            print(f"🚁 {vtol.vtol_id}: estado '{vtol.state}' na posição ({vtol.xo}, {vtol.yo})")
            if vtol.current_vertiport and hasattr(vtol.current_vertiport, 'get_occupancy_info'):
                # Registra o VTOL no vertiport se está pousado
                if vtol.state == "landed" and vtol not in vtol.current_vertiport.occupied_slots:
                    vtol.current_vertiport.occupied_slots.append(vtol)
                    print(f"  📍 Registrado no vertiport (ocupação atualizada)")
    
    # Mostra ocupação após registro
    print(f"\n--- Ocupação Após Registro Inicial ---")
    for vp_info in simulation.vertiports_list:
        vp_obj = vp_info['object']
        if hasattr(vp_obj, 'get_occupancy_info'):
            occupancy = vp_obj.get_occupancy_info()
            print(f"🏢 {vp_info['id']}: {occupancy['occupied']}/{occupancy['capacity']} " +
                  f"(taxa: {occupancy['occupancy_rate']:.1%})")
            
            # Lista VTOLs pousados
            if occupancy['occupied'] > 0:
                for vtol in vp_obj.occupied_slots:
                    print(f"  🛬 {getattr(vtol, 'vtol_id', 'VTOL-sem-ID')}")
    
    # Simula alguns ciclos de atualização para ver o comportamento
    print(f"\n--- Simulando Movimentação ---")
    for cycle in range(3):
        print(f"\n🔄 Ciclo {cycle + 1}:")
        
        # Atualiza cada VTOL
        for vtol in simulation.evtols:
            old_state = vtol.state
            vtol.update()
            
            if old_state != vtol.state:
                vtol_id = getattr(vtol, 'vtol_id', 'VTOL-sem-ID')
                print(f"  🚁 {vtol_id}: {old_state} → {vtol.state}")
                
                # Se começou a pairar, mostra isso
                if vtol.state == "hovering":
                    if vtol.destination_vertiport and hasattr(vtol.destination_vertiport, 'get_occupancy_info'):
                        vp_occupancy = vtol.destination_vertiport.get_occupancy_info()
                        print(f"    ⏸️ Pairando sobre vertiport (ocupação: {vp_occupancy['occupied']}/{vp_occupancy['capacity']})")
        
        # Mostra mudanças na ocupação
        for vp_info in simulation.vertiports_list:
            vp_obj = vp_info['object']
            if hasattr(vp_obj, 'get_occupancy_info'):
                occupancy = vp_obj.get_occupancy_info()
                if occupancy['occupied'] > 0 or occupancy['hovering_count'] > 0:
                    print(f"  🏢 {vp_info['id']}: ocupado {occupancy['occupied']}/{occupancy['capacity']}, " +
                          f"pairando {occupancy['hovering_count']}")
        
        time.sleep(0.1)  # Pequena pausa para visualização
    
    print(f"\n🎯 Teste de capacidade com JSON concluído!")
    
    # Relatório final
    total_hovering = 0
    total_capacity_full = 0
    
    for vp_info in simulation.vertiports_list:
        vp_obj = vp_info['object']
        if hasattr(vp_obj, 'get_occupancy_info'):
            occupancy = vp_obj.get_occupancy_info()
            total_hovering += occupancy['hovering_count']
            if occupancy['occupancy_rate'] >= 1.0:
                total_capacity_full += 1
    
    print(f"\n📊 Relatório Final:")
    print(f"  • VTOLs pairando: {total_hovering}")
    print(f"  • Vertiportos lotados: {total_capacity_full}")
    
    if total_hovering > 0:
        print(f"  ✅ Sistema de capacidade funcionando! VTOLs estão pairando quando necessário.")
    else:
        print(f"  ℹ️ Nenhum VTOL precisou pairar neste teste.")
    
    return simulation

if __name__ == "__main__":
    test_json_capacity()
