"""
Visual Test - UAM Network Simulator Visual Testing

Interactive visual testing of the UAM Network Simulator engine with pygame interface.
"""

import sys
import os
import pandas as pd
import pygame

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.Modules.Simulation.engine import Simulation, Network, VTOL, Vertiport


def test_visual_components():
    """Test visual components with real pygame window."""
    print("UAM Network Simulator - Visual Test")
    print("=" * 45)
    print("Visual components test with pygame window")
    print("Press ESC to continue between tests")
    
    # Test 1: Data Loading
    print("\n1. Loading CSV Data...")
    try:
        vertiports_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_info.csv'), sep=';')
        links_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_link.csv'), sep=';')
        print(f"✓ Loaded {len(vertiports_df)} vertiports and links matrix")
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        return False
    
    # Test 2: Static Visual Components
    print("\n2. Testing Static Visual Components...")
    print("  Opening pygame window - press ESC to continue...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("UAM Test - Static Components")
    clock = pygame.time.Clock()
    
    try:
        network = Network(vertiports_df, links_df)
        vertiport = Vertiport(150, 150, capacity=2, name="Test_VP")
        vtol = VTOL(200, 200, network)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            
            screen.fill((40, 40, 60))
            
            # Draw network first
            network.draw(screen)
            
            # Draw test vertiport
            vertiport.draw(screen)
            
            # Draw test VTOL
            vtol.draw(screen)
            
            # Add text
            if pygame.font.get_init():
                font = pygame.font.Font(None, 24)
                text = font.render("Static Components Test - ESC to continue", True, (255, 255, 255))
                screen.blit(text, (10, 10))
            
            pygame.display.flip()
            clock.tick(60)
        
        print("✓ Static components working")
    except Exception as e:
        print(f"✗ Static components test failed: {e}")
        pygame.quit()
        return False
    
    # Test 3: Dynamic Simulation
    print("\n3. Testing Dynamic Simulation...")
    print("  Running visual simulation - ESC to continue...")
    
    pygame.display.set_caption("UAM Test - Dynamic Simulation")
    
    try:
        simulation = Simulation(vertiports_df, links_df)
        vertiports = simulation.network.get_vertiports()
        
        # Add multiple VTOLs for better visualization
        simulation.add_vtol(1, vertiports[0], vertiports[1], 0, 1)
        if len(vertiports) > 2:
            simulation.add_vtol(2, vertiports[1], vertiports[2], 5, 1)
        if len(vertiports) > 3:
            simulation.add_vtol(3, vertiports[0], vertiports[3], 10, 1)
        
        print(f"✓ Created simulation with {len(simulation.vtols)} VTOLs")
        
        frame_count = 0
        running = True
        paused = False
        
        while running and frame_count < 300:  # 5 minutes at 60 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                        print(f"  {'Paused' if paused else 'Resumed'}")
            
            if not paused:
                simulation.simulate_step()
            
            screen.fill((40, 40, 60))
            simulation.network.draw(screen)
            
            for vtol in simulation.vtols:
                vtol.draw(screen)
            
            # Add text overlay
            if pygame.font.get_init():
                font = pygame.font.Font(None, 24)
                text_lines = [
                    f"Dynamic Simulation Test - Frame {frame_count}",
                    f"Time: {simulation.current_time} | VTOLs: {len(simulation.vtols)}",
                    "SPACE=pause/resume, ESC=exit"
                ]
                
                for i, line in enumerate(text_lines):
                    text = font.render(line, True, (255, 255, 255))
                    screen.blit(text, (10, 10 + i * 25))
                
                # Show VTOL states
                states = {}
                for vtol in simulation.vtols:
                    state = vtol.state if hasattr(vtol, 'state') else vtol.status
                    states[state] = states.get(state, 0) + 1
                
                state_text = f"States: {states}"
                text = font.render(state_text, True, (200, 200, 255))
                screen.blit(text, (10, 100))
            
            pygame.display.flip()
            clock.tick(30)  # 30 FPS for better visualization
            frame_count += 1
            
            if frame_count % 30 == 0:  # Every second
                states = {}
                for vtol in simulation.vtols:
                    state = vtol.state if hasattr(vtol, 'state') else vtol.status
                    states[state] = states.get(state, 0) + 1
                print(f"  Frame {frame_count}: {states}")
        
        print("✓ Dynamic simulation completed")
    except Exception as e:
        print(f"✗ Dynamic simulation failed: {e}")
        pygame.quit()
        return False
    
    pygame.quit()
    return True


def main():
    """Main function."""
    print("Starting visual engine test...\n")
    
    try:
        success = test_visual_components()
        
        if success:
            print("\n" + "=" * 45)
            print("🎉 ALL VISUAL TESTS PASSED!")
            print("✓ CSV data loading")
            print("✓ Static visual components")
            print("✓ Dynamic simulation visualization")
            print("\nVisual engine is fully functional!")
        else:
            print("\n❌ Some visual tests failed.")
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted")
        pygame.quit()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        pygame.quit()
        import traceback
        traceback.print_exc()
    
    print("\nVisual testing completed!")


if __name__ == "__main__":
    main()
