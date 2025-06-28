#!/usr/bin/env python3
import sys
import os

# Adiciona o caminho dos módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'Modules', 'Simulation'))

# Importa o engine
from engine import Simulation, SimulatorUI
import time

def test_vtol_circulation():
    """Testa a circulação de VTOLs de forma simplificada"""
    print("🧪 Teste de Circulação de VTOLs")
    print("=" * 40)
    
    # Cria simulação com rede circular
    print("📊 Criando simulação com rede circular...")
    sim = Simulation(num_vtols=2, auto_create_network=True)
    
    print(f"🚁 VTOLs criados: {len(sim.evtols)}")
    
    # Simula alguns frames da simulação
    print("\n🔄 Simulando movimento dos VTOLs...")
    for frame in range(600):  # 10 segundos a 60 FPS
        for vtol in sim.evtols:
            vtol.update()
            
            # Logs de debug a cada 60 frames (1 segundo)
            if frame % 60 == 0:
                print(f"Frame {frame}: {vtol.vtol_id} - Estado: {vtol.state}")
                if hasattr(vtol, '_next_destination'):
                    print(f"  📍 Próximo destino agendado: {vtol._next_destination}")
                if vtol.current_vertiport:
                    print(f"  🏢 Vertiport atual: {vtol.current_vertiport}")
                if vtol.destination_vertiport:
                    print(f"  🎯 Destino: {vtol.destination_vertiport}")
                print(f"  ⏱️ Timer: {vtol.state_timer}")
                if hasattr(vtol, 'flight_path') and vtol.flight_path:
                    print(f"  🛤️ Path length: {len(vtol.flight_path)}, Index: {vtol.current_path_index}")
                if hasattr(vtol, 'intermediate_target') and vtol.intermediate_target:
                    print(f"  🎯 Intermediate target: {vtol.intermediate_target}")
                    # Calcula distância ao target
                    dist = ((vtol.xo - vtol.intermediate_target[0])**2 + (vtol.yo - vtol.intermediate_target[1])**2)**0.5
                    print(f"  📏 Distance to target: {dist:.1f}")
                print(f"  📍 Position: ({vtol.xo}, {vtol.yo})")
                print()
        
        # Para o teste se não há mais VTOLs circulantes
        active_vtols = [v for v in sim.evtols if hasattr(v, 'is_circulating') and v.is_circulating]
        if not active_vtols:
            print("⚠️ Todos os VTOLs pararam de circular!")
            break
    
    print("✅ Teste concluído!")
    
    # Mostra estado final
    print("\n📊 Estado Final dos VTOLs:")
    for i, vtol in enumerate(sim.evtols):
        print(f"VTOL {i+1} ({vtol.vtol_id}):")
        print(f"  Estado: {vtol.state}")
        print(f"  Circulando: {getattr(vtol, 'is_circulating', False)}")
        print(f"  Posição: ({vtol.xo}, {vtol.yo})")
        print(f"  Vertiport atual: {vtol.current_vertiport}")
        print(f"  Destino: {vtol.destination_vertiport}")
        if hasattr(vtol, '_next_destination'):
            print(f"  Próximo destino agendado: {vtol._next_destination}")
        print()

if __name__ == "__main__":
    test_vtol_circulation()
