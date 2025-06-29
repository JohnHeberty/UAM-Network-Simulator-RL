"""
Test Simulation - Engine Testing Script

Comprehensive testing of the UAM Network Simulator engine.
"""

import sys
import os
import pandas as pd
import pygame

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.Modules.Simulation.engine import Simulation, Network, VTOL, Vertiport


def test_engine(headless=True):
    """Test all engine components."""
    print("UAM Network Simulator - Engine Test")
    print("=" * 40)
    print(f"Mode: {'Headless' if headless else 'Visual'}")
    
    # Test 1: Data Loading
    print("\n1. Testing CSV Data Loading...")
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        vertiports_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_info.csv'), sep=';')
        links_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_link.csv'), sep=';')
        print(f"✓ Loaded {len(vertiports_df)} vertiports and links matrix")
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        return False
    
    # Test 2: Network Creation
    print("\n2. Testing Network Creation...")
    try:
        network = Network(vertiports_df, links_df)
        vertiports = network.get_vertiports()
        print(f"✓ Created network with {len(vertiports)} vertiports")
        print(f"✓ Network has {len(list(network.graph.edges()))} edges")
        
        # Test pathfinding
        if len(vertiports) >= 2:
            path = network.get_shortest_path(vertiports[0], vertiports[-1])
            if path:
                print(f"✓ Path {vertiports[0]} → {vertiports[-1]}: {' → '.join(path)}")
            else:
                print(f"✓ No path found from {vertiports[0]} to {vertiports[-1]}")
    except Exception as e:
        print(f"✗ Network creation failed: {e}")
        return False
    
    # Test 3: Simulation Logic
    print("\n3. Testing Simulation Logic...")
    try:
        simulation = Simulation(vertiports_df, links_df)
        
        # Add test VTOLs
        vtol_added = simulation.add_vtol(1, vertiports[0], vertiports[1], 0, 1)
        if vtol_added:
            print("✓ Added test VTOL successfully")
        else:
            print("✗ Failed to add VTOL")
        
        # Run simulation steps
        for step in range(15):
            simulation.simulate_step()
            if step % 5 == 0:
                states = {}
                for vtol in simulation.vtols:
                    state = vtol.status
                    states[state] = states.get(state, 0) + 1
                print(f"  Step {step}: Time={simulation.current_time}, States={states}")
        
        results = simulation.get_simulation_results()
        print(f"✓ Simulation ran for {results['current_time']} steps")
        print(f"  Final: {results['landed_vtols']} landed, {results['flying_vtols']} flying")
    except Exception as e:
        print(f"✗ Simulation test failed: {e}")
        return False
    
    # Test 4: Pygame Components
    print("\n4. Testing Pygame Components...")
    
    # Only use dummy driver in headless mode
    if headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    try:
        pygame.init()
        
        if headless:
            screen = pygame.Surface((800, 600))
        else:
            screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption("UAM Test - Pygame Components")
        
        vertiport = Vertiport(100, 100, capacity=2, name="Test_VP")
        vertiport.draw(screen)
        print(f"✓ Vertiport '{vertiport.name}' created successfully")
        
        vtol = VTOL(150, 150, network)
        vtol.draw(screen)
        print(f"✓ VTOL created in state '{vtol.state}'")
        
        if not headless:
            pygame.display.flip()
            pygame.time.wait(1000)  # Show for 1 second
        
        pygame.quit()
        print("✓ Pygame components working")
    except Exception as e:
        print(f"✗ Pygame test failed: {e}")
        return False
    
    # Test 5: Visual Simulation
    print("\n5. Testing Visual Simulation...")
    try:
        pygame.init()
        
        if headless:
            screen = pygame.Surface((1000, 800))
            clock = None
        else:
            screen = pygame.display.set_mode((1000, 800))
            pygame.display.set_caption("UAM Test - Visual Simulation")
            clock = pygame.time.Clock()
        
        simulation = Simulation(vertiports_df, links_df)
        simulation.add_vtol(1, vertiports[0], vertiports[1], 0, 1)
        
        print(f"✓ Created visual simulation with {len(simulation.vtols)} VTOLs")
        
        # Run visual frames
        for frame in range(60 if not headless else 20):
            # Handle events in visual mode
            if not headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            break
            
            simulation.simulate_step()
            screen.fill((40, 40, 60))
            simulation.network.draw(screen)
            
            for vtol in simulation.vtols:
                vtol.draw(screen)
            
            if not headless:
                pygame.display.flip()
                if clock:
                    clock.tick(10)  # 10 FPS for testing
            
            if frame % 10 == 0:
                states = {}
                for vtol in simulation.vtols:
                    state = vtol.state if hasattr(vtol, 'state') else vtol.status
                    states[state] = states.get(state, 0) + 1
                print(f"  Frame {frame}: States={states}")
        
        pygame.quit()
        print("✓ Visual simulation completed")
    except Exception as e:
        print(f"✗ Visual simulation failed: {e}")
        return False
    
    return True


def main():
    """Main function."""
    print("Starting comprehensive engine test...\n")
    
    # Ask user for test mode
    try:
        mode_choice = input("Run test with visual interface? (Y/n): ").strip().lower()
        headless = mode_choice in ['n', 'no']
    except:
        headless = False  # Default to visual mode
    
    success = test_engine(headless)
    
    if success:
        print("\n" + "=" * 40)
        print("🎉 ALL TESTS PASSED!")
        print("✓ CSV data loading")
        print("✓ NetworkX integration") 
        print("✓ Simulation logic")
        print("✓ Pygame visualization")
        print("✓ Visual simulation")
        
        print("\nEngine is fully functional with pygame support!")
        
        # Offer interactive demo
        if not headless:
            try:
                choice = input("\nRun full interactive demo? (Y/n): ").strip().lower()
                if choice not in ['n', 'no']:
                    print("Starting demo... (SPACE=pause, I=info, ESC=exit)")
                    # Import and run demo from demo directory
                    demo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demo')
                    sys.path.insert(0, demo_path)
                    import demo_pygame_visualization
                    demo_pygame_visualization.main()
            except Exception as e:
                print(f"Demo failed: {e}")
        else:
            print("\nFor visual testing, run: python tests/test_visual.py")
    else:
        print("\n❌ Some tests failed.")
    
    print("\nEngine testing completed!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
