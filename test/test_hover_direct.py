"""
Teste mais direto para verificar se VTOLs pairando tentam pousar quando uma vaga é liberada.
"""
import pygame
import sys
import os

# Adiciona o diretório src ao PATH para importar módulos
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from Modules.Simulation.engine import *

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Teste Direto de Hovering Fix")
    
    # Cria vertiports
    vertiport1 = Vertiport(300, 300, capacity=1)
    vertiport2 = Vertiport(500, 300, capacity=2)
    
    # Cria rede
    network = Network()
    network.add_node(vertiport1)
    network.add_node(vertiport2)
    network.add_link(vertiport1, vertiport2)
    
    # Cria VTOLs
    vtol1 = VTOL(300, 300, network)
    vtol1.vtol_id = "VTOL-1"
    vtol1.state = "landed"
    vtol1.current_vertiport = vertiport1
    
    vtol2 = VTOL(320, 280, network)
    vtol2.vtol_id = "VTOL-2"
    vtol2.state = "flying"
    vtol2.destination_vertiport = vertiport1
    
    # VTOL-1 ocupa o vertiport
    vertiport1.land_vtol(vtol1)
    
    print("🧪 Teste direto de hovering fix")
    print(f"📍 Vertiport1 capacidade: {vertiport1.capacity}")
    print(f"🚁 VTOL-1: {vtol1.state} (ocupando vertiport1)")
    print(f"🚁 VTOL-2: {vtol2.state} (tentará pousar em vertiport1)")
    print()
    
    frame_count = 0
    running = True
    
    while running and frame_count < 600:  # 10 segundos máximo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Força liberação manual do vertiport
                    print("⚡ FORÇA: Liberando vertiport manualmente...")
                    vertiport1.takeoff_vtol(vtol1)
                    vtol1.current_vertiport = None
                    vtol1.state = "flying"
                    vtol1.destination_vertiport = vertiport2
        
        # Força liberação automática após 3 segundos
        if frame_count == 180:  # 3 segundos
            print("⏰ AUTO: Liberando vertiport automaticamente...")
            vertiport1.takeoff_vtol(vtol1)
            vtol1.current_vertiport = None
            vtol1.state = "flying"
            vtol1.destination_vertiport = vertiport2
        
        # Atualiza VTOLs
        vtol1.update()
        vtol2.update()
        
        # Debug a cada segundo
        if frame_count % 60 == 0:
            occupancy = vertiport1.get_occupancy_info()
            print(f"Frame {frame_count}: Vertiport1 = {occupancy['occupied']}/{occupancy['capacity']}, Pairando={occupancy['hovering_count']}")
            print(f"  VTOL-1: {vtol1.state}")
            print(f"  VTOL-2: {vtol2.state} (can_attempt_landing: {getattr(vtol2, '_can_attempt_landing', 'N/A')})")
            
            # Verifica se VTOL-2 conseguiu pousar
            if vtol2.state == "landed" and frame_count > 240:
                print("✅ SUCESSO! VTOL-2 conseguiu pousar após VTOL-1 decolar!")
                break
        
        # Desenha
        screen.fill((50, 50, 50))
        vertiport1.draw(screen)
        vertiport2.draw(screen)
        vtol1.draw(screen)
        vtol2.draw(screen)
        
        # Informações na tela
        if pygame.font.get_init():
            font = pygame.font.Font(None, 24)
            text1 = font.render(f"VTOL-1: {vtol1.state}", True, (255, 255, 255))
            text2 = font.render(f"VTOL-2: {vtol2.state}", True, (255, 255, 255))
            text3 = font.render("Pressione SPACE para forçar liberação", True, (255, 255, 0))
            screen.blit(text1, (10, 10))
            screen.blit(text2, (10, 35))
            screen.blit(text3, (10, 550))
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    # Resultado final
    if vtol2.state == "landed":
        print("✅ TESTE PASSOU! VTOL conseguiu pousar após liberação da vaga")
    else:
        print("❌ TESTE FALHOU! VTOL não conseguiu pousar")
        print(f"   VTOL-2 estado final: {vtol2.state}")
    
    pygame.quit()

if __name__ == "__main__":
    main()
