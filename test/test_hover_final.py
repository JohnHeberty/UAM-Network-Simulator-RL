"""
Teste final para verificar se VTOLs pairando tentam pousar quando uma vaga é liberada.
Simula situação mais realista com VTOLs que circulam.
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
    pygame.display.set_caption("Teste Final - Hovering Fix UAM Network Simulator")
    
    # Cria simulação usando os JSONs existentes
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'data')
    simulation = Simulation(
        vertiports_json=os.path.join(data_path, "vertiports.json"),
        vtol_routes_json=os.path.join(data_path, "vtol_routes.json")
    )
    
    print("🧪 Teste final de hovering fix")
    print("📍 Carregados vertiportos e rotas dos JSONs")
    print(f"🚁 {len(simulation.evtols)} VTOLs ativos")
    print("\n⏱️  Aguardando VTOLs chegarem nos vertiportos...")
    print("✅ Se o fix funcionar, VTOLs deverão pousar após outros decolarem")
    print("🎮 Pressione ESC para sair\n")
    
    frame_count = 0
    running = True
    last_log_frame = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Atualiza simulação
        simulation.update()
        
        # Desenha
        screen.fill((50, 50, 50))
        simulation.draw(screen)
        
        # Log detalhado a cada 2 segundos
        if frame_count - last_log_frame >= 120:
            last_log_frame = frame_count
            
            print(f"\n⏰ Frame {frame_count} (t={frame_count/60:.1f}s)")
            
            # Status dos vertiportos
            for vertiport_info in simulation.vertiports_list:
                vertiport = vertiport_info['object']
                occupancy = vertiport.get_occupancy_info()
                if occupancy['occupied'] > 0 or occupancy['hovering_count'] > 0:
                    print(f"📍 {vertiport_info['id']}: {occupancy['occupied']}/{occupancy['capacity']} ocupado, {occupancy['hovering_count']} pairando")
            
            # Status dos VTOLs
            hovering_vtols = []
            landed_vtols = []
            for vtol in simulation.evtols:
                if not vtol.clean:
                    if vtol.state == "hovering":
                        hovering_vtols.append(vtol.vtol_id)
                    elif vtol.state == "landed":
                        landed_vtols.append(vtol.vtol_id)
            
            if hovering_vtols:
                print(f"🚁 Pairando: {', '.join(hovering_vtols)}")
            if landed_vtols:
                print(f"🚁 Pousados: {', '.join(landed_vtols)}")
        
        # Verifica se houve transições de hover para land (sucesso)
        successful_landings = []
        for vtol in simulation.evtols:
            if (not vtol.clean and vtol.state == "landed" and 
                hasattr(vtol, '_was_hovering') and vtol._was_hovering):
                successful_landings.append(vtol.vtol_id)
                vtol._was_hovering = False  # Reset flag
        
        if successful_landings:
            print(f"✅ SUCESSO! VTOLs que pousaram após hover: {', '.join(successful_landings)}")
        
        # Marca VTOLs que estão pairando
        for vtol in simulation.evtols:
            if not vtol.clean:
                if vtol.state == "hovering":
                    vtol._was_hovering = True
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
        
        # Para após 20 segundos
        if frame_count > 1200:
            print("\n🏁 Teste finalizado após 20 segundos")
            break
    
    pygame.quit()
    print("🏁 Teste concluído")

if __name__ == "__main__":
    main()
