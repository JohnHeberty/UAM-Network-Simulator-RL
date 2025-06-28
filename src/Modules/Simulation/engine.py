from typing import List, Tuple, Union, Optional
import os
import csv
import json
import sys
import math
import random
import pygame
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

# Constantes
WIDTH, HEIGHT = 1000, 800
FPS = 60
EVTOL_COLOR = (100, 200, 255)
PERSON_COLOR = (255, 100, 100)
VERTIPORT_COLOR = (180, 180, 180)
VERTIPORT_BORDER_COLOR = (220, 220, 220)
NETWORK_LINK_COLOR = (150, 150, 255)  # Azul claro para links
NETWORK_LINK_HIGHLIGHT_COLOR = (255, 255, 100)  # Amarelo para destaque

# Configuração de tamanhos de desenho (globais para fácil customização)
PERSON_DRAW_SIZE = 3          # Raio do círculo para pessoas
VTOL_DRAW_SIZE = 16           # Largura base para VTOLs

# --- Interfaces seguindo princípios SOLID ---

# SRP - Cada interface tem uma única responsabilidade
class Drawable(ABC):
    """Interface para objetos que podem ser desenhados na tela"""
    @abstractmethod
    def draw(self, surface):
        pass

# Interfaces seguindo o Princípio da Segregação de Interfaces (ISP)
class Movable(ABC):
    """Interface para objetos que podem se mover"""
    @abstractmethod
    def update_position(self) -> None:
        """Atualiza a posição do objeto"""
        pass

class Updatable(ABC):
    """Interface para objetos que podem ser atualizados"""
    @abstractmethod
    def update(self) -> None:
        """Atualiza o estado do objeto"""
        pass

class Stateful(ABC):
    """Interface para objetos que têm estado"""
    @abstractmethod
    def get_state(self) -> str:
        """Retorna o estado atual"""
        pass
    
    @abstractmethod
    def set_state(self, state: str) -> None:
        """Define o estado"""
        pass

# Interface específica para planejamento de rotas
class PathPlanner(ABC):
    """Interface para estratégias de planejamento de rotas"""
    @abstractmethod
    def plan_route(self, origin: Tuple[int, int], destination: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Planeja uma rota entre origem e destino, retorna lista de pontos"""
        pass
    
    @abstractmethod
    def get_next_point(self, current_pos: Tuple[int, int], target_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Retorna o próximo ponto em direção ao alvo"""
        pass

# Interface para objetos que podem ser removidos
class Cleanable(ABC):
    """Interface para objetos que podem ser marcados para remoção"""
    @abstractmethod
    def mark_for_cleanup(self) -> None:
        """Marca para remoção"""
        pass
    
    @abstractmethod
    def is_clean(self) -> bool:
        """Verifica se está marcado para remoção"""
        pass

# Interface para gestão de rede
class NetworkManager(ABC):
    """Interface para gestão de redes de transporte"""
    @abstractmethod
    def add_node(self, node) -> bool:
        """Adiciona um nó à rede"""
        pass
    
    @abstractmethod
    def remove_node(self, node) -> bool:
        """Remove um nó da rede"""
        pass
    
    @abstractmethod
    def find_path(self, start, end) -> List:
        """Encontra um caminho entre dois nós"""
        pass

# Implementação concreta do planejador de rotas
class StraightLinePathPlanner(PathPlanner):
    """Planejador de rota em linha reta"""
    def __init__(self, step=1):
        self.step = step

    def plan_route(self, origin, destination):
        """Planeja uma rota simples de origem a destino"""
        return [origin, destination]
    
    def get_next_point(self, current_pos, target_pos):
        """Calcula o próximo ponto em direção ao alvo"""
        ox, oy = current_pos
        dx, dy = target_pos
        vx, vy = dx - ox, dy - oy
        dist = (vx ** 2 + vy ** 2) ** 0.5
        if dist == 0 or dist < self.step:
            return target_pos
        nx = ox + self.step * vx / dist
        ny = oy + self.step * vy / dist
        return int(nx), int(ny)

# --- Princípio da Responsabilidade Única (SRP) ---
# --- Implementação de entidades seguindo SRP ---
class Person(Drawable, Movable, Cleanable):
    """Representa uma pessoa na simulação - responsabilidade única: gerenciar estado e movimento de uma pessoa"""
    def __init__(self, x: int, y: int):
        self.xo = x  # origem
        self.xd = self.xo  # destino
        self.bxo = self.xo  # posição anterior
        self.yo = y  # origem
        self.yd = self.yo  # destino
        self.byo = self.yo  # posição anterior
        self.path_planner = StraightLinePathPlanner()
        self.clean = False

    def set_destination(self, xd: int, yd: int) -> None:
        """Define o destino da pessoa"""
        if (self.xd, self.yd) == (self.xo, self.yo):
            self.xd = xd
            self.yd = yd

    def update_position(self) -> None:
        """Atualiza a posição da pessoa em direção ao destino"""
        # Salva a posição anterior antes de atualizar
        self.bxo, self.byo = self.xo, self.yo
        self.xo, self.yo = self.path_planner.get_next_point((self.xo, self.yo), (self.xd, self.yd))
        
        # Verifica se chegou ao destino ou se parou de se mover
        if (self.xo, self.yo) == (self.xd, self.yd) or (self.bxo, self.byo) == (self.xo, self.yo):
            self.mark_for_cleanup()

    def update(self) -> None:
        """Atualiza o estado da pessoa"""
        if not self.clean:
            self.update_position()

    def mark_for_cleanup(self) -> None:
        """Marca a pessoa para remoção"""
        self.clean = True

    def is_clean(self) -> bool:
        """Retorna se a pessoa deve ser removida"""
        return self.clean

    def draw(self, surface) -> None:
        """Desenha a pessoa na tela"""
        if not self.clean:
            self.update_position()
            pygame.draw.circle(surface, PERSON_COLOR, (self.xo, self.yo), PERSON_DRAW_SIZE)

# --- Classe VTOL seguindo princípios SOLID ---
class VTOL(Drawable, Movable, Stateful, Cleanable):
    """
    VTOL (Vertical Take-Off and Landing) aircraft que navega pela rede de vertiportos.
    Responsabilidade única: gerenciar estado, movimento e comportamento de um VTOL.
    Aberto para extensão, fechado para modificação (OCP).
    """
    def __init__(self, x, y, network=None):
        # Posição atual
        self.xo = x
        self.yo = y
        self.bxo = self.xo  # posição anterior
        self.byo = self.yo  # posição anterior
        
        # Destino e navegação
        self.destination_vertiport = None  # Vertiport de destino
        self.current_vertiport = None  # Vertiport atual (se pousado)
        self.flight_path = []  # Caminho de vertiportos a seguir
        self.current_path_index = 0  # Índice atual no caminho
        self.intermediate_target = None  # Próximo ponto no segmento atual
        
        # Referência à rede
        self.network = network
        
        # Estado de limpeza
        self.clean = False
        
        # Propriedades para circulação constante
        self.is_circulating = False  # Se é um VTOL que circula constantemente
        self.vtol_id = "VTOL"  # ID personalizado
        
        # Propriedades para rotas personalizadas
        self.custom_route = []  # Lista de IDs de vertiportos na rota personalizada
        self.current_route_index = 0  # Índice atual na rota personalizada
        self.loop_route = True  # Se deve fazer loop na rota ou parar no final
        self.vertiports_map = {}  # Mapeamento de IDs para objetos Vertiport
        self._next_destination = None  # Próximo destino agendado para circulação
        
        # Estados do VTOL
        self.state = "landed"  # landed, taking_off, flying, landing, hovering, in_transit
        self.before_state = self.state
        self.state_timer = 0  # Timer para transições de estado
        
        # Propriedades visuais e animação
        self.base_width = VTOL_DRAW_SIZE
        self.base_scale = 1
        self.atual_scale = 0.4  # Começa pequeno (pousado)
        self.scale_animation = False
        self.scale_target = 0.4
        self.scale_speed = 0.02
        
        # Propriedades de movimento
        self.speed = 4  # Velocidade de movimento aumentada para simulação mais rápida
        self.path_planner = StraightLinePathPlanner(step=self.speed)
        
        # Cores dinâmicas baseadas no estado
        self.colors = {
            "landed": (80, 150, 200),      # Azul escuro
            "taking_off": (120, 180, 255), # Azul médio
            "flying": (100, 200, 255),     # Azul claro (original)
            "landing": (120, 180, 255),    # Azul médio
            "hovering": (255, 255, 100),   # Amarelo (esperando para pousar)
            "in_transit": (150, 220, 255)  # Azul muito claro
        }
        
        # Propriedades para controle de capacidade
        self._can_attempt_landing = True  # Flag para tentar pousar novamente
        self._hover_position = None       # Posição para pairar sobre vertiport
    
    def _set_next_circulation_destination(self):
        """Define o próximo destino para VTOLs circulantes."""
        if not self.network or not self.current_vertiport:
            return False
        
        # Se tem rota personalizada, usa ela
        if hasattr(self, 'custom_route') and self.custom_route:
            return self._set_next_custom_route_destination()
        
        # Fallback para lógica circular padrão
        return self._set_next_circular_destination()
    
    def _set_next_custom_route_destination(self):
        """Define próximo destino baseado na rota personalizada, suportando ida-e-volta."""
        if not self.custom_route or len(self.custom_route) < 2:
            return False

        # Detecta se a rota é circular (primeiro == último)
        is_circular = self.custom_route[0] == self.custom_route[-1]
        if not hasattr(self, 'reverse_route'):
            self.reverse_route = False  # Flag para ida-e-volta

        # Determina direção
        if is_circular:
            # Comportamento circular padrão
            next_index = (self.current_route_index + 1) % len(self.custom_route)
        else:
            # Ida-e-volta: avança ou retrocede
            if not self.reverse_route:
                next_index = self.current_route_index + 1
                if next_index >= len(self.custom_route):
                    # Chegou ao fim, inverte direção
                    self.reverse_route = True
                    next_index = self.current_route_index - 1
            else:
                next_index = self.current_route_index - 1
                if next_index < 0:
                    # Chegou ao início, inverte direção
                    self.reverse_route = False
                    next_index = self.current_route_index + 1

        # Protege contra índices inválidos
        if next_index < 0 or next_index >= len(self.custom_route):
            print(f"🏁 {self.vtol_id} completou rota ida-e-volta e será removido")
            self.is_circulating = False
            return False

        next_vp_id = self.custom_route[next_index]
        if hasattr(self, 'vertiports_map') and next_vp_id in self.vertiports_map:
            next_vertiport = self.vertiports_map[next_vp_id]
            print(f"🔄 {self.vtol_id} seguindo rota personalizada para {next_vp_id}... (ida-e-volta: {not is_circular}, reverse: {self.reverse_route})")
            self.state_timer = 15
            self._next_destination = next_vertiport
            return True
        return False
    
    def _set_next_circular_destination(self):
        """Define próximo destino usando lógica circular padrão."""
        if not self.network:
            return False
            
        # Encontra o próximo vertiport na sequência circular
        current_index = None
        nodes_list = list(self.network.nodes)
        
        # Encontra o índice do vertiport atual
        for i, node in enumerate(nodes_list):
            if node == self.current_vertiport:
                current_index = i
                break
        
        if current_index is not None:
            # Próximo vertiport na sequência (circular)
            next_index = (current_index + 1) % len(nodes_list)
            next_vertiport = nodes_list[next_index]
            
            # Define novo destino após um pequeno delay
            if hasattr(self, 'vtol_id'):
                print(f"🔄 {self.vtol_id} circulando para próximo vertiport...")
            
            # Pequeno delay antes de definir novo destino (simula parada no vertiport)
            self.state_timer = 15  # 0.25 segundos a 60 FPS (reduzido para simulação mais rápida)
            
            # Agenda próximo destino
            self._next_destination = next_vertiport
            return True
        
        return False
    
    def find_nearest_vertiport(self):
        """Encontra o vertiport mais próximo da posição atual"""
        if not self.network or not self.network.nodes:
            return None
        
        min_distance = float('inf')
        nearest_vertiport = None
        
        for vertiport in self.network.nodes:
            center_x = vertiport.x + 30  # Centro do vertiport (60x60, centro em +30)
            center_y = vertiport.y + 30
            distance = ((self.xo - center_x)**2 + (self.yo - center_y)**2)**0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest_vertiport = vertiport
        
        return nearest_vertiport
    
    def set_destination_vertiport(self, destination_vertiport):
        """Define o vertiport de destino e calcula a rota"""
        if not self.network or destination_vertiport not in self.network.nodes:
            return False
        
        # Se não tem vertiport atual, encontra o mais próximo
        if not self.current_vertiport:
            self.current_vertiport = self.find_nearest_vertiport()
        
        if not self.current_vertiport:
            return False
        
        # Calcula o caminho na rede
        self.flight_path = self.network.find_shortest_path(
            self.current_vertiport, 
            destination_vertiport
        )
        
        if not self.flight_path:
            return False
        
        self.destination_vertiport = destination_vertiport
        self.current_path_index = 0
        
        # Se já está no destino
        if len(self.flight_path) == 1:
            return True
        
        # Inicia o voo
        self._start_takeoff()
        return True
    
    def _start_takeoff(self):
        """Inicia a sequência de decolagem"""
        if self.state == "landed":
            # Notifica o vertiport sobre a decolagem
            if self.current_vertiport and hasattr(self.current_vertiport, 'takeoff_vtol'):
                self.current_vertiport.takeoff_vtol(self)
            
            self.state = "taking_off"
            self.state_timer = 30  # 0.5 segundos a 60 FPS (reduzido para simulação mais rápida)
            self.scale_target = 1.0
            self.scale_animation = True
            self.current_vertiport = None  # Não está mais pousado
    
    def _start_landing(self):
        """Inicia a sequência de pouso ou pairar se não há vaga"""
        if self.state in ["flying", "in_transit"]:
            # Verifica se o vertiport de destino tem capacidade
            if self.destination_vertiport and hasattr(self.destination_vertiport, 'request_landing'):
                if self.destination_vertiport.request_landing(self):
                    # Há vaga disponível - pode pousar
                    self.state = "landing"
                    self.state_timer = 30  # 0.5 segundos a 60 FPS
                    self.scale_target = 0.4
                    self.scale_animation = True
                else:
                    # Sem vaga - deve pairar
                    self._start_hovering()
            else:
                # Fallback para comportamento antigo se vertiport não tem controle de capacidade
                self.state = "landing"
                self.state_timer = 30
                self.scale_target = 0.4
                self.scale_animation = True
    
    def _start_hovering(self):
        """Inicia o estado de pairar sobre o vertiport"""
        self.state = "hovering"
        self.state_timer = 60  # Tenta novamente em 1 segundo
        # Define posição de pairar acima do vertiport
        if self.destination_vertiport:
            self._hover_position = (
                self.destination_vertiport.x + 30,  # Centro X do vertiport
                self.destination_vertiport.y + 10   # Um pouco acima do vertiport
            )
        self._can_attempt_landing = False
    
    def _update_scale_animation(self):
        """Atualiza a animação de escala"""
        if self.scale_animation:
            if abs(self.atual_scale - self.scale_target) > 0.01:
                if self.atual_scale < self.scale_target:
                    self.atual_scale += self.scale_speed
                else:
                    self.atual_scale -= self.scale_speed
            else:
                self.atual_scale = self.scale_target
                self.scale_animation = False
    
    def _get_next_waypoint(self):
        """Obtém o próximo waypoint no caminho"""
        if (self.current_path_index < len(self.flight_path) - 1):
            self.current_path_index += 1
            next_vertiport = self.flight_path[self.current_path_index]
            return (next_vertiport.x + 30, next_vertiport.y + 30)  # Centro do vertiport
        return None
    
    def _update_movement(self):
        """Atualiza o movimento do VTOL"""
        if self.state in ["flying", "in_transit"]:
            if not self.intermediate_target:
                # Precisa de um novo waypoint
                waypoint = self._get_next_waypoint()
                if waypoint:
                    self.intermediate_target = waypoint
                else:
                    # Chegou ao destino final
                    self._start_landing()
                    return
            
            # Move em direção ao waypoint atual
            self.bxo, self.byo = self.xo, self.yo
            new_pos = self.path_planner.get_next_point(
                (self.xo, self.yo), 
                self.intermediate_target
            )
            self.xo, self.yo = new_pos
            
            # Verifica se chegou ao waypoint
            distance_to_target = ((self.xo - self.intermediate_target[0])**2 + 
                                (self.yo - self.intermediate_target[1])**2)**0.5
            
            if distance_to_target < 8:  # Aumentado de 5 para 8 para detecção mais robusta
                self.intermediate_target = None
                
                # Se chegou ao destino final
                if self.current_path_index >= len(self.flight_path) - 1:
                    self._start_landing()
    
    def update(self):
        """Atualiza o estado e movimento do VTOL"""
        # Atualiza timer de estado
        if self.state_timer > 0:
            self.state_timer -= 1
        
        # Máquina de estados
        if self.state == "taking_off":
            if self.state_timer <= 0:
                self.state = "flying"
                # Define o primeiro waypoint
                if len(self.flight_path) > 1:
                    next_vertiport = self.flight_path[1]
                    self.intermediate_target = (next_vertiport.x + 30, next_vertiport.y + 30)
                    self.current_path_index = 0
        
        elif self.state == "landing":
            if self.state_timer <= 0:
                # Tenta efetuar o pouso registrando no vertiport
                if self.destination_vertiport and hasattr(self.destination_vertiport, 'land_vtol'):
                    if self.destination_vertiport.land_vtol(self):
                        # Pouso bem-sucedido
                        self.state = "landed"
                        # Posiciona no centro do vertiport de destino
                        self.xo = self.destination_vertiport.x + 30
                        self.yo = self.destination_vertiport.y + 30
                        self.current_vertiport = self.destination_vertiport
                    else:
                        # Não conseguiu pousar - volta a pairar
                        self._start_hovering()
                        return
                else:
                    # Fallback para comportamento antigo
                    self.state = "landed"
                    if self.destination_vertiport:
                        self.xo = self.destination_vertiport.x + 30
                        self.yo = self.destination_vertiport.y + 30
                        self.current_vertiport = self.destination_vertiport
                
                # Verifica se chegou ao destino final
                if (self.current_vertiport and 
                    self.destination_vertiport and 
                    self.current_vertiport == self.destination_vertiport):
                    
                    # Se é um VTOL circulante, define próximo destino automaticamente
                    if hasattr(self, 'is_circulating') and self.is_circulating:
                        self._set_next_circulation_destination()
                    else:
                        # VTOLs normais se marcam como clean
                        self.clean = True

        elif self.state == "hovering":
            # Move para posição de pairar se definida
            if self._hover_position:
                self.bxo, self.byo = self.xo, self.yo
                new_pos = self.path_planner.get_next_point(
                    (self.xo, self.yo), 
                    self._hover_position
                )
                self.xo, self.yo = new_pos
            
            # Verifica periodicamente se pode tentar pousar novamente
            if self.state_timer <= 0:
                if (self._can_attempt_landing or 
                    (self.destination_vertiport and 
                     hasattr(self.destination_vertiport, 'can_land') and 
                     self.destination_vertiport.can_land(self))):
                    # Tenta pousar novamente
                    self._start_landing()
                else:
                    # Continua pairando - reseta o timer
                    self.state_timer = 60  # Tenta novamente em 1 segundo
        
        elif self.state == "landed":
            # Se é um VTOL circulante, verifica se precisa agendar próximo destino
            if (hasattr(self, 'is_circulating') and self.is_circulating and self.state_timer <= 0):
                # Se já tem próximo destino agendado, decola para ele
                if hasattr(self, '_next_destination'):
                    next_dest = self._next_destination
                    delattr(self, '_next_destination')  # Remove a agenda
                    
                    # Define novo destino
                    if self.set_destination_vertiport(next_dest):
                        # Atualiza o índice da rota para o novo destino
                        if hasattr(self, 'custom_route') and self.custom_route:
                            for i, vp_id in enumerate(self.custom_route):
                                if (hasattr(self, 'vertiports_map') and 
                                    vp_id in self.vertiports_map and 
                                    self.vertiports_map[vp_id] == next_dest):
                                    self.current_route_index = i
                                    break
                    if hasattr(self, 'vtol_id'):
                        print(f"🛫 {self.vtol_id} decolando para próximo destino (índice: {self.current_route_index})")
                
                # Se não tem próximo destino agendado, agenda um novo
                else:
                    self._set_next_circulation_destination()
        
        elif self.state in ["flying", "in_transit"]:
            self._update_movement()
        
        # Atualiza animação de escala
        self._update_scale_animation()
    
    def get_current_color(self):
        """Retorna a cor baseada no estado atual"""
        return self.colors.get(self.state, self.colors["flying"])
    
    def draw(self, surface):
        """Desenha o VTOL com visual melhorado"""
        # Atualiza estado e movimento
        self.update()
        
        # Calcula tamanho baseado na escala
        size = int(self.base_width * self.atual_scale)
        color = self.get_current_color()
        
        # Desenha o corpo principal do VTOL
        main_rect = pygame.Rect(
            self.xo - size//2, 
            self.yo - int(size * 0.75)//2, 
            size, 
            int(size * 0.75)
        )
        pygame.draw.rect(surface, color, main_rect)
        
        # Adiciona detalhes visuais baseados no estado
        if self.state in ["flying", "in_transit"]:
            # Desenha "rotores" girando
            rotor_color = (200, 200, 200, 128)  # Cinza translúcido
            rotor_size = size + 2
            
            # Rotores nas laterais
            pygame.draw.circle(surface, rotor_color, 
                             (self.xo - size//2, self.yo), rotor_size//3, 1)
            pygame.draw.circle(surface, rotor_color, 
                             (self.xo + size//2, self.yo), rotor_size//3, 1)
        
        elif self.state == "taking_off":
            # Efeito de decolagem
            pygame.draw.circle(surface, (255, 255, 255, 64), 
                             (self.xo, self.yo + size//2), size//2, 1)
        
        elif self.state == "landing":
            # Efeito de pouso
            pygame.draw.circle(surface, (255, 255, 100, 64), 
                             (self.xo, self.yo + size//2), size//2, 1)
        
        elif self.state == "hovering":
            # Efeito de pairar - círculos piscando
            hover_alpha = 64 + int(32 * math.sin(pygame.time.get_ticks() * 0.01))
            hover_color = (255, 255, 0, hover_alpha)
            pygame.draw.circle(surface, hover_color[:3], 
                             (self.xo, self.yo), size//2 + 3, 2)
            # Rotores girando mais devagar
            rotor_color = (255, 255, 100, 96)
            pygame.draw.circle(surface, rotor_color[:3], 
                             (self.xo - size//2, self.yo), size//3, 1)
            pygame.draw.circle(surface, rotor_color[:3], 
                             (self.xo + size//2, self.yo), size//3, 1)
        
        # Desenha indicador de destino se estiver voando
        if self.destination_vertiport and self.state in ["flying", "in_transit", "taking_off", "hovering"]:
            dest_x = self.destination_vertiport.x + 30
            dest_y = self.destination_vertiport.y + 30
            line_color = (255, 255, 0, 128) if self.state == "hovering" else (255, 255, 0, 128)
            pygame.draw.line(surface, line_color[:3], 
                           (self.xo, self.yo), (dest_x, dest_y), 1)
    
    def get_state_info(self):
        """Retorna informações detalhadas sobre o estado do VTOL"""
        return {
            "state": self.state,
            "position": (self.xo, self.yo),
            "current_vertiport": self.current_vertiport,
            "destination_vertiport": self.destination_vertiport,
            "flight_path_length": len(self.flight_path) if self.flight_path else 0,
            "path_progress": f"{self.current_path_index}/{len(self.flight_path)-1}" if self.flight_path else "0/0",
            "scale": round(self.atual_scale, 2)
        }
    
    # Implementação das interfaces SOLID
    def get_state(self) -> str:
        """Implementação da interface Stateful"""
        return self.state
    
    def set_state(self, state: str) -> None:
        """Implementação da interface Stateful"""
        self.before_state = self.state
        self.state = state
        
    def update_position(self) -> None:
        """Implementação da interface Movable"""
        self._update_movement()
    
    def mark_for_cleanup(self) -> None:
        """Implementação da interface Cleanable"""
        self.clean = True
    
    def is_clean(self) -> bool:
        """Implementação da interface Cleanable"""
        return self.clean

# --- Princípio da Segregação de Interfaces (ISP) ---
class Vertiport(Drawable):
    def __init__(self, x, y, capacity=2):
        self.x = x
        self.y = y
        self.capacity = capacity
        self.occupied_slots = []  # Lista de VTOLs atualmente pousados
        self.hovering_queue = []  # Fila de VTOLs esperando para pousar

    def can_land(self, vtol):
        """Verifica se há vaga disponível para pouso"""
        return len(self.occupied_slots) < self.capacity

    def request_landing(self, vtol):
        """Solicita permissão para pouso - retorna True se pode pousar, False se deve ficar pairando"""
        if self.can_land(vtol):
            return True
        else:
            # Adiciona à fila de espera se não estiver já
            if vtol not in self.hovering_queue:
                self.hovering_queue.append(vtol)
            return False

    def land_vtol(self, vtol):
        """Executa o pouso do VTOL no vertiport"""
        if self.can_land(vtol):
            self.occupied_slots.append(vtol)
            # Remove da fila de espera se estava lá
            if vtol in self.hovering_queue:
                self.hovering_queue.remove(vtol)
            return True
        return False

    def takeoff_vtol(self, vtol):
        """Remove VTOL do vertiport (decolagem)"""
        if vtol in self.occupied_slots:
            self.occupied_slots.remove(vtol)
            # Verifica se há VTOLs esperando na fila
            if self.hovering_queue:
                next_vtol = self.hovering_queue[0]
                # Notifica o próximo VTOL que pode tentar pousar
                if hasattr(next_vtol, '_can_attempt_landing'):
                    next_vtol._can_attempt_landing = True
            return True
        return False

    def get_occupancy_info(self):
        """Retorna informações sobre ocupação do vertiport"""
        return {
            'capacity': self.capacity,
            'occupied': len(self.occupied_slots),
            'available': self.capacity - len(self.occupied_slots),
            'hovering_count': len(self.hovering_queue),
            'occupancy_rate': len(self.occupied_slots) / self.capacity if self.capacity > 0 else 0
        }

    def draw(self, surface):
        # Desenha o vertiport com borda mais visível
        pygame.draw.rect(surface, VERTIPORT_COLOR, (self.x, self.y, 60, 60))
        pygame.draw.rect(surface, VERTIPORT_BORDER_COLOR, (self.x, self.y, 60, 60), 3)
        
        # Indica ocupação visualmente
        occupancy = self.get_occupancy_info()
        if occupancy['occupied'] > 0:
            # Desenha indicador de ocupação
            fill_height = int(60 * occupancy['occupancy_rate'])
            fill_rect = pygame.Rect(self.x + 2, self.y + 60 - fill_height - 2, 56, fill_height)
            overlay_color = (255, 200, 100, 128) if occupancy['occupied'] < self.capacity else (255, 100, 100, 128)
            pygame.draw.rect(surface, overlay_color[:3], fill_rect)
        
        # Mostra VTOLs pairando se houver
        if len(self.hovering_queue) > 0:
            # Desenha indicador de VTOLs pairando
            hover_indicator = pygame.Rect(self.x + 50, self.y - 10, 15, 8)
            pygame.draw.rect(surface, (255, 255, 0), hover_indicator)
            # Número de VTOLs pairando
            if hasattr(pygame, 'font') and pygame.font.get_init():
                font = pygame.font.Font(None, 12)
                text = font.render(str(len(self.hovering_queue)), True, (0, 0, 0))
                surface.blit(text, (self.x + 52, self.y - 8))

# --- Classe para gerenciar a rede de vertiportos e conexões seguindo SOLID ---
class Network(Drawable, NetworkManager):
    """
    Gerencia a rede de vertiportos e suas conexões.
    Responsabilidade única: administrar a topologia da rede de transporte.
    """
    def __init__(self):
        self.nodes = set()  # Set para operações O(1) de busca
        self.adjacency_list = {}  # Dicionário para lista de adjacência (melhor performance)
        self.link_color = NETWORK_LINK_COLOR  # Cor das conexões (azul claro)
        self.link_highlight_color = NETWORK_LINK_HIGHLIGHT_COLOR  # Cor de destaque
        self.link_width = 3  # Espessura das linhas de conexão (aumentada)
        self.show_distance_labels = False  # Flag para mostrar distâncias nos links
        self.vertiport_size = 60  # Tamanho padrão dos vertiportos
        self.highlighted_path = []  # Caminho destacado na visualização
        
    def add_node(self, node):
        """Adiciona um vertiport como nó da rede"""
        if node is None:
            raise ValueError("Vertiport não pode ser None")
        
        if node not in self.nodes:
            self.nodes.add(node)
            self.adjacency_list[node] = set()
            return True
        return False
    
    def remove_node(self, node):
        """Remove um vertiport da rede e todas suas conexões"""
        if node not in self.nodes:
            return False
            
        # Remove todas as conexões com este vertiport
        for connected_node in list(self.adjacency_list[node]):
            self.remove_link(node, connected_node)
        
        # Remove o nó
        self.nodes.remove(node)
        del self.adjacency_list[node]
        return True
    
    def find_path(self, start, end):
        """Implementação da interface NetworkManager - encontra caminho entre nós"""
        return self.find_shortest_path(start, end)
    
    def add_link(self, vertiport1, vertiport2):
        """Adiciona uma conexão bidirecional entre dois vertiportos"""
        if vertiport1 is None or vertiport2 is None:
            raise ValueError("Vertiports não podem ser None")
        
        if vertiport1 == vertiport2:
            return False  # Não permite self-loops
            
        if vertiport1 not in self.nodes or vertiport2 not in self.nodes:
            return False
        
        # Adiciona conexão bidirecional
        self.adjacency_list[vertiport1].add(vertiport2)
        self.adjacency_list[vertiport2].add(vertiport1)
        return True
    
    def remove_link(self, vertiport1, vertiport2):
        """Remove a conexão entre dois vertiportos"""
        if vertiport1 not in self.nodes or vertiport2 not in self.nodes:
            return False
            
        # Remove conexão bidirecional
        self.adjacency_list[vertiport1].discard(vertiport2)
        self.adjacency_list[vertiport2].discard(vertiport1)
        return True
    
    def get_connected_vertiports(self, vertiport):
        """Retorna lista de vertiportos conectados a um vertiport específico"""
        if vertiport not in self.nodes:
            return []
        return list(self.adjacency_list[vertiport])
    
    def calculate_distance(self, vertiport1, vertiport2):
        """Calcula a distância euclidiana entre dois vertiportos"""
        return ((vertiport1.x - vertiport2.x)**2 + (vertiport1.y - vertiport2.y)**2)**0.5
    
    def auto_connect_nearby(self, max_distance=200):
        """Conecta automaticamente vertiportos próximos dentro de uma distância máxima"""
        nodes_list = list(self.nodes)
        connections_made = 0
        
        for i, node1 in enumerate(nodes_list):
            for node2 in nodes_list[i+1:]:
                if node2 not in self.adjacency_list[node1]:  # Se não estão conectados
                    distance = self.calculate_distance(node1, node2)
                    if distance <= max_distance:
                        if self.add_link(node1, node2):
                            connections_made += 1
        
        return connections_made
    
    def find_shortest_path(self, start_vertiport, end_vertiport):
        """Encontra o caminho mais curto entre dois vertiportos usando BFS"""
        if start_vertiport not in self.nodes or end_vertiport not in self.nodes:
            return []
        
        if start_vertiport == end_vertiport:
            return [start_vertiport]
        
        queue = [(start_vertiport, [start_vertiport])]
        visited = {start_vertiport}
        
        while queue:
            current_node, path = queue.pop(0)
            
            for neighbor in self.adjacency_list[current_node]:
                if neighbor == end_vertiport:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # Nenhum caminho encontrado
    
    def get_network_stats(self):
        """Retorna estatísticas da rede"""
        total_nodes = len(self.nodes)
        total_edges = sum(len(connections) for connections in self.adjacency_list.values()) // 2
        
        if total_nodes == 0:
            return {
                "nodes": 0,
                "edges": 0,
                "density": 0,
                "avg_degree": 0
            }
        
        max_possible_edges = total_nodes * (total_nodes - 1) // 2
        density = total_edges / max_possible_edges if max_possible_edges > 0 else 0
        avg_degree = (total_edges * 2) / total_nodes if total_nodes > 0 else 0
        
        return {
            "nodes": total_nodes,
            "edges": total_edges,
            "density": round(density, 3),
            "avg_degree": round(avg_degree, 2)
        }
    
    def is_connected(self):
        """Verifica se a rede é conectada (todos os nós são alcançáveis)"""
        if len(self.nodes) <= 1:
            return True
        
        start_node = next(iter(self.nodes))
        visited = set()
        queue = [start_node]
        
        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.add(current)
                queue.extend(self.adjacency_list[current] - visited)
        
        return len(visited) == len(self.nodes)
    
    def get_center_position(self, vertiport):
        """Retorna a posição central de um vertiport"""
        return (vertiport.x + self.vertiport_size // 2, vertiport.y + self.vertiport_size // 2)
    
    def draw(self, surface):
        """Desenha a rede: primeiro os links, depois os nós"""
        # Desenha as conexões (links) primeiro para ficarem atrás dos nós
        for node in self.nodes:
            for connected_node in self.adjacency_list[node]:
                # Evita desenhar a mesma linha duas vezes
                if id(node) < id(connected_node):
                    start_pos = self.get_center_position(node)
                    end_pos = self.get_center_position(connected_node)
                    
                    # Verifica se este link faz parte de um caminho destacado
                    is_highlighted = self._is_link_highlighted(node, connected_node)
                    link_color = self.link_highlight_color if is_highlighted else self.link_color
                    link_width = self.link_width + 2 if is_highlighted else self.link_width
                    
                    # Desenha a linha de conexão
                    pygame.draw.line(surface, link_color, start_pos, end_pos, link_width)
        
        # Desenha os nós (vertiportos)
        for node in self.nodes:
            node.draw(surface)
    
    def _is_link_highlighted(self, node1, node2):
        """Verifica se um link está no caminho destacado"""
        if not self.highlighted_path or len(self.highlighted_path) < 2:
            return False
        
        for i in range(len(self.highlighted_path) - 1):
            current = self.highlighted_path[i]
            next_node = self.highlighted_path[i + 1]
            if (current == node1 and next_node == node2) or (current == node2 and next_node == node1):
                return True
        return False
    
    def highlight_path(self, path):
        """Define um caminho para ser destacado na visualização"""
        self.highlighted_path = path if path else []
    
    def clear_highlight(self):
        """Remove o destaque do caminho"""
        self.highlighted_path = []
    
    def set_link_color(self, color):
        """Define a cor dos links da rede"""
        self.link_color = color
    
    def set_highlight_color(self, color):
        """Define a cor de destaque dos links"""
        self.link_highlight_color = color
    
    def set_link_width(self, width):
        """Define a espessura dos links"""
        self.link_width = max(1, width)

# --- Classe para gerenciar Matriz Origem-Destino (OD) ---
class MatrizOD:
    """
    Classe para carregar e processar matrizes Origem-Destino (OD) de demanda de passageiros.
    
    Esta classe é projetada para APENAS CONSUMIR dados de arquivos CSV existentes.
    Ela NÃO gera nem cria novos arquivos CSV.
    
    Funcionalidades:
    - Carrega dados OD de arquivos CSV na pasta /data
    - Processa demanda baseada em dados OD carregados
    - Gera estatísticas de demanda para análise
    - Fornece dados de demanda por intervalos de 5 minutos
    
    Arquivos esperados na pasta /data:
    - Arquivo OD: origem, destino, demanda_base
    - Arquivo de demanda: interval, start_time, end_time, origem, destino, demanda
    """
    def __init__(self, csv_file_path=None):
        self.csv_file_path = csv_file_path
        self.od_data = {}  # Dicionário para armazenar dados OD
        self.vertiports_map = {}  # Mapeia IDs para objetos Vertiport
        self.demand_history = []  # Histórico de demandas processadas
        self.time_intervals = []  # Intervalos de tempo (cada 5 min por 1h)
        
        # Define o diretório de dados
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
        
        # Gera intervalos de 5 minutos por 1 hora (12 intervalos)
        self._generate_time_intervals()
        
        # Carrega dados se arquivo CSV foi fornecido
        if csv_file_path:
            full_path = self.get_data_file_path(csv_file_path)
            if os.path.exists(full_path):
                self.load_od_data(full_path)
            else:
                print(f"⚠️ Arquivo não encontrado: {full_path}")
    
    def get_data_file_path(self, filename):
        """Retorna o caminho completo para um arquivo na pasta data"""
        return os.path.join(self.data_dir, filename)

    def _generate_time_intervals(self):
        """Gera intervalos de tempo de 5 em 5 minutos por 1 hora"""
        start_time = datetime(2024, 1, 1, 8, 0, 0)  # Começa às 8:00
        
        for i in range(12):  # 12 intervalos de 5 minutos = 1 hora
            interval_start = start_time + timedelta(minutes=i * 5)
            interval_end = interval_start + timedelta(minutes=5)
            self.time_intervals.append({
                'interval': i + 1,
                'start_time': interval_start.strftime('%H:%M'),
                'end_time': interval_end.strftime('%H:%M'),
                'datetime_start': interval_start,
                'datetime_end': interval_end
            })
    
    def register_vertiport(self, vertiport_id, vertiport_obj):
        """Registra um vertiport com seu ID para uso na matriz OD"""
        self.vertiports_map[vertiport_id] = vertiport_obj
    
    def load_od_data(self, csv_file_path):
        """Carrega dados de matriz OD de um arquivo CSV"""
        # Se não for um caminho absoluto, usa o diretório de dados
        if not os.path.isabs(csv_file_path):
            full_path = self.get_data_file_path(csv_file_path)
        else:
            full_path = csv_file_path
            
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    origem = row.get('origem', '').strip()
                    destino = row.get('destino', '').strip()
                    demanda_base = int(row.get('demanda_base', 0))
                    
                    if origem and destino:
                        key = f"{origem}->{destino}"
                        self.od_data[key] = {
                            'origem': origem,
                            'destino': destino,
                            'demanda_base': demanda_base
                        }
            
            print(f"✅ Dados OD carregados de {full_path}")
            print(f"📊 {len(self.od_data)} pares origem-destino processados")
            
            # Automaticamente processa os dados OD para gerar demand_history
            self.process_od_data_for_simulation()
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados OD: {e}")
    
    def load_demand_data(self, csv_file_path):
        """Carrega dados de demanda já processados de um arquivo CSV"""
        try:
            demand_data = []
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    demand_data.append({
                        'origem': row.get('origem', '').strip(),
                        'destino': row.get('destino', '').strip(),
                        'demanda': int(row.get('demanda', 0)),
                        'interval': int(row.get('interval', 1)),
                        'start_time': row.get('start_time', '').strip(),
                        'end_time': row.get('end_time', '').strip()
                    })
            
            self.demand_history = demand_data
            print(f"✅ Dados de demanda carregados de {csv_file_path}")
            print(f"📊 {len(self.demand_history)} registros de demanda processados")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados de demanda: {e}")
    
    def process_od_data_for_simulation(self, min_demand=1, max_demand=10):
        """Processa dados OD carregados para gerar demandas simuladas"""
        if not self.od_data:
            print("⚠️ Nenhum dado OD carregado. Use load_od_data() primeiro.")
            return []
        
        demand_data = []
        
        for interval in self.time_intervals:
            for od_key, od_info in self.od_data.items():
                # Gera demanda simulada baseada na demanda base
                base_demand = od_info['demanda_base']
                random_factor = random.uniform(0.5, 1.5)  # Varia entre 50% e 150% da demanda base
                
                demand = max(1, int(base_demand * random_factor))
                demand = random.randint(min(demand, min_demand), min(demand + 3, max_demand))
                
                demand_data.append({
                    'origem': od_info['origem'],
                    'destino': od_info['destino'],
                    'demanda': demand,
                    'interval': interval['interval'],
                    'start_time': interval['start_time'],
                    'end_time': interval['end_time']
                })
        
        self.demand_history = demand_data
        print(f"📊 Dados processados: {len(demand_data)} registros de demanda gerados")
        return demand_data
    
    def _generate_default_od_data(self):
        """Gera dados OD padrão quando não há arquivo CSV"""
        default_pairs = [
            ('V1', 'V3', 5), ('V1', 'V5', 3), ('V1', 'V7', 4),
            ('V2', 'V4', 6), ('V2', 'V6', 4), ('V2', 'V8', 3),
            ('V3', 'V1', 4), ('V3', 'V5', 5), ('V3', 'V7', 2),
            ('V4', 'V2', 3), ('V4', 'V6', 6), ('V4', 'V8', 4),
            ('V5', 'V1', 3), ('V5', 'V3', 4), ('V5', 'V7', 5),
            ('V6', 'V2', 4), ('V6', 'V4', 5), ('V6', 'V8', 3),
            ('V7', 'V1', 2), ('V7', 'V3', 3), ('V7', 'V5', 4),
            ('V8', 'V2', 3), ('V8', 'V4', 4), ('V8', 'V6', 5)
        ]
        
        for origem, destino, demanda_base in default_pairs:
            key = f"{origem}->{destino}"
            self.od_data[key] = {
                'origem': origem,
                'destino': destino,
                'demanda_base': demanda_base
            }
        
    def get_demand_for_interval(self, interval_number):
        """Retorna a demanda para um intervalo específico"""
        return [d for d in self.demand_history if d['interval'] == interval_number]
    
    def get_total_demand_by_od(self):
        """Retorna demanda total agregada por par origem-destino"""
        od_totals = {}
        
        for demand in self.demand_history:
            key = f"{demand['origem']}->{demand['destino']}"
            if key not in od_totals:
                od_totals[key] = 0
            od_totals[key] += demand['demanda']
        
        return od_totals
    
    def get_demand_stats(self):
        """Retorna estatísticas da matriz de demanda"""
        if not self.demand_history:
            return {
                'total_demand': 0,
                'avg_demand_per_interval': 0,
                'min_demand': 0,
                'max_demand': 0,
                'unique_od_pairs': len(self.od_data),
                'time_intervals': len(self.time_intervals)
            }
        
        total_demand = sum(d['demanda'] for d in self.demand_history)
        avg_demand_per_interval = total_demand / len(self.time_intervals) if self.time_intervals else 0
        
        demands = [d['demanda'] for d in self.demand_history]
        min_demand = min(demands)
        max_demand = max(demands)
        
        return {
            'total_demand': total_demand,
            'avg_demand_per_interval': round(avg_demand_per_interval, 2),
            'min_demand': min_demand,
            'max_demand': max_demand,
            'unique_od_pairs': len(self.od_data),
            'time_intervals': len(self.time_intervals)
        }

# --- Princípio da Inversão de Dependência (DIP) aplicado ---
class Simulation:
    """
    Classe principal da simulação seguindo todos os princípios SOLID:
    - SRP: Responsável apenas pela coordenação da simulação
    - OCP: Aberta para extensão através de interfaces
    - LSP: Aceita qualquer implementação das interfaces
    - ISP: Depende apenas das interfaces necessárias
    - DIP: Depende de abstrações, não de implementações concretas
    """
    def __init__(self, 
                 num_vtols: int = 4, 
                 vertiports_json: Optional[str] = None, 
                 vtol_routes_json: Optional[str] = None, 
                 auto_create_network: bool = True,
                 network_manager: Optional['Network'] = None):
        
        # Composição com implementação específica
        self.evtols: List[VTOL] = []
        self.people: List[Person] = []
        self.network: 'Network' = network_manager or Network()
        self._highlight_timer: int = 0
        self.num_vtols: int = num_vtols
        self.vertiports_list: List[dict] = []
        self.vertiports_map: dict = {}
        
        # Inicializa a Matriz OD
        self.matriz_od = MatrizOD()
        
        # Configura a rede baseado nos parâmetros
        self._setup_network(vertiports_json, vtol_routes_json, auto_create_network)
        
        # Configurações finais
        self.network.clear_highlight()
        self._show_network_info()

    def _setup_network(self, vertiports_json: Optional[str], vtol_routes_json: Optional[str], auto_create_network: bool) -> None:
        """Configura a rede baseado nos parâmetros fornecidos"""
        if vertiports_json and vtol_routes_json:
            print("🔧 Modo Personalizado: Carregando configuração via JSON...")
            self._load_vertiports_from_json(vertiports_json)
            self._load_vtol_routes_from_json(vtol_routes_json)
        elif auto_create_network:
            print("🔄 Modo Automático: Criando rede circular padrão...")
            self.create_initial_network()
            self._register_vertiports_in_od()
            self._create_circulating_vtols()

    def _load_vertiports_from_json(self, json_file_path):
        """Carrega vertiportos de um arquivo JSON."""
        try:
            # Se não for um caminho absoluto, usa o diretório de dados
            if not os.path.isabs(json_file_path):
                full_path = self.matriz_od.get_data_file_path(json_file_path)
            else:
                full_path = json_file_path
            
            with open(full_path, 'r', encoding='utf-8') as file:
                vertiports_data = json.load(file)
            
            print(f"📂 Carregando vertiportos de: {full_path}")
            
            # Limpa a rede atual
            self.network = Network()
            self.vertiports_list = []
            self.vertiports_map = {}
            
            # Cria vertiportos baseados no JSON
            for vp_data in vertiports_data:
                vertiport_id = vp_data.get('id', 'V?')
                name = vp_data.get('name', f'Vertiport {vertiport_id}')
                x = vp_data.get('x', 100)
                y = vp_data.get('y', 100)
                capacity = vp_data.get('capacity', 2)
                
                # Cria o objeto Vertiport
                vertiport = Vertiport(x, y, capacity)
                self.network.add_node(vertiport)
                
                # Registra na lista e no mapeamento
                vertiport_info = {
                    'id': vertiport_id,
                    'name': name,
                    'x': x,
                    'y': y,
                    'capacity': capacity,
                    'object': vertiport
                }
                self.vertiports_list.append(vertiport_info)
                self.vertiports_map[vertiport_id] = vertiport
                
                print(f"   ✅ {vertiport_id}: {name} em ({x}, {y})")
            
            # Cria conexões se especificadas no JSON
            self._create_connections_from_json(vertiports_data)
            
            print(f"📍 {len(self.vertiports_list)} vertiportos carregados com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar vertiportos do JSON: {e}")
            # Fallback para rede automática
            self.create_initial_network()
    
    def _create_connections_from_json(self, vertiports_data):
        """Cria conexões entre vertiportos baseado no JSON."""
        connections_made = 0
        
        for vp_data in vertiports_data:
            vertiport_id = vp_data.get('id')
            connections = vp_data.get('connections', [])
            
            if vertiport_id in self.vertiports_map:
                origin_vp = self.vertiports_map[vertiport_id]
                
                for connection_id in connections:
                    if connection_id in self.vertiports_map:
                        dest_vp = self.vertiports_map[connection_id]
                        if self.network.add_link(origin_vp, dest_vp):
                            connections_made += 1
        
        if connections_made > 0:
            print(f"🔗 {connections_made} conexões criadas entre vertiportos")
        else:
            # Se não há conexões especificadas, conecta automaticamente vertiportos próximos
            connections_made = self.network.auto_connect_nearby(max_distance=300)
            print(f"🔗 {connections_made} conexões automáticas criadas (vertiportos próximos)")
    
    def _load_vtol_routes_from_json(self, json_file_path):
        """Carrega rotas de VTOLs de um arquivo JSON."""
        try:
            # Se não for um caminho absoluto, usa o diretório de dados
            if not os.path.isabs(json_file_path):
                full_path = self.matriz_od.get_data_file_path(json_file_path)
            else:
                full_path = json_file_path
            
            with open(full_path, 'r', encoding='utf-8') as file:
                vtol_routes_data = json.load(file)
            
            print(f"🚁 Carregando rotas de VTOLs de: {full_path}")
            
            # Limpa VTOLs existentes
            self.evtols = []
            
            # Cria VTOLs baseados no JSON
            for vtol_data in vtol_routes_data:
                vtol_id = vtol_data.get('vtol_id', 'VTOL-?')
                route = vtol_data.get('route', [])
                start_at_index = vtol_data.get('start_at_index', 0)
                loop_route = vtol_data.get('loop_route', True)
                
                if len(route) < 2:
                    print(f"⚠️ Rota do {vtol_id} muito curta (mínimo 2 vertiportos)")
                    continue
                
                # Valida se todos os vertiportos da rota existem
                valid_route = []
                for vp_id in route:
                    if vp_id in self.vertiports_map:
                        valid_route.append(vp_id)
                    else:
                        print(f"⚠️ Vertiport {vp_id} não encontrado para {vtol_id}")
                
                if len(valid_route) < 2:
                    print(f"⚠️ Rota válida do {vtol_id} muito curta após validação")
                    continue
                
                # Cria o VTOL
                success = self._create_vtol_with_custom_route(vtol_id, valid_route, start_at_index, loop_route)
                if success:
                    print(f"   ✅ {vtol_id}: Rota {' → '.join(valid_route)} (Loop: {'Sim' if loop_route else 'Não'})")
                else:
                    print(f"   ❌ Falha ao criar {vtol_id}")
            
            print(f"🚁 {len(self.evtols)} VTOLs criados com rotas personalizadas!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar rotas de VTOLs do JSON: {e}")
    
    def _create_vtol_with_custom_route(self, vtol_id, route, start_at_index=0, loop_route=True):
        """Cria um VTOL com rota personalizada."""
        if not route or len(route) < 2:
            return False
        
        # Posição inicial
        start_vp_id = route[start_at_index % len(route)]
        start_vp_obj = self.vertiports_map[start_vp_id]
        
        # Próximo vertiport na rota
        next_index = (start_at_index + 1) % len(route)
        next_vp_id = route[next_index]
        next_vp_obj = self.vertiports_map[next_vp_id]
        
        # Cria o VTOL
        vtol = VTOL(
            x=start_vp_obj.x + 30,
            y=start_vp_obj.y + 30,
            network=self.network
        )
        
        # Configura propriedades personalizadas
        vtol.vtol_id = vtol_id
        vtol.custom_route = route  # Rota completa
        vtol.current_route_index = start_at_index  # Índice atual na rota
        vtol.loop_route = loop_route  # Se deve fazer loop
        vtol.is_circulating = True
        vtol.current_vertiport = start_vp_obj
        vtol.vertiports_map = self.vertiports_map  # Referência ao mapeamento
        
        # Define primeiro destino
        if vtol.set_destination_vertiport(next_vp_obj):
            self.evtols.append(vtol)
            return True
        
        return False
    
    def _show_network_info(self):
        """Mostra informações sobre a rede criada."""
        network_info = self.get_network_info()
        print("\n🌐 Informações da Rede UAM:")
        print(f"   📍 Vertiportos: {network_info['nodes']}")
        print(f"   🔗 Conexões: {network_info['edges']}")
        print(f"   🌐 Densidade: {network_info['density']}")
        print(f"   📊 Grau Médio: {network_info['avg_degree']}")
        print(f"   🔄 Conectada: {'✅ Sim' if self.network.is_connected() else '❌ Não'}")
        print(f"   🚁 VTOLs Ativos: {len(self.evtols)}")
        
        # Lista os VTOLs e suas rotas
        if self.evtols:
            print("\n🚁 VTOLs e suas Rotas:")
            for vtol in self.evtols:
                if hasattr(vtol, 'custom_route'):
                    route_str = ' → '.join(vtol.custom_route)
                    loop_str = " (🔄 Loop)" if getattr(vtol, 'loop_route', False) else " (➡️ Linear)"
                    print(f"   {vtol.vtol_id}: {route_str}{loop_str}")
                else:
                    print(f"   {vtol.vtol_id}: Rota circular padrão")

    def get_circulating_vtols_count(self):
        """Retorna o número de VTOLs circulantes ativos."""
        return sum(1 for vtol in self.evtols if hasattr(vtol, 'is_circulating') and vtol.is_circulating)
    
    def spawn_vertiport(self, x=None, y=None, auto_connect=True):
        """Adiciona um novo vertiport à rede em posição específica"""
        x = random.randint(50, WIDTH - 50) if x is None else x
        y = random.randint(50, HEIGHT - 50) if y is None else y
        vertiport = Vertiport(x, y)
        self.network.add_node(vertiport)
        # Conecta automaticamente com vertiportos próximos apenas se solicitado
        if auto_connect:
            self.network.auto_connect_nearby(max_distance=200)
        return vertiport

    def create_initial_network(self):
        """Cria uma rede circular de vertiportos com conexões sequenciais"""
        import math
        
        # Parâmetros do círculo
        center_x, center_y = WIDTH // 2, HEIGHT // 2  # Centro da tela
        radius = 250  # Raio do círculo
        num_vertiports = 8  # Número de vertiportos no círculo
        
        # Lista para armazenar os vertiportos criados em ordem
        vertiports_in_circle = []
        
        # Cria vertiportos em posições circulares
        for i in range(num_vertiports):
            # Calcula o ângulo para este vertiport (distribuição uniforme)
            angle = (2 * math.pi * i) / num_vertiports
            
            # Calcula as coordenadas x, y baseadas no ângulo
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            
            # Cria o vertiport sem auto-conectar
            vertiport = Vertiport(x, y)
            self.network.add_node(vertiport)
            vertiports_in_circle.append(vertiport)
        
        # Conecta cada vertiport apenas com o próximo na sequência (rede circular)
        for i in range(len(vertiports_in_circle)):
            current_vertiport = vertiports_in_circle[i]
            next_vertiport = vertiports_in_circle[(i + 1) % len(vertiports_in_circle)]  # % para fazer o último conectar com o primeiro
            
            # Adiciona link bidirecional entre vertiportos adjacentes
            self.network.add_link(current_vertiport, next_vertiport)
    
    def _register_vertiports_in_od(self):
        """Registra os vertiportos da rede na matriz OD."""
        if not self.network or not self.network.nodes:
            return
            
        # Registra cada vertiport na matriz OD
        for i, node in enumerate(self.network.nodes):
            vertiport_info = {
                'id': f"V{i+1}",
                'name': f"Vertiport {i+1}",
                'x': node.x,
                'y': node.y
            }
            self.vertiports_list.append(vertiport_info)
            
        print(f"📋 Registrados {len(self.vertiports_list)} vertiportos na matriz OD")
    
    def _create_circulating_vtols(self):
        """Cria VTOLs fixos que circulam constantemente pela rede."""
        if len(self.vertiports_list) < 2:
            print("⚠️ Rede insuficiente para VTOLs circulantes (mínimo 2 vertiportos)")
            return
            
        # Distribui VTOLs pelos vertiportos
        for i in range(self.num_vtols):
            # Posição inicial no vertiport
            start_vertiport_idx = i % len(self.vertiports_list)
            start_vertiport = self.vertiports_list[start_vertiport_idx]
            
            # Próximo vertiport na sequência circular
            next_vertiport_idx = (start_vertiport_idx + 1) % len(self.vertiports_list)
            next_vertiport = self.vertiports_list[next_vertiport_idx]
            
            # Encontra os objetos Vertiport correspondentes na rede
            start_vertiport_obj = None
            next_vertiport_obj = None
            
            for node in self.network.nodes:
                if hasattr(node, 'x') and hasattr(node, 'y'):
                    if (abs(node.x - start_vertiport['x']) < 5 and 
                        abs(node.y - start_vertiport['y']) < 5):
                        start_vertiport_obj = node
                    if (abs(node.x - next_vertiport['x']) < 5 and 
                        abs(node.y - next_vertiport['y']) < 5):
                        next_vertiport_obj = node
            
            if not start_vertiport_obj or not next_vertiport_obj:
                print(f"⚠️ Não foi possível encontrar vertiports na rede para VTOL {i+1}")
                continue
            
            # Cria VTOL na posição do vertiport inicial
            vtol = VTOL(
                x=start_vertiport['x'] + 30,  # Centro do vertiport
                y=start_vertiport['y'] + 30,
                network=self.network
            )
            
            # Adiciona propriedades para circulação
            vtol.is_circulating = True  # Marca como VTOL circulante
            vtol.vtol_id = f"VTOL-{i+1}"  # ID personalizado
            vtol.current_vertiport = start_vertiport_obj
            
            # Define destino e inicia movimento
            if vtol.set_destination_vertiport(next_vertiport_obj):
                print(f"🚁 {vtol.vtol_id}: {start_vertiport['name']} → {next_vertiport['name']}")
            else:
                print(f"⚠️ Falha ao definir rota para {vtol.vtol_id}")
            
            self.evtols.append(vtol)
    
    def _get_next_vertiport_for_vtol(self, current_destination_id):
        """Retorna o próximo vertiport na sequência circular."""
        # Encontra o índice do vertiport atual
        current_idx = None
        for i, vertiport in enumerate(self.vertiports_list):
            if vertiport['id'] == current_destination_id:
                current_idx = i
                break
        
        if current_idx is not None:
            # Próximo vertiport na sequência circular
            next_idx = (current_idx + 1) % len(self.vertiports_list)
            return self.vertiports_list[next_idx]
        
        # Fallback: retorna o primeiro vertiport
        return self.vertiports_list[0] if self.vertiports_list else None
    
    def get_network_info(self):
        """Retorna informações sobre a rede"""
        return self.network.get_network_stats()
    
    def find_route(self, start_vertiport, end_vertiport):
        """Encontra uma rota entre dois vertiportos"""
        return self.network.find_shortest_path(start_vertiport, end_vertiport)
    
    def is_network_connected(self):
        """Verifica se a rede está conectada"""
        return self.network.is_connected()
    
    def highlight_route_between_vertiports(self, vertiport1, vertiport2):
        """Destaca uma rota entre dois vertiportos específicos"""
        path = self.network.find_shortest_path(vertiport1, vertiport2)
        if path:
            self.network.highlight_path(path)
            return path
        return []
    
    def clear_route_highlight(self):
        """Remove o destaque da rota"""
        self.network.clear_highlight()
    
    def create_circular_network(self, num_vertiports=8, radius=250):
        """Cria uma nova rede circular com parâmetros personalizados"""
        import math
        
        # Limpa a rede atual
        self.network = Network()
        
        # Parâmetros do círculo
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        
        # Lista para armazenar os vertiportos criados em ordem
        vertiports_in_circle = []
        
        # Cria vertiportos em posições circulares
        for i in range(num_vertiports):
            angle = (2 * math.pi * i) / num_vertiports
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            
            vertiport = Vertiport(x, y)
            self.network.add_node(vertiport)
            vertiports_in_circle.append(vertiport)
        
        # Conecta cada vertiport apenas com o próximo na sequência
        for i in range(len(vertiports_in_circle)):
            current_vertiport = vertiports_in_circle[i]
            next_vertiport = vertiports_in_circle[(i + 1) % len(vertiports_in_circle)]
            self.network.add_link(current_vertiport, next_vertiport)
        
        return vertiports_in_circle
    
    def update(self):
        """Atualiza o estado da simulação sem criar novos objetos automaticamente"""
        # Timer da simulação para controle interno
        self._highlight_timer += 1
        
        # Atualiza apenas os estados dos objetos existentes
        # Não cria novos objetos automaticamente

    def draw(self, surface):
        # Desenha a rede (vertiportos e suas conexões)
        self.network.draw(surface)
        
        # Desenha as pessoas
        for p in self.people:
            if not p.clean: # Se a pessoa não chegou ao destino, desenha
                p.draw(surface)
            else: # Se chegou ao destino, remove a pessoa
                self.people.remove(p)
        
        # Desenha os VTOLs
        for e in self.evtols[:]:  # Cria uma cópia da lista para iteração segura
            if not e.clean: # Se o VTOL não chegou ao destino, desenha
                e.draw(surface)
            else: # Se chegou ao destino
                # Só remove VTOLs que não são circulantes
                if not (hasattr(e, 'is_circulating') and e.is_circulating):
                    self.evtols.remove(e)

# --- Princípio da Inversão de Dependência (DIP): Simulador depende de abstrações ---
class SimulatorUI:
    def __init__(self, fps: bool = True):
        self.title_window = "UAM Network Simulator"
        self.fps = fps
        self.sim = Simulation()

        pygame.init()
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.title_window)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            if self.fps:
                pygame.display.set_caption(f"{self.title_window} - FPS: {self.clock.get_fps():.2f}")

            # Processa eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

            # Desenha fundo e atualiza a tela
            self.screen.fill((30, 30, 30))
            self.sim.draw(self.screen)

            # Atualiza apenas a simulação - sem criações automáticas
            self.sim.update()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    print("🚀 UAM Network Simulator - Sistema de Cadastro JSON")
    print("=" * 55)
    
    # Exemplo 1: Simulação com rede automática (modo padrão)
    print("\n📋 Exemplo 1: Modo Automático (Rede Circular)")
    print("Criando simulação com rede circular padrão...")
    
    sim_auto = Simulation(num_vtols=4)
    print("✅ Simulação automática criada!\n")
    
    # Exemplo 2: Simulação com configuração JSON personalizada
    print("\n� Exemplo 2: Modo Personalizado (Configuração JSON)")
    print("Carregando configuração de vertiportos e rotas de arquivos JSON...")
    
    try:
        sim_custom = Simulation(
            num_vtols=0,  # Não cria VTOLs automáticos
            vertiports_json="vertiports.json",
            vtol_routes_json="vtol_routes.json",
            auto_create_network=False
        )
        print("✅ Simulação personalizada criada!\n")
        
        # Exemplo 3: Demonstração da simulação visual
        print("\n🎮 Iniciando Simulação Visual...")
        print("Escolha qual simulação executar:")
        print("1 - Simulação Automática (rede circular)")
        print("2 - Simulação Personalizada (JSON)")
        
        # Para demonstração, vamos usar a simulação personalizada
        app = SimulatorUI()
        app.sim = sim_custom  # Substitui a simulação padrão
        
        print("🚁 Executando simulação personalizada com rotas JSON...")
        app.run()
        
    except Exception as e:
        print(f"⚠️ Erro ao carregar configuração JSON: {e}")
        print("🔄 Executando simulação automática como fallback...")
        
        app = SimulatorUI()
        app.run()
