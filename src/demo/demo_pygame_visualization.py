"""
Demo of the UAM Network Simulator with Pygame Visualization

This script demonstrates the pygame-based visualization of VTOLs moving through the network.
"""

import pygame
import sys
import pandas as pd
from src.Modules.Simulation.engine import Simulation, VTOL

def main():
    """Main demo function"""
    # Initialize pygame
    pygame.init()
    
    # Screen setup
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("UAM Network Simulator - Pygame Visualization")
    clock = pygame.time.Clock()
    
    # Load data
    try:
        vertiports_df = pd.read_csv('src/data/matriz_od_info.csv', sep=';')
        links_df = pd.read_csv('src/data/matriz_od_link.csv', sep=';')
        print(f"Loaded {len(vertiports_df)} vertiports and links matrix")
    except FileNotFoundError as e:
        print(f"Error loading data files: {e}")
        pygame.quit()
        sys.exit(1)
    
    # Create simulation
    simulation = Simulation(vertiports_df, links_df)
    print(f"Created simulation with {len(simulation.network.get_vertiports())} vertiports")
    
    # Add some test VTOLs
    vertiports = simulation.network.get_vertiports()
    if len(vertiports) >= 2:
        # Add VTOL from first to second vertiport
        simulation.add_vtol(1, vertiports[0], vertiports[1], 0, 1)
        print(f"Added VTOL 1: {vertiports[0]} -> {vertiports[1]}")
        
        if len(vertiports) >= 3:
            # Add VTOL from first to third vertiport
            simulation.add_vtol(2, vertiports[0], vertiports[2], 10, 1)
            print(f"Added VTOL 2: {vertiports[0]} -> {vertiports[2]}")
        
        if len(vertiports) >= 4:
            # Add circulating VTOL
            origin_obj = simulation.network.get_vertiport_object(vertiports[0])
            circulating_vtol = VTOL(origin_obj.x + 30, origin_obj.y + 30, simulation.network)
            circulating_vtol.id = 3
            circulating_vtol.current_vertiport = origin_obj
            circulating_vtol.is_circulating = True
            circulating_vtol.state = "landed"
            circulating_vtol.state_timer = 30
            simulation.vtols.append(circulating_vtol)
            print(f"Added circulating VTOL 3 starting at {vertiports[0]}")
    
    # Font for UI text
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    # Main loop
    running = True
    simulation_running = True
    show_info = True
    
    print("\nStarting pygame visualization...")
    print("Controls:")
    print("  SPACE - Pause/Resume simulation")
    print("  I - Toggle info display")
    print("  ESC - Exit")
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    simulation_running = not simulation_running
                    print(f"Simulation {'resumed' if simulation_running else 'paused'}")
                elif event.key == pygame.K_i:
                    show_info = not show_info
                    print(f"Info display {'enabled' if show_info else 'disabled'}")
        
        # Update simulation
        if simulation_running:
            simulation.simulate_step()
        
        # Clear screen
        screen.fill((40, 40, 60))
        
        # Draw network
        simulation.network.draw(screen)
        
        # Draw VTOLs
        for vtol in simulation.vtols:
            vtol.draw(screen)
        
        # Draw UI information
        if show_info:
            y_offset = 10
            
            # Simulation info
            time_text = font.render(f"Time: {simulation.current_time}", True, (255, 255, 255))
            screen.blit(time_text, (10, y_offset))
            y_offset += 30
            
            status_text = small_font.render(f"Status: {'Running' if simulation_running else 'Paused'}", True, (255, 255, 255))
            screen.blit(status_text, (10, y_offset))
            y_offset += 25
            
            # VTOL info
            vtol_text = small_font.render(f"VTOLs: {len(simulation.vtols)}", True, (255, 255, 255))
            screen.blit(vtol_text, (10, y_offset))
            y_offset += 20
            
            # Count VTOLs by state
            state_counts = {}
            for vtol in simulation.vtols:
                state = vtol.state if hasattr(vtol, 'state') else vtol.status
                state_counts[state] = state_counts.get(state, 0) + 1
            
            for state, count in state_counts.items():
                state_text = small_font.render(f"  {state}: {count}", True, (200, 200, 200))
                screen.blit(state_text, (20, y_offset))
                y_offset += 18
            
            # Vertiport occupancy
            y_offset += 10
            occupancy_title = small_font.render("Vertiport Occupancy:", True, (255, 255, 255))
            screen.blit(occupancy_title, (10, y_offset))
            y_offset += 20
            
            for vp_id, vp_obj in simulation.network.vertiport_objects.items():
                occupancy = vp_obj.get_occupancy_info()
                occ_text = small_font.render(
                    f"  {vp_id}: {occupancy['occupied']}/{occupancy['capacity']} "
                    f"(hover: {occupancy['hovering_count']})", 
                    True, (200, 200, 200)
                )
                screen.blit(occ_text, (20, y_offset))
                y_offset += 18
            
            # Controls
            y_offset = HEIGHT - 80
            controls = [
                "SPACE: Pause/Resume",
                "I: Toggle info",
                "ESC: Exit"
            ]
            for control in controls:
                control_text = small_font.render(control, True, (180, 180, 180))
                screen.blit(control_text, (10, y_offset))
                y_offset += 18
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    # Cleanup
    pygame.quit()
    print("Pygame visualization ended")

if __name__ == "__main__":
    main()
