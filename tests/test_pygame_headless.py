"""
Automated test for pygame visualization (no GUI)
"""

import pygame
import pandas as pd
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.Modules.Simulation.engine import Simulation, VTOL

def test_pygame_visualization():
    """Test the pygame visualization without opening a window"""
    
    # Set SDL to use dummy video driver (no window)
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    try:
        pygame.init()
        
        # Create a dummy surface for testing
        screen = pygame.Surface((800, 600))
        
        # Load data
        project_root = os.path.dirname(os.path.dirname(__file__))
        vertiports_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_info.csv'), sep=';')
        links_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_link.csv'), sep=';')
        
        # Create simulation
        simulation = Simulation(vertiports_df, links_df)
        
        # Add test VTOLs
        vertiports = simulation.network.get_vertiports()
        simulation.add_vtol(1, vertiports[0], vertiports[1], 0, 1)
        
        # Add circulating VTOL
        if len(vertiports) >= 1:
            origin_obj = simulation.network.get_vertiport_object(vertiports[0])
            if origin_obj:
                circulating_vtol = VTOL(origin_obj.x + 30, origin_obj.y + 30, simulation.network)
                circulating_vtol.vtol_id = "VTOL_2"
                circulating_vtol.current_vertiport = origin_obj
                circulating_vtol.is_circulating = True
                circulating_vtol.state = "landed"
                simulation.vtols.append(circulating_vtol)
        
        print(f"✓ Created simulation with {len(simulation.vtols)} VTOLs")
        
        # Test drawing for several frames
        for frame in range(30):
            # Update simulation
            simulation.simulate_step()
            
            # Clear screen
            screen.fill((40, 40, 60))
            
            # Test drawing network
            simulation.network.draw(screen)
            
            # Test drawing VTOLs
            for vtol in simulation.vtols:
                vtol.draw(screen)
            
            if frame % 10 == 0:
                print(f"✓ Frame {frame}: Simulation time {simulation.current_time}")
        
        # Check VTOL states
        states = {}
        for vtol in simulation.vtols:
            state = vtol.state if hasattr(vtol, 'state') else vtol.status
            states[state] = states.get(state, 0) + 1
        
        print(f"✓ Final VTOL states: {states}")
        
        # Test vertiport occupancy
        for vp_id, vp_obj in simulation.network.vertiport_objects.items():
            occupancy = vp_obj.get_occupancy_info()
            print(f"✓ {vp_id}: {occupancy['occupied']}/{occupancy['capacity']} occupied")
        
        pygame.quit()
        print("🎉 Pygame visualization test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Pygame visualization test failed: {e}")
        pygame.quit()
        return False

if __name__ == "__main__":
    print("Testing pygame visualization components (headless)...\n")
    success = test_pygame_visualization()
    sys.exit(0 if success else 1)
