"""
Demo script for VTOL routing with CSV DataFrame support
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.Modules.Simulation.engine import Simulation, Network


def load_csv_data():
    """Load CSV data as DataFrames."""
    vertiports_df = pd.read_csv('src/data/matriz_od_info.csv', sep=';')
    links_df = pd.read_csv('src/data/matriz_od_link.csv', sep=';')
    return vertiports_df, links_df


def demo_network_analysis():
    """Demonstrate network analysis capabilities."""
    print("=== UAM Network Analysis Demo ===")
    
    vertiports_df, links_df = load_csv_data()
    network = Network(vertiports_df, links_df)
    
    print(f"Network has {len(network.get_vertiports())} vertiports")
    
    # Analyze connectivity
    print("\nConnectivity Analysis:")
    total_edges = 0
    bidirectional_edges = 0
    
    for origin in network.get_vertiports():
        neighbors = network.get_neighbors(origin)
        total_edges += len(neighbors)
        
        for destination in neighbors:
            if network.is_bidirectional(origin, destination):
                bidirectional_edges += 1
    
    # Avoid double counting bidirectional edges
    unique_bidirectional = bidirectional_edges // 2
    unidirectional_edges = total_edges - bidirectional_edges
    
    print(f"  Total directed edges: {total_edges}")
    print(f"  Bidirectional links: {unique_bidirectional}")
    print(f"  Unidirectional links: {unidirectional_edges}")
    
    # Show route possibilities
    print("\nRoute Analysis:")
    vertiports = network.get_vertiports()
    
    for origin in vertiports:
        reachable = []
        for destination in vertiports:
            if origin != destination:
                path = network.get_shortest_path(origin, destination)
                if path:
                    reachable.append(f"{destination}({len(path)-1} hops)")
        
        print(f"  {origin} can reach: {', '.join(reachable)}")


def demo_vtol_simulation():
    """Demonstrate VTOL simulation."""
    print("\n=== VTOL Simulation Demo ===")
    
    vertiports_df, links_df = load_csv_data()
    sim = Simulation(vertiports_df, links_df)
    
    # Create realistic VTOL scenarios
    scenarios = [
        {"id": 1, "origin": "V1", "destination": "V5", "departure": 0, "passengers": 2, "description": "Morning commute"},
        {"id": 2, "origin": "V2", "destination": "V4", "departure": 1, "passengers": 1, "description": "Business trip"},
        {"id": 3, "origin": "V3", "destination": "V1", "departure": 2, "passengers": 3, "description": "Family transport"},
        {"id": 4, "origin": "V5", "destination": "V2", "departure": 0, "passengers": 1, "description": "Return journey"},
        {"id": 5, "origin": "V4", "destination": "V3", "departure": 3, "passengers": 2, "description": "Afternoon meeting"}
    ]
    
    print("Adding VTOLs to simulation:")
    for scenario in scenarios:
        success = sim.add_vtol(
            scenario["id"], 
            scenario["origin"], 
            scenario["destination"], 
            scenario["departure"], 
            scenario["passengers"]
        )
        
        if success:
            route = sim.network.get_shortest_path(scenario["origin"], scenario["destination"])
            print(f"  ✓ VTOL {scenario['id']}: {scenario['description']}")
            print(f"    Route: {' → '.join(route)}")
        else:
            print(f"  ✗ VTOL {scenario['id']}: Failed to add")
    
    # Run simulation
    print(f"\nRunning simulation...")
    results = sim.run_simulation(max_time=100)
    
    # Print results
    print(f"\n=== Simulation Results ===")
    print(f"Simulation time: {results['current_time']} steps")
    print(f"Total VTOLs: {results['total_vtols']}")
    print(f"  Landed: {results['landed_vtols']} ({results['landed_vtols']/results['total_vtols']*100:.1f}%)")
    print(f"  Flying: {results['flying_vtols']}")
    print(f"  Waiting: {results['waiting_vtols']}")
    
    # Detailed results
    print(f"\nDetailed VTOL Status:")
    for vtol in results['vtol_details']:
        status_emoji = {"LANDED": "✅", "FLYING": "✈️", "WAITING": "⏳"}
        
        print(f"  {status_emoji.get(vtol['status'], '❓')} VTOL {vtol['id']}: {vtol['status']}")
        print(f"    Journey: {vtol['origin']} → {vtol['destination']}")
        print(f"    Current location: {vtol['current_vertiport']}")
        
        if vtol['hover_count'] > 0:
            print(f"    Hover count: {vtol['hover_count']}")
        
        if len(vtol['route']) > 2:
            remaining_route = vtol['route'][vtol['route'].index(vtol['current_vertiport']):]
            print(f"    Remaining path: {' → '.join(remaining_route)}")


def demo_capacity_analysis():
    """Demonstrate capacity constraints."""
    print("\n=== Capacity Analysis Demo ===")
    
    vertiports_df, links_df = load_csv_data()
    network = Network(vertiports_df, links_df)
    
    print("Vertiport Capacities:")
    for vertiport_id in network.get_vertiports():
        info = network.get_vertiport_info(vertiport_id)
        neighbors = network.get_neighbors(vertiport_id)
        print(f"  {vertiport_id}: Capacity={info['capacity']}, Connections={len(neighbors)}")
    
    # Test high-traffic scenario
    print(f"\nHigh-traffic scenario simulation:")
    sim = Simulation(vertiports_df, links_df)
    
    # Add many VTOLs to create congestion
    for i in range(1, 8):
        origin = f"V{((i-1) % 5) + 1}"
        destination = f"V{(i % 5) + 1}"
        success = sim.add_vtol(i, origin, destination, 0, 1)
        
        if success:
            print(f"  Added VTOL {i}: {origin} → {destination}")
        else:
            print(f"  Failed to add VTOL {i}: {origin} → {destination} (no route)")
    
    # Run simulation
    results = sim.run_simulation(max_time=50)
    
    print(f"\nHigh-traffic results:")
    print(f"  Landed VTOLs: {results['landed_vtols']}/{results['total_vtols']}")
    print(f"  Average hover count: {sum(v['hover_count'] for v in results['vtol_details'])/len(results['vtol_details']):.1f}")
    
    # Show VTOLs with high hover counts
    high_hover = [v for v in results['vtol_details'] if v['hover_count'] >= 3]
    if high_hover:
        print(f"  VTOLs with high hover counts:")
        for vtol in high_hover:
            print(f"    VTOL {vtol['id']}: {vtol['hover_count']} hovers")


if __name__ == "__main__":
    print("UAM Network Simulator - CSV DataFrame Demo")
    print("=" * 50)
    
    try:
        demo_network_analysis()
        demo_vtol_simulation()
        demo_capacity_analysis()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
