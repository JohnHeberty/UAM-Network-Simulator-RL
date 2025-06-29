#!/usr/bin/env python3
"""
Exemplo de uso do novo sistema de roteamento NetworkX
Demonstra como os VTOLs podem solicitar rotas otimizadas
"""

import sys
import os

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.Modules.Simulation.engine import Network, Vertiport, VTOL

def create_example_network():
    """Cria uma rede de exemplo para demonstração"""
    print("🏗️ Criando rede de exemplo...")
    
    # Cria uma rede mista (permite tanto links bidirecionais quanto unidirecionais)
    network = Network(directed=True)
    
    # Cria vertiportos representando locais urbanos
    locations = {
        'Airport': (100, 100),
        'Downtown': (300, 150),
        'Mall': (500, 100),
        'Hospital': (200, 300),
        'University': (400, 350),
        'Stadium': (250, 200),
        'Port': (450, 250)
    }
    
    vertiports = {}
    for name, (x, y) in locations.items():
        vp = Vertiport(x, y, capacity=3)
        network.add_node(vp)
        vertiports[name] = vp
        print(f"   📍 {name} em ({x}, {y})")
    
    # Adiciona links bidirecionais (ruas normais)
    bidirectional_routes = [
        ('Airport', 'Downtown'),
        ('Downtown', 'Stadium'),
        ('Stadium', 'Hospital'),
        ('Hospital', 'University'),
        ('Downtown', 'Mall'),
        ('Mall', 'Port'),
        ('Port', 'University')
    ]
    
    print("\n🔗 Criando links bidirecionais...")
    for origin, dest in bidirectional_routes:
        vp1, vp2 = vertiports[origin], vertiports[dest]
        distance = network.calculate_distance(vp1, vp2)
        network.add_link(vp1, vp2, bidirectional=True, weight=distance)
        print(f"   ↔️ {origin} ↔ {dest} (distância: {distance:.1f})")
    
    # Adiciona links unidirecionais (vias expressas ou restrições de tráfego aéreo)
    unidirectional_routes = [
        ('Airport', 'Mall'),      # Via expressa do aeroporto
        ('University', 'Airport') # Corredor de retorno
    ]
    
    print("\n➡️ Criando links unidirecionais...")
    for origin, dest in unidirectional_routes:
        vp1, vp2 = vertiports[origin], vertiports[dest]
        distance = network.calculate_distance(vp1, vp2)
        network.add_link(vp1, vp2, bidirectional=False, weight=distance)
        print(f"   ➡️ {origin} → {dest} (distância: {distance:.1f})")
    
    return network, vertiports

def demonstrate_vtol_routing(network, vertiports):
    """Demonstra como VTOLs podem solicitar rotas"""
    print("\n🚁 Demonstração de Roteamento VTOL")
    print("=" * 50)
    
    # Simula vários VTOLs solicitando rotas diferentes
    route_requests = [
        ('VTOL-001', 'Airport', 'University'),
        ('VTOL-002', 'Hospital', 'Mall'),
        ('VTOL-003', 'Stadium', 'Port'),
        ('VTOL-004', 'University', 'Downtown')
    ]
    
    for vtol_id, origin_name, dest_name in route_requests:
        print(f"\n🛸 {vtol_id}: {origin_name} → {dest_name}")
        
        origin_vp = vertiports[origin_name]
        dest_vp = vertiports[dest_name]
        
        # VTOL solicita rota otimizada (usando Dijkstra)
        path = network.find_shortest_path(origin_vp, dest_vp)
        
        if path:
            # Converte caminho para nomes legíveis
            route_names = []
            for vp in path:
                name = next((name for name, v in vertiports.items() if v == vp), "Unknown")
                route_names.append(name)
            
            # Calcula distância total
            # Calcula distância total do caminho
            total_distance = 0
            for i in range(len(path) - 1):
                total_distance += network.calculate_distance(path[i], path[i+1])
            
            print(f"   ✅ Rota encontrada: {' → '.join(route_names)}")
            print(f"   📏 Distância total: {total_distance:.1f} unidades")
            print(f"   🛣️ Waypoints: {len(path)}")
            
            # Destaca a rota na rede
            network.highlight_path(path)
            
        else:
            print(f"   ❌ Nenhuma rota disponível")

def analyze_network_properties(network, vertiports):
    """Analisa propriedades da rede"""
    print("\n📊 Análise da Rede")
    print("=" * 30)
    
    stats = network.get_network_stats()
    print(f"📍 Vertiportos: {stats['nodes']}")
    print(f"🔗 Conexões: {stats['edges']}")
    print(f"🌐 Densidade: {stats['density']:.3f}")
    print(f"📊 Grau médio: {stats['avg_degree']:.2f}")
    print(f"🔄 Conectada: {'✅' if stats['is_connected'] else '❌'}")
    print(f"➡️ Direcionada: {'✅' if stats['is_directed'] else '❌'}")

def demonstrate_routing_comparison():
    """Compara diferentes tipos de roteamento"""
    print("\n🔄 Comparação de Algoritmos de Roteamento")
    print("=" * 45)
    
    # Cria uma rede simples para comparação
    network = Network(directed=False)
    
    # Grid 3x3 de vertiportos
    grid_vps = {}
    for i in range(3):
        for j in range(3):
            vp = Vertiport(i * 150 + 100, j * 150 + 100, capacity=2)
            network.add_node(vp)
            grid_vps[(i, j)] = vp
    
    # Conecta vizinhos adjacentes
    for i in range(3):
        for j in range(3):
            current = grid_vps[(i, j)]
            # Conecta à direita
            if i < 2:
                network.add_link(current, grid_vps[(i+1, j)])
            # Conecta para baixo
            if j < 2:
                network.add_link(current, grid_vps[(i, j+1)])
    
    # Testa roteamento do canto superior esquerdo ao inferior direito
    origin = grid_vps[(0, 0)]
    destination = grid_vps[(2, 2)]
    
    # Dijkstra (NetworkX)
    path_dijkstra = network.find_shortest_path(origin, destination)
    
    # Calcula distância total do caminho  
    total_distance = 0
    for i in range(len(path_dijkstra) - 1):
        total_distance += network.calculate_distance(path_dijkstra[i], path_dijkstra[i+1])
    
    print(f"🎯 Rota (0,0) → (2,2): {len(path_dijkstra)} pontos, distância: {total_distance:.1f}")

if __name__ == "__main__":
    print("🌐 Demonstração Completa do Sistema de Roteamento NetworkX")
    print("=" * 70)
    
    try:
        # Cria rede de exemplo
        network, vertiports = create_example_network()
        
        # Demonstra roteamento de VTOLs
        demonstrate_vtol_routing(network, vertiports)
        
        # Analisa propriedades da rede
        analyze_network_properties(network, vertiports)
        
        # Compara algoritmos
        demonstrate_routing_comparison()
        
        print("\n🎉 Demonstração concluída!")
        print("\n💡 Como usar na simulação:")
        print("   1. VTOL solicita: path = network.find_shortest_path(origin, destination)")
        print("   2. VTOL segue waypoints: for waypoint in path: ...")
        print("   3. Suporte a links bidirecionais: network.add_link(vp1, vp2, bidirectional=True)")
        print("   4. Suporte a links unidirecionais: network.add_link(vp1, vp2, bidirectional=False)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
