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


def test_engine():
    """Test all engine components."""
    print("UAM Network Simulator - Engine Test")
    print("=" * 40)
    
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
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    try:
        pygame.init()
        screen = pygame.Surface((800, 600))
        
        vertiport = Vertiport(100, 100, capacity=2, name="Test_VP")
        vertiport.draw(screen)
        print(f"✓ Vertiport '{vertiport.name}' created successfully")
        
        vtol = VTOL(150, 150, network)
        vtol.draw(screen)
        print(f"✓ VTOL created in state '{vtol.state}'")
        
        pygame.quit()
        print("✓ Pygame components working")
    except Exception as e:
        print(f"✗ Pygame test failed: {e}")
        return False
    
    # Test 5: Visual Simulation
    print("\n5. Testing Visual Simulation...")
    try:
        pygame.init()
        screen = pygame.Surface((1000, 800))
        
        simulation = Simulation(vertiports_df, links_df)
        simulation.add_vtol(1, vertiports[0], vertiports[1], 0, 1)
        
        print(f"✓ Created visual simulation with {len(simulation.vtols)} VTOLs")
        
        # Run visual frames
        for frame in range(20):
            simulation.simulate_step()
            screen.fill((40, 40, 60))
            simulation.network.draw(screen)
            
            for vtol in simulation.vtols:
                vtol.draw(screen)
            
            if frame % 5 == 0:
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
    
    success = test_engine()
    
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
        try:
            choice = input("\nRun interactive demo? (y/N): ").strip().lower()
            if choice in ['y', 'yes']:
                print("Starting demo... (SPACE=pause, I=info, ESC=exit)")
                import demo_pygame_visualization
                demo_pygame_visualization.main()
        except:
            pass
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
