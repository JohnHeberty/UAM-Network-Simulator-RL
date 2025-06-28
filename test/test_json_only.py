#!/usr/bin/env python3
"""
Teste final para verificar que o modo automático foi removido completamente
e que apenas o modo JSON funciona.
"""
import sys
import os

# Define path to data directory
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'data')

# Adiciona o diretório src ao PATH para importar módulos
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from Modules.Simulation.engine import Simulation

def test_json_only_mode():
    """Testa se apenas o modo JSON funciona"""
    print("🧪 Teste: Modo JSON Obrigatório")
    print("=" * 40)
    
    try:
        # Tenta criar simulação com JSONs válidos
        print("✅ Teste 1: Criando simulação com JSONs válidos...")
        sim = Simulation(
            vertiports_json=os.path.join(data_path, "vertiports.json"),
            vtol_routes_json=os.path.join(data_path, "vtol_routes.json")
        )
        print(f"   ✅ Sucesso! {len(sim.evtols)} VTOLs criados")
        print(f"   ✅ {len(sim.vertiports_list)} vertiportos carregados")
        
    except Exception as e:
        print(f"   ❌ Falha inesperada: {e}")
        return False
    
    try:
        # Tenta criar simulação sem parâmetros (usa defaults)
        print("\n✅ Teste 2: Criando simulação sem parâmetros...")
        sim2 = Simulation()  # Deve usar os defaults
        print(f"   ✅ Sucesso! {len(sim2.evtols)} VTOLs criados")
        print(f"   ✅ {len(sim2.vertiports_list)} vertiportos carregados")
        
    except Exception as e:
        print(f"   ❌ Falha inesperada: {e}")
        return False
    
    try:
        # Tenta criar simulação com JSON inexistente
        print("\n❌ Teste 3: Tentando usar JSON inexistente...")
        sim3 = Simulation(
            vertiports_json="arquivo_inexistente.json",
            vtol_routes_json="outro_inexistente.json"
        )
        print(f"   ❌ ERRO: Deveria ter falhado mas criou {len(sim3.evtols)} VTOLs")
        return False
        
    except Exception as e:
        print(f"   ✅ Comportamento correto: {e}")
    
    return True

if __name__ == "__main__":
    print("🧪 Teste Final: Remoção do Modo Automático")
    print("=" * 50)
    
    success = test_json_only_mode()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCESSO! Modo automático removido corretamente")
        print("✅ Sistema agora funciona apenas com JSONs")
    else:
        print("💥 FALHA! Ainda há problemas no sistema")
