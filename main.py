"""
UAM Network Simulator - Simulação Completa Unificada

Sistema completo de simulação UAM com todas as funcionalidades integradas:
- VTOLs com rotas planejadas carregadas do JSON (circulares e ping-pong)
- VTOLs de simulação tradicional (ponto-a-ponto)
- Sistema de passageiros baseado em demanda temporal do CSV
- Passageiros gerados dentro dos vertiportos
- Embarque/desembarque com animações visuais
- Pathfinding automático para cada perna da rota
- Visualização em tempo real com informações detalhadas
- Controles interativos para pausar, reiniciar e alternar visualizações
- Sistema de testes integrado para validação
"""

import pandas as pd
import pygame
import sys
import os
import random

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.Modules.Simulation.engine import Simulation, MatrizOD, Person

# ===============================================================================
# FUNÇÕES DE PASSAGEIROS
# ===============================================================================

def spawn_passengers_from_demand(simulation):
    """Spawn passengers based on current demand from CSV"""
    if not simulation.matriz_od:
        return
    
    current_demands = simulation.matriz_od.get_current_demand()
    
    for demand in current_demands:
        origem = demand['origem']
        destino = demand['destino']
        quantidade = demand['demanda']
        
        # Get vertiport objects
        origem_vp = simulation.network.get_vertiport_object(origem)
        destino_vp = simulation.network.get_vertiport_object(destino)
        
        if origem_vp and destino_vp:
            # Spawn passengers with a probability based on demand
            for _ in range(quantidade):
                if random.random() < 0.1:  # 10% chance per frame per passenger
                    spawn_passenger_at_vertiport(simulation, origem_vp, destino_vp)

def spawn_passenger_at_vertiport(simulation, origin_vertiport, destination_vertiport):
    """Spawn a single passenger at a vertiport"""
    # Get spawn position inside vertiport
    spawn_x, spawn_y = origin_vertiport.get_passenger_spawn_position()
    
    # Create passenger
    passenger = Person(spawn_x, spawn_y, origin_vertiport, destination_vertiport)
    
    # Add to vertiport and simulation
    origin_vertiport.add_passenger(passenger)
    
    # Add to simulation passengers list if it exists
    if not hasattr(simulation, 'passengers'):
        simulation.passengers = []
    simulation.passengers.append(passenger)
    
    print(f"Spawned passenger at {origin_vertiport.name} going to {destination_vertiport.name}")

def draw_passengers(simulation, screen):
    """Draw all passengers in the simulation"""
    if hasattr(simulation, 'passengers'):
        for passenger in simulation.passengers[:]:  # Copy list to avoid modification during iteration
            if passenger.is_ready_for_cleanup():
                simulation.passengers.remove(passenger)
            else:
                passenger.draw(screen)

# ===============================================================================
# FUNÇÕES DE TESTE
# ===============================================================================

def test_passenger_boarding():
    """Test passenger boarding functionality"""
    print("\n" + "="*50)
    print("TESTE DO SISTEMA DE PASSAGEIROS")
    print("="*50)
    
    try:
        # Load data
        vertiports_df = pd.read_csv('src/data/matriz_od_info.csv', sep=';')
        links_df = pd.read_csv('src/data/matriz_od_link.csv', sep=';')
        
        # Create simulation
        simulation = Simulation(vertiports_df, links_df)
        
        # Add demand system
        simulation.matriz_od = MatrizOD('src/data/demanda_passageiros.csv')
        simulation.matriz_od.current_time_minutes = 4 * 60  # 04:00
        
        # Add a test VTOL
        simulation.add_vtol(200, "V1", "V2", 0, 4)  # Capacity for 4 passengers
        
        # Get vertiports
        v1 = simulation.network.get_vertiport_object("V1")
        v2 = simulation.network.get_vertiport_object("V2")
        
        if v1 and v2:
            # Create passengers going from V1 to V2
            for i in range(3):
                spawn_x, spawn_y = v1.get_passenger_spawn_position()
                passenger = Person(spawn_x, spawn_y, v1, v2)
                v1.add_passenger(passenger)
                print(f"✓ Created passenger {i+1} at V1 going to V2")
            
            # Get test VTOL
            vtol = simulation.vtols[0]
            print(f"\nVTOL inicial:")
            print(f"  Estado: {vtol.state}")
            print(f"  Passageiros a bordo: {len(vtol.onboard_passengers)}")
            print(f"  V1 passageiros esperando: {len(getattr(v1, 'passengers_waiting', []))}")
            
            # Simulate some steps
            print(f"\nExecutando simulação...")
            for step in range(15):
                simulation.simulate_step()
                if step in [0, 5, 10, 14]:
                    print(f"  Step {step}: Estado={vtol.state}, Passageiros={len(vtol.onboard_passengers)}")
            
            print(f"\nResultados finais:")
            print(f"  ✓ VTOL estado final: {vtol.state}")
            print(f"  ✓ Passageiros a bordo: {len(vtol.onboard_passengers)}")
            print(f"  ✓ V1 passageiros esperando: {len(getattr(v1, 'passengers_waiting', []))}")
            print(f"  ✓ V2 passageiros chegados: {len(getattr(v2, 'passengers_arrived', []))}")
            
            # Validate results
            if len(vtol.onboard_passengers) > 0 or len(getattr(v2, 'passengers_arrived', [])) > 0:
                print(f"\n🎉 TESTE PASSOU: Sistema de passageiros funcionando!")
            else:
                print(f"\n⚠️  TESTE INCOMPLETO: Aguardando mais ciclos de simulação")
                
        else:
            print("❌ ERRO: Não foi possível encontrar vertiportos V1 e V2")
            return False
            
    except Exception as e:
        print(f"❌ ERRO durante o teste: {e}")
        return False
    
    return True

# ===============================================================================
# SIMULAÇÃO PRINCIPAL
# ===============================================================================

def run_complete_simulation():
    """Execute a simulação completa com visualização"""
    print("UAM Network Simulator - Simulação Completa")
    print("=" * 45)
    
    # Initialize pygame
    pygame.init()
    
    # Screen setup
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("UAM Network Simulator - Simulação Completa")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    # Load data
    try:
        vertiports_df = pd.read_csv('src/data/matriz_od_info.csv', sep=';')
        links_df = pd.read_csv('src/data/matriz_od_link.csv', sep=';')
        print(f"✓ Carregados {len(vertiports_df)} vertiportos e matriz de links")
    except FileNotFoundError as e:
        print(f"❌ Erro ao carregar arquivos de dados: {e}")
        pygame.quit()
        return
    
    # Create simulation with JSON routes
    routes_file = 'src/data/vtol_routes.json'
    simulation = Simulation(vertiports_df, links_df, routes_file)
    
    # Add passenger demand system
    demand_file = 'src/data/demanda_passageiros.csv'
    try:
        simulation.matriz_od = MatrizOD(demand_file)
        # Start simulation at 04:00 (when demand begins)
        simulation.matriz_od.current_time_minutes = 4 * 60  # 04:00
        if simulation.matriz_od.demand_data is not None:
            print(f"✓ Sistema de demanda carregado com {len(simulation.matriz_od.demand_data)} registros")
            print(f"✓ Simulação iniciando em {simulation.matriz_od.get_current_time_str()}")
        else:
            print("⚠️  Sistema de demanda carregado mas sem dados disponíveis")
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível carregar demanda de passageiros: {e}")
        simulation.matriz_od = None
    
    # Create VTOLs from JSON routes
    simulation.create_vtols_from_routes()
    json_vtols = len(simulation.vtols)
    
    # Add traditional simulation VTOLs for passenger testing
    simulation.add_vtol(100, "V1", "V5", 0, 1)  # Immediate departure
    simulation.add_vtol(101, "V3", "V1", 20, 2)  # Delayed departure  
    simulation.add_vtol(102, "V2", "V4", 40, 1)  # Later departure
    traditional_vtols = len(simulation.vtols) - json_vtols
    
    print(f"✓ Criados {json_vtols} VTOLs de rotas JSON")
    print(f"✓ Adicionados {traditional_vtols} VTOLs tradicionais")
    print(f"✓ Total: {len(simulation.vtols)} VTOLs")
    
    # Start JSON route VTOLs
    simulation.start_planned_routes()
    
    # Simulation state
    running = True
    paused = False
    show_info = True
    show_routes = True
    show_passengers = True
    show_tests = False
    frame_count = 0
    last_time_update = 0
    last_passenger_spawn = 0
    
    print(f"\n🚀 Iniciando simulação completa...")
    print("Controles:")
    print("  SPACE - Pausar/Retomar")
    print("  I - Alternar exibição de informações")
    print("  R - Alternar exibição de rotas")
    print("  P - Alternar exibição de passageiros")
    print("  T - Executar teste de passageiros")
    print("  S - Reiniciar rotas JSON")
    print("  ESC - Sair")
    
    # Main simulation loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    print(f"{'⏸️  Pausado' if paused else '▶️  Retomado'}")
                elif event.key == pygame.K_i:
                    show_info = not show_info
                elif event.key == pygame.K_r:
                    show_routes = not show_routes
                elif event.key == pygame.K_p:
                    show_passengers = not show_passengers
                    print(f"Passageiros: {'Visível' if show_passengers else 'Oculto'}")
                elif event.key == pygame.K_t:
                    show_tests = not show_tests
                    if show_tests:
                        test_passenger_boarding()
                elif event.key == pygame.K_s:
                    simulation.start_planned_routes()
                    print("🔄 Rotas JSON reiniciadas")
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        if not paused:
            # Process passenger demand system
            current_time = pygame.time.get_ticks()
            
            # Update time every second (advance simulation time)
            if current_time - last_time_update > 1000:  # 1 second
                if simulation.matriz_od:
                    simulation.matriz_od.advance_time(1)  # Advance 1 minute in simulation
                last_time_update = current_time
            
            # Spawn passengers based on demand
            if simulation.matriz_od and current_time - last_passenger_spawn > 2000:  # Every 2 seconds
                spawn_passengers_from_demand(simulation)
                last_passenger_spawn = current_time
            
            # Update simulation
            simulation.simulate_step()
            frame_count += 1
        
        # Clear screen
        screen.fill((40, 40, 60))
        
        # Draw network
        simulation.network.draw(screen)
        
        # Draw passengers if enabled
        if show_passengers:
            draw_passengers(simulation, screen)
        
        # Draw VTOLs
        for vtol in simulation.vtols:
            vtol.draw(screen)
        
        # Draw info overlay
        if show_info:
            # Count states
            states = {}
            planned_count = 0
            traditional_count = 0
            
            for vtol in simulation.vtols:
                state = vtol.state if hasattr(vtol, 'state') else vtol.status
                states[state] = states.get(state, 0) + 1
                
                if hasattr(vtol, 'planned_route') and vtol.planned_route and vtol.is_circulating:
                    planned_count += 1
                else:
                    traditional_count += 1
            
            # Count passengers
            passengers_list = getattr(simulation, 'passengers', [])
            total_passengers = len(passengers_list)
            passengers_by_state = {}
            for passenger in passengers_list:
                state = passenger.state
                passengers_by_state[state] = passengers_by_state.get(state, 0) + 1
            
            # Count passengers on VTOLs
            total_passengers_on_vtols = 0
            for vtol in simulation.vtols:
                if hasattr(vtol, 'onboard_passengers'):
                    total_passengers_on_vtols += len(vtol.onboard_passengers)
            
            # Info text
            info_lines = [
                f"Frame: {frame_count}",
                f"Tempo: {simulation.current_time}",
                f"Hora Sim: {simulation.matriz_od.get_current_time_str() if simulation.matriz_od else 'N/A'}",
                f"Total VTOLs: {len(simulation.vtols)}",
                f"  Rotas JSON: {planned_count}",
                f"  Tradicionais: {traditional_count}",
                f"Total Passageiros: {total_passengers}",
                f"  Nos VTOLs: {total_passengers_on_vtols}",
                f"Estados Passageiros: {passengers_by_state}",
                f"Estados VTOLs: {states}",
                f"Status: {'⏸️ Pausado' if paused else '▶️ Executando'}",
                "",
            ]
            
            # Add passenger demand info if enabled
            if show_passengers and simulation.matriz_od:
                info_lines.append("Demanda Atual de Passageiros:")
                current_demands = simulation.matriz_od.get_current_demand()
                if current_demands:
                    for demand in current_demands[:5]:  # Show up to 5 demands
                        info_lines.append(f"  {demand['origem']} → {demand['destino']}: {demand['demanda']}")
                else:
                    info_lines.append("  Nenhuma demanda atual")
                info_lines.append("")
            
            # Add route info if enabled
            if show_routes:
                info_lines.append("Rotas JSON:")
                for vtol in simulation.vtols:
                    if hasattr(vtol, 'planned_route') and vtol.planned_route:
                        route = vtol.planned_route
                        current_idx = getattr(vtol, 'current_route_index', 0)
                        is_circular = getattr(vtol, 'is_circular_route', False)
                        reverse = getattr(vtol, 'reverse_direction', False)
                        
                        # Show current position in route
                        route_display = []
                        for i, vp in enumerate(route):
                            if i == current_idx:
                                route_display.append(f"[{vp}]")
                            else:
                                route_display.append(vp)
                        
                        direction = "↻" if is_circular else ("←" if reverse else "→")
                        info_lines.append(f"  {vtol.vtol_id}: {' → '.join(route_display)} {direction}")
                
                info_lines.append("")
                info_lines.append("VTOLs Tradicionais:")
                for vtol in simulation.vtols:
                    if not (hasattr(vtol, 'planned_route') and vtol.planned_route and vtol.is_circulating):
                        if hasattr(vtol, 'journey_route') and vtol.journey_route:
                            origin = vtol.journey_route[0] if vtol.journey_route else "?"
                            if hasattr(vtol, 'final_destination') and hasattr(vtol.final_destination, 'name'):
                                dest = vtol.final_destination.name
                            else:
                                dest = "?"
                            info_lines.append(f"  VTOL {vtol.vtol_id}: {origin} → {dest} ({vtol.status})")
            
            # Draw info
            y_offset = 10
            for line in info_lines:
                if line.startswith("  "):  # Indent sub-items
                    text_surface = small_font.render(line, True, (200, 200, 200))
                else:
                    text_surface = small_font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 16
        
        # Status info at bottom
        status_lines = [
            "SPACE=Pausar  I=Info  R=Rotas  P=Passageiros  T=Teste  S=Reiniciar  ESC=Sair"
        ]
        
        y_pos = HEIGHT - 30
        for line in status_lines:
            text_surface = font.render(line, True, (200, 200, 200))
            screen.blit(text_surface, (10, y_pos))
            y_pos += 25
        
        # Update display
        pygame.display.flip()
        clock.tick(10)  # 10 FPS for better visibility
        
        # Print periodic status
        if frame_count % 200 == 0:
            states = {}
            for vtol in simulation.vtols:
                state = vtol.state if hasattr(vtol, 'state') else vtol.status
                states[state] = states.get(state, 0) + 1
            print(f"Frame {frame_count}: {states}")
    
    # Final report
    print(f"\n📊 Simulação finalizada após {frame_count} frames:")
    results = simulation.get_simulation_results()
    print(f"  ✓ Total VTOLs: {results['total_vtols']}")
    print(f"  ✓ Voando: {results['flying_vtols']}")
    print(f"  ✓ Pousados: {results['landed_vtols']}")
    print(f"  ✓ Esperando: {results['waiting_vtols']}")
    
    # Cleanup
    pygame.quit()
    print("\n🎉 Simulação completa finalizada!")

# ===============================================================================
# MENU PRINCIPAL
# ===============================================================================

def show_main_menu():
    """Show main menu and handle user choice"""
    print("\n" + "="*60)
    print("🚁 UAM NETWORK SIMULATOR - MENU PRINCIPAL")
    print("="*60)
    print("Escolha uma opção:")
    print()
    print("1. 🎮 Executar Simulação Completa (Visual)")
    print("2. 🧪 Executar Teste de Passageiros")
    print("3. 📊 Executar Ambos (Teste + Simulação)")
    print("4. ❌ Sair")
    print()
    
    while True:
        try:
            choice = input("Digite sua escolha (1-4): ").strip()
            
            if choice == "1":
                print("\n🎮 Iniciando simulação visual...")
                run_complete_simulation()
                break
            elif choice == "2":
                print("\n🧪 Executando teste de passageiros...")
                test_passenger_boarding()
                input("\nPressione Enter para continuar...")
                show_main_menu()
                break
            elif choice == "3":
                print("\n🔄 Executando teste e simulação...")
                test_success = test_passenger_boarding()
                if test_success:
                    input("\nTeste concluído! Pressione Enter para iniciar simulação visual...")
                    run_complete_simulation()
                else:
                    print("\n⚠️  Teste falhou. Verificar configuração antes de executar simulação.")
                    input("Pressione Enter para continuar...")
                    show_main_menu()
                break
            elif choice == "4":
                print("\n👋 Saindo do simulador...")
                break
            else:
                print("❌ Opção inválida. Digite 1, 2, 3 ou 4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saindo do simulador...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

# ===============================================================================
# MAIN
# ===============================================================================

def main():
    """Main function"""
    print("🚁 UAM Network Simulator - Iniciando...")
    
    # Verify required files exist
    required_files = [
        'src/data/matriz_od_info.csv',
        'src/data/matriz_od_link.csv', 
        'src/data/demanda_passageiros.csv',
        'src/data/vtol_routes.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Erro: Arquivos necessários não encontrados:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\nVerifique se todos os arquivos de dados estão presentes.")
        return
    
    print("✓ Todos os arquivos necessários encontrados.")
    
    # Show main menu
    show_main_menu()

if __name__ == "__main__":
    main()
