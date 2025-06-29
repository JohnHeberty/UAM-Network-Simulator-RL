"""
Test script for NetworkX integration with CSV DataFrame support
"""

import sys
import os
import pandas as pd

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.Modules.Simulation.engine import Simulation, Network


def load_csv_data():
    """Load CSV data as DataFrames."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    vertiports_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_info.csv'), sep=';')
    links_df = pd.read_csv(os.path.join(project_root, 'src/data/matriz_od_link.csv'), sep=';')
    
    print("Vertiports DataFrame:")
    print(vertiports_df)
    print("\nLinks DataFrame:")
    print(links_df)
    
    return vertiports_df, links_df


def test_network_creation():
    """Test network creation from CSV DataFrames."""
    print("=== Testing Network Creation from CSV DataFrames ===")
    
    vertiports_df, links_df = load_csv_data()
    
    # Create network
    network = Network(vertiports_df, links_df)
    
    # Test basic network operations
    vertiports = network.get_vertiports()
    print(f"Vertiports: {vertiports}")
    
    # Test connectivity
    print("\nTesting connectivity:")
    for origin in vertiports:
        neighbors = network.get_neighbors(origin)
        print(f"  {origin} -> {neighbors}")
    
    # Test bidirectionality
    print("\nTesting bidirectionality:")
    for origin in vertiports:
        for destination in vertiports:
            if origin != destination and network.has_edge(origin, destination):
                is_bidir = network.is_bidirectional(origin, destination)
                print(f"  {origin} -> {destination}: {'bidirectional' if is_bidir else 'unidirectional'}")
    
    # Test shortest paths
    print("\nTesting shortest paths:")
    test_routes = [
        ("V1", "V5"),
        ("V2", "V4"),
        ("V3", "V1"),
        ("V5", "V2")
    ]
    
    for origin, destination in test_routes:
        path = network.get_shortest_path(origin, destination)
        print(f"  {origin} -> {destination}: {path}")
    
    return network


def test_simulation():
    """Test simulation with CSV DataFrames."""
    print("\n=== Testing Simulation with CSV DataFrames ===")
    
    vertiports_df, links_df = load_csv_data()
    
    # Create simulation
    sim = Simulation(vertiports_df, links_df)
    
    # Add some VTOLs
    vtol_configs = [
        (1, "V1", "V5", 0, 2),
        (2, "V2", "V4", 1, 1),
        (3, "V3", "V1", 2, 3),
        (4, "V5", "V2", 0, 1)
    ]
    
    for vtol_id, origin, destination, departure_time, passengers in vtol_configs:
        success = sim.add_vtol(vtol_id, origin, destination, departure_time, passengers)
        print(f"Added VTOL {vtol_id} ({origin} -> {destination}): {'Success' if success else 'Failed'}")
    
    # Run simulation
    print(f"\nRunning simulation for 50 time steps...")
    results = sim.run_simulation(max_time=50)
    
    # Print results
    print(f"Simulation completed at time {results['current_time']}")
    print(f"Total VTOLs: {results['total_vtols']}")
    print(f"Landed: {results['landed_vtols']}")
    print(f"Waiting: {results['waiting_vtols']}")
    print(f"Flying: {results['flying_vtols']}")
    
    print("\nVTOL Details:")
    for vtol in results['vtol_details']:
        print(f"  VTOL {vtol['id']}: {vtol['origin']} -> {vtol['destination']}")
        print(f"    Status: {vtol['status']}")
        print(f"    Current location: {vtol['current_vertiport']}")
        print(f"    Route: {' -> '.join(vtol['route'])}")
        print(f"    Hover count: {vtol['hover_count']}")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n=== Testing Edge Cases ===")
    
    vertiports_df, links_df = load_csv_data()
    sim = Simulation(vertiports_df, links_df)
    
    # Test invalid vertiports
    print("Testing invalid vertiports:")
    invalid_tests = [
        (10, "V1", "V99", 0, 1),  # Invalid destination
        (11, "V99", "V1", 0, 1),  # Invalid origin
        (12, "V99", "V99", 0, 1)  # Both invalid
    ]
    
    for vtol_id, origin, destination, departure_time, passengers in invalid_tests:
        success = sim.add_vtol(vtol_id, origin, destination, departure_time, passengers)
        print(f"  VTOL {vtol_id} ({origin} -> {destination}): {'Success' if success else 'Failed (expected)'}")
    
    # Test no path scenarios
    print("\nTesting connectivity:")
    all_vertiports = sim.network.get_vertiports()
    
    for origin in all_vertiports:
        for destination in all_vertiports:
            if origin != destination:
                path = sim.network.get_shortest_path(origin, destination)
                if not path:
                    print(f"  No path from {origin} to {destination}")


if __name__ == "__main__":
    print("Testing UAM Network Simulator with CSV DataFrame support")
    print("=" * 60)
    
    try:
        # Test network creation
        network = test_network_creation()
        
        # Test simulation
        test_simulation()
        
        # Test edge cases
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
