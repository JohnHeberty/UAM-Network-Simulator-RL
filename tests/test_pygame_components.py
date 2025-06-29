"""
Simple test of the pygame visualization components
"""

import os
import pandas as pd
import pygame
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.Modules.Simulation.engine import Network, VTOL, Vertiport

def test_pygame_components():
    """Test individual pygame components"""
    
    # Load test data
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        vertiports_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_info.csv'), sep=';')
        links_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_link.csv'), sep=';')
        print(f"✓ Loaded data: {len(vertiports_df)} vertiports")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return False
    
    # Test Network creation
    try:
        network = Network(vertiports_df, links_df)
        print(f"✓ Created network with {len(network.get_vertiports())} vertiports")
        print(f"✓ Network has {len(list(network.graph.edges()))} edges")
    except Exception as e:
        print(f"✗ Error creating network: {e}")
        return False
    
    # Test Vertiport creation
    try:
        vertiport = Vertiport(100, 100, capacity=3, name="Test_VP")
        print(f"✓ Created vertiport at ({vertiport.x}, {vertiport.y}) with capacity {vertiport.capacity}")
    except Exception as e:
        print(f"✗ Error creating vertiport: {e}")
        return False
    
    # Test VTOL creation
    try:
        vtol = VTOL(150, 150, network)
        print(f"✓ Created VTOL at ({vtol.xo}, {vtol.yo}) with state '{vtol.state}'")
    except Exception as e:
        print(f"✗ Error creating VTOL: {e}")
        return False
    
    # Test pygame initialization (without display)
    try:
        pygame.init()
        print("✓ Pygame initialized successfully")
        
        # Test if we can create a surface (headless)
        test_surface = pygame.Surface((800, 600))
        print("✓ Can create pygame surfaces")
        
        pygame.quit()
        print("✓ Pygame cleanup successful")
    except Exception as e:
        print(f"✗ Pygame error: {e}")
        return False
    
    print("\n🎉 All pygame components are working correctly!")
    return True

if __name__ == "__main__":
    print("Testing pygame visualization components...\n")
    success = test_pygame_components()
    sys.exit(0 if success else 1)
