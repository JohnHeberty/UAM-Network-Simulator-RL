"""
UAM Network Simulator - Demo Principal

Demonstra o sistema completo de simulação UAM com:
- VTOLs com rotas planejadas carregadas do JSON (circulares e ping-pong)
- VTOLs de simulação tradicional (ponto-a-ponto)
- Pathfinding automático para cada perna da rota
- Visualização em tempo real com informações detalhadas
- Controles interativos para pausar, reiniciar e alternar visualizações

Este demo unificado substitui os demos anteriores e mostra todas as funcionalidades
do simulador em uma única aplicação.
"""

import pandas as pd
import pygame
import sys
import os

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.Modules.Simulation.engine import Simulation

def main():
    """Demo principal do simulador UAM"""
    print("UAM Network Simulator - Demo Principal")
    print("=" * 42)
    
    # Initialize pygame
    pygame.init()
    
    # Screen setup
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("UAM Network Simulator - Demo Principal")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    # Load data
    try:
        vertiports_df = pd.read_csv('src/data/matriz_od_info.csv', sep=';')
        links_df = pd.read_csv('src/data/matriz_od_link.csv', sep=';')
        print(f"Loaded {len(vertiports_df)} vertiports and links matrix")
    except FileNotFoundError as e:
        print(f"Error loading data files: {e}")
        pygame.quit()
        return
    
    # Create simulation with JSON routes
    routes_file = 'src/data/vtol_routes.json'
    simulation = Simulation(vertiports_df, links_df, routes_file)
    vertiports = simulation.network.get_vertiports()
    
    # Create VTOLs from JSON routes
    simulation.create_vtols_from_routes()
    json_vtols = len(simulation.vtols)
    
    # Add some traditional simulation VTOLs
    simulation.add_vtol(100, "V1", "V5", 0, 1)  # Immediate departure
    simulation.add_vtol(101, "V3", "V1", 20, 2)  # Delayed departure
    simulation.add_vtol(102, "V2", "V4", 40, 1)  # Later departure
    traditional_vtols = len(simulation.vtols) - json_vtols
    
    print(f"Created {json_vtols} VTOLs from JSON routes")
    print(f"Added {traditional_vtols} traditional simulation VTOLs")
    print(f"Total: {len(simulation.vtols)} VTOLs")
    
    # Start JSON route VTOLs
    simulation.start_planned_routes()
    
    # Simulation state
    running = True
    paused = False
    show_info = True
    show_routes = True
    frame_count = 0
    
    print("\nStarting complete UAM simulation...")
    print("Controls:")
    print("  SPACE - Pause/Resume")
    print("  I - Toggle info display")
    print("  R - Toggle route display")
    print("  S - Restart JSON routes")
    print("  ESC - Exit")
    
    # Main loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    print(f"{'Paused' if paused else 'Resumed'}")
                elif event.key == pygame.K_i:
                    show_info = not show_info
                elif event.key == pygame.K_r:
                    show_routes = not show_routes
                elif event.key == pygame.K_s:
                    simulation.start_planned_routes()
                    print("Restarted JSON routes")
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        if not paused:
            # Update simulation
            simulation.simulate_step()
            frame_count += 1
        
        # Clear screen
        screen.fill((40, 40, 60))
        
        # Draw network
        simulation.network.draw(screen)
        
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
            
            # Info text
            info_lines = [
                f"Frame: {frame_count}",
                f"Time: {simulation.current_time}",
                f"Total VTOLs: {len(simulation.vtols)}",
                f"  JSON Routes: {planned_count}",
                f"  Traditional: {traditional_count}",
                f"States: {states}",
                f"Paused: {paused}",
                "",
            ]
            
            # Add route info if enabled
            if show_routes:
                info_lines.append("JSON Routes:")
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
                info_lines.append("Traditional VTOLs:")
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
            "SPACE=Pause  I=Info  R=Routes  S=Restart  ESC=Exit"
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
    print(f"\nSimulação finalizada após {frame_count} frames:")
    results = simulation.get_simulation_results()
    print(f"  Total VTOLs: {results['total_vtols']}")
    print(f"  Voando: {results['flying_vtols']}")
    print(f"  Pousados: {results['landed_vtols']}")
    print(f"  Esperando: {results['waiting_vtols']}")
    
    # Cleanup
    pygame.quit()
    print("\nSimulação completa finalizada!")

if __name__ == "__main__":
    main()
