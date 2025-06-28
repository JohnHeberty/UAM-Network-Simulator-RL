"""
Teste específico para verificar se VTOLs pairando tentam pousar quando uma vaga é liberada.
"""
import pygame
import sys
import os

# Define path to data directory
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'data')

# Adiciona o diretório src ao PATH para importar módulos
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from Modules.Simulation.engine import *

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Teste de Hovering Fix - UAM Network Simulator")
    
    # Cria uma simulação simples
    simulation = Simulation(vertiports_json=os.path.join(data_path, "vertiports.json"), vtol_routes_json=os.path.join(data_path, "vtol_routes.json"))
    simulation.evtols = []  # Remove os VTOLs padrão
    
    # Adiciona um vertiport com capacidade limitada (1 slot)
    vertiport = Vertiport(400, 300, capacity=1)
    simulation.network.add_node(vertiport)
    
    # Adiciona 3 VTOLs no mesmo vertiport (forçando hovering)
    vtol1 = VTOL(400, 300, simulation.network)
    vtol1.vtol_id = "VTOL-1"
    vtol1.current_vertiport = vertiport
    vtol1.destination_vertiport = vertiport
    vtol1.state = "landed"
    
    vtol2 = VTOL(450, 250, simulation.network)
    vtol2.vtol_id = "VTOL-2"
    vtol2.destination_vertiport = vertiport
    vtol2.state = "flying"
    
    vtol3 = VTOL(350, 250, simulation.network)
    vtol3.vtol_id = "VTOL-3"
    vtol3.destination_vertiport = vertiport
    vtol3.state = "flying"
    
    # Registra o primeiro VTOL como ocupando o vertiport
    vertiport.land_vtol(vtol1)
    
    simulation.evtols = [vtol1, vtol2, vtol3]
    
    print("🧪 Iniciando teste de hovering fix...")
    print(f"📍 Vertiport capacidade: {vertiport.capacity}")
    print(f"🚁 VTOL-1: {vtol1.state} (ocupando vertiport)")
    print(f"🚁 VTOL-2: {vtol2.state} (tentará pousar)")
    print(f"🚁 VTOL-3: {vtol3.state} (tentará pousar)")
    print("\n⏱️  VTOL-1 decolará automaticamente em alguns segundos...")
    print("✅ Se o fix funcionar, VTOL-2 ou VTOL-3 deverá pousar quando VTOL-1 decolar")
    print("\n🎮 Pressione ESC para sair\n")
    
    # Timer para forçar decolagem do VTOL-1
    decolagem_timer = 300  # 5 segundos a 60 FPS
    
    frame_count = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Força decolagem do VTOL-1 após 5 segundos
        if decolagem_timer > 0:
            decolagem_timer -= 1
            if decolagem_timer == 0:
                print("🛫 Forçando decolagem do VTOL-1...")
                vtol1.set_destination_vertiport(vertiport)  # Ele vai decolar e tentar pousar novamente
        
        # Atualiza simulação
        simulation.update()
        
        # Desenha
        screen.fill((50, 50, 50))
        simulation.draw(screen)
        
        # Informações de debug a cada 60 frames (1 segundo)
        if frame_count % 60 == 0:
            occupancy = vertiport.get_occupancy_info()
            print(f"Frame {frame_count}: Ocupação={occupancy['occupied']}/{occupancy['capacity']}, Pairando={occupancy['hovering_count']}")
            
            for vtol in simulation.evtols:
                if hasattr(vtol, 'vtol_id') and not vtol.clean:
                    hover_flag = getattr(vtol, '_can_attempt_landing', False)
                    print(f"  {vtol.vtol_id}: {vtol.state} (can_attempt_landing: {hover_flag})")
        
        # Verifica se algum VTOL pousou após hover
        if frame_count > 360:  # Após 6 segundos
            hovering_count = len([v for v in simulation.evtols if v.state == "hovering" and not v.clean])
            landed_count = len([v for v in simulation.evtols if v.state == "landed" and not v.clean])
            
            if hovering_count == 0 and landed_count > 0:
                print("✅ SUCESSO! VTOLs conseguiram pousar após hover!")
                print(f"   {landed_count} VTOL(s) pousado(s)")
                
            elif frame_count > 600:  # 10 segundos - timeout
                print("❌ FALHA! VTOLs ainda estão pairando após timeout")
                for vtol in simulation.evtols:
                    if hasattr(vtol, 'vtol_id') and not vtol.clean:
                        print(f"   {vtol.vtol_id}: {vtol.state}")
                break
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    pygame.quit()
    print("🏁 Teste finalizado")

if __name__ == "__main__":
    main()
