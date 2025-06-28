#!/usr/bin/env python3
import sys
import os

# Adiciona o caminho dos módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'Modules', 'Simulation'))

# Importa o engine
from engine import Simulation
import time

def test_json_vtol_routes():
    """Testa especificamente as rotas JSON personalizadas"""
    print("🧪 Teste de Rotas JSON Personalizadas")
    print("=" * 45)
    
    # Cria simulação com configuração JSON
    print("📊 Criando simulação com rotas JSON personalizadas...")
    try:
        sim = Simulation(
            num_vtols=0,  # Não cria VTOLs automáticos
            vertiports_json="vertiports.json",
            vtol_routes_json="vtol_routes.json",
            auto_create_network=False
        )
        
        print(f"🚁 VTOLs criados: {len(sim.evtols)}")
        
        # Mostra informações detalhadas de cada VTOL
        print("\n📋 Informações Detalhadas dos VTOLs:")
        for i, vtol in enumerate(sim.evtols):
            print(f"\n{vtol.vtol_id}:")
            print(f"  📍 Posição inicial: ({vtol.xo}, {vtol.yo})")
            print(f"  🛤️ Rota completa: {vtol.custom_route}")
            print(f"  🎯 Índice atual: {vtol.current_route_index}")
            print(f"  🔄 Loop: {vtol.loop_route}")
            print(f"  🏢 Vertiport atual: {vtol.current_vertiport}")
            print(f"  🎯 Destino: {vtol.destination_vertiport}")
            print(f"  📊 Estado: {vtol.state}")
        
        # Foco especial no BETA-2
        beta_2 = None
        for vtol in sim.evtols:
            if vtol.vtol_id == "BETA-2":
                beta_2 = vtol
                break
        
        if beta_2:
            print(f"\n🔍 FOCO NO BETA-2:")
            print(f"  Rota: {beta_2.custom_route}")
            print(f"  Índice atual: {beta_2.current_route_index}")
            print(f"  Próximo deveria ser: {beta_2.custom_route[(beta_2.current_route_index + 1) % len(beta_2.custom_route)]}")
        
        # Simula movimento e acompanha especificamente o BETA-2
        print("\n🔄 Simulando movimento - Foco no BETA-2...")
        for frame in range(900):  # 15 segundos a 60 FPS
            for vtol in sim.evtols:
                vtol.update()
            
            # Logs específicos do BETA-2 a cada 2 segundos
            if frame % 120 == 0 and beta_2:
                print(f"\nFrame {frame}: BETA-2")
                print(f"  Estado: {beta_2.state}")
                print(f"  Posição: ({beta_2.xo}, {beta_2.yo})")
                print(f"  Índice da rota: {beta_2.current_route_index}/{len(beta_2.custom_route)-1}")
                print(f"  Vertiport atual: {beta_2.current_vertiport}")
                print(f"  Destino: {beta_2.destination_vertiport}")
                if hasattr(beta_2, '_next_destination'):
                    print(f"  📍 Próximo agendado: {beta_2._next_destination}")
                else:
                    print(f"  📍 Próximo agendado: NENHUM")
                print(f"  Timer: {beta_2.state_timer}")
                print(f"  Circulando: {getattr(beta_2, 'is_circulating', False)}")
                
                # Mostra qual deveria ser o próximo na rota
                if beta_2.custom_route:
                    current_idx = beta_2.current_route_index
                    next_idx = (current_idx + 1) % len(beta_2.custom_route)
                    next_vp_id = beta_2.custom_route[next_idx]
                    print(f"  🎯 Próximo na rota deveria ser: {next_vp_id} (índice {next_idx})")
                
                # Verificação manual da condição para agendar próximo destino
                if beta_2.state == "landed":
                    has_circulating = hasattr(beta_2, 'is_circulating') and beta_2.is_circulating
                    has_next_dest = hasattr(beta_2, '_next_destination')
                    timer_ready = beta_2.state_timer <= 0
                    print(f"  🔧 Debug condições:")
                    print(f"    - is_circulating: {has_circulating}")
                    print(f"    - has _next_destination: {has_next_dest}")
                    print(f"    - timer <= 0: {timer_ready}")
                    print(f"    - Deveria agendar próximo: {has_circulating and not has_next_dest and timer_ready}")
        
        print("\n✅ Teste concluído!")
        
        # Estado final do BETA-2
        if beta_2:
            print(f"\n📊 Estado Final do BETA-2:")
            print(f"  Estado: {beta_2.state}")
            print(f"  Circulando: {getattr(beta_2, 'is_circulating', False)}")
            print(f"  Rota: {beta_2.custom_route}")
            print(f"  Índice atual: {beta_2.current_route_index}")
            print(f"  Posição: ({beta_2.xo}, {beta_2.yo})")
            print(f"  Vertiport atual: {beta_2.current_vertiport}")
            print(f"  Destino: {beta_2.destination_vertiport}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_json_vtol_routes()
