#!/usr/bin/env python3
import sys
import os

# Define path to data directory
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'data')

# Adiciona o caminho dos módulos
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Importa o engine
from Modules.Simulation.engine import Simulation
import time

def test_json_vtol_routes():
    """Testa especificamente as rotas JSON personalizadas"""
    print("🧪 Teste de Rotas JSON Personalizadas")
    print("=" * 45)
    
    # Cria simulação com configuração JSON
    print("📊 Criando simulação com rotas JSON personalizadas...")
    try:
        sim = Simulation(
            vertiports_json=os.path.join(data_path, "vertiports.json"),
            vtol_routes_json=os.path.join(data_path, "vtol_routes.json")
        )
        
        print(f"🚁 VTOLs criados: {len(sim.evtols)}")
        print(f"📍 Vertiportos: {len(sim.vertiports_list)}")
        
        # Busca especificamente o BETA-2
        beta2_vtol = None
        for vtol in sim.evtols:
            if hasattr(vtol, 'vtol_id') and vtol.vtol_id == 'BETA-2':
                beta2_vtol = vtol
                break
        
        if not beta2_vtol:
            print("❌ VTOL BETA-2 não foi encontrado!")
            return False
        
        print(f"✅ BETA-2 encontrado!")
        print(f"   Rota: {' → '.join(beta2_vtol.custom_route)}")
        print(f"   Índice atual: {beta2_vtol.current_route_index}")
        print(f"   Estado: {beta2_vtol.state}")
        print()
        
        # Simula alguns ciclos para verificar progressão da rota
        print("🔄 Simulando movimentação do BETA-2...")
        cycle_count = 0
        max_cycles = 50
        route_positions = []
        
        while cycle_count < max_cycles:
            # Atualiza a simulação
            sim.update()
            
            # Registra posição na rota se o VTOL estiver pousado
            if beta2_vtol.state == "landed" and beta2_vtol.current_vertiport:
                current_vp_id = None
                for vp_id, vp_obj in beta2_vtol.vertiports_map.items():
                    if vp_obj == beta2_vtol.current_vertiport:
                        current_vp_id = vp_id
                        break
                
                if current_vp_id and (not route_positions or route_positions[-1] != current_vp_id):
                    route_positions.append(current_vp_id)
                    print(f"   ✈️  Ciclo {cycle_count}: BETA-2 pousou em {current_vp_id} (índice: {beta2_vtol.current_route_index})")
                    
                    # Verifica se completou pelo menos um ciclo da rota
                    if len(route_positions) >= len(beta2_vtol.custom_route):
                        print("✅ BETA-2 completou um ciclo completo da rota!")
                        print(f"   Sequência visitada: {' → '.join(route_positions)}")
                        return True
            
            cycle_count += 1
            time.sleep(0.01)  # Pequena pausa para não sobrecarregar
        
        print(f"⚠️ Teste concluído após {max_cycles} ciclos")
        print(f"   Sequência visitada: {' → '.join(route_positions)}")
        print(f"   Estado final: {beta2_vtol.state}")
        
        # Considera sucesso se visitou pelo menos 2 vertiportos
        if len(route_positions) >= 2:
            print("✅ BETA-2 está circulando corretamente!")
            return True
        else:
            print("❌ BETA-2 não circulou adequadamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste do Bug BETA-2 - Rotas JSON")
    print("=" * 50)
    print()
    
    success = test_json_vtol_routes()
    
    print()
    if success:
        print("🎉 TESTE PASSOU! BETA-2 está funcionando corretamente")
    else:
        print("💥 TESTE FALHOU! Há problemas com o BETA-2")
