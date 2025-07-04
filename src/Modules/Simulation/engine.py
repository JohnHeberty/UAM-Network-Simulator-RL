"""
Simulation engine for UAM Network Simulator

Motor principal da simulação implementando arquitetura SOLID.
"""

import pandas as pd
import networkx as nx
from typing import List, Dict, Tuple, Optional
import math
import pygame
import sys
import os
import json
from abc import ABC, abstractmethod

# Visual Constants
WIDTH, HEIGHT = 1000, 800
FPS = 60
VERTIPORT_COLOR = (180, 180, 180)
VERTIPORT_BORDER_COLOR = (220, 220, 220)
NETWORK_LINK_COLOR = (150, 150, 255)
NETWORK_LINK_HIGHLIGHT_COLOR = (255, 255, 100)
VTOL_DRAW_SIZE = 16
PERSON_COLOR = (255, 100, 100)  # Red color for passengers

# Visual Interfaces
class Drawable(ABC):
    """Interface for objects that can be drawn on screen"""
    @abstractmethod
    def draw(self, surface):
        pass

class MatrizOD:
    """Classe para gerenciar matriz origem-destino de demanda de passageiros"""
    
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.demand_data = None
        self.current_time_minutes = 0  # Tempo em minutos desde 00:00
        self.load_demand_data()
    
    def load_demand_data(self):
        """Carrega dados de demanda do arquivo CSV"""
        try:
            self.demand_data = pd.read_csv(self.csv_file_path)
            print(f"Loaded {len(self.demand_data)} demand records from {self.csv_file_path}")
        except FileNotFoundError:
            print(f"Warning: Demand file {self.csv_file_path} not found. Using default demand.")
            self.demand_data = pd.DataFrame()
    
    def time_to_minutes(self, time_str):
        """Converte string de tempo (HH:MM) para minutos desde 00:00"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return hour * 60 + minute
        except ValueError:
            return 0
    
    def get_current_time_str(self):
        """Retorna tempo atual como string HH:MM"""
        hours = self.current_time_minutes // 60
        minutes = self.current_time_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    
    def advance_time(self, minutes=1):
        """Avança o tempo da simulação"""
        self.current_time_minutes += minutes
        # Reset após 24 horas
        if self.current_time_minutes >= 24 * 60:
            self.current_time_minutes = 0
    
    def get_current_demand(self):
        """Retorna demanda atual baseada no tempo de simulação"""
        if self.demand_data is None or self.demand_data.empty:
            return []
        
        current_demands = []
        for _, row in self.demand_data.iterrows():
            start_time = self.time_to_minutes(row['hora_inicio'])
            end_time = self.time_to_minutes(row['hora_fim'])
            
            # Verifica se o tempo atual está no intervalo
            if start_time <= self.current_time_minutes < end_time:
                current_demands.append({
                    'origem': row['vertiport_origem'],
                    'destino': row['vertiport_destino'],
                    'demanda': int(row['demanda'])
                })
        
        return current_demands

# --- Princípio da Responsabilidade Única (SRP) ---
class Person(Drawable):
    def __init__(self, x, y, origin_vertiport=None, destination_vertiport=None):
        self.xo = x  # origin position
        self.yo = y  # origin position
        self.xd = x  # destination position
        self.yd = y  # destination position
        self.bxo = x  # before position x
        self.byo = y  # before position y
        
        self.origin_vertiport = origin_vertiport
        self.destination_vertiport = destination_vertiport
        self.current_vertiport = origin_vertiport
        
        self.state = "waiting"  # waiting, boarding, flying, arrived, leaving
        self.path_planner = StraightLinePathPlanner()
        self.clean = False
        self.boarding_vtol = None
        
        # Animação de saída (pessoa sobe verticalmente quando sai do vertiporto)
        self.exit_animation = False
        self.exit_start_y = y
        self.exit_speed = 2

    def set_destination(self, xd, yd):
        if (self.xd, self.yd) == (self.xo, self.yo):
            self.xd = xd
            self.yd = yd

    def board_vtol(self, vtol):
        """Embarca a pessoa no VTOL"""
        self.boarding_vtol = vtol
        self.state = "boarding"
    
    def arrive_at_destination(self):
        """Pessoa chegou ao destino - inicia animação de saída"""
        self.state = "leaving"
        self.exit_animation = True
        self.exit_start_y = self.yo
        self.current_vertiport = self.destination_vertiport
    
    def is_ready_for_cleanup(self):
        """Verifica se a pessoa está pronta para ser removida da simulação"""
        return self.clean

    def draw(self, surface):
        # Atualiza posição baseada no estado
        if self.state == "flying" and self.boarding_vtol:
            # Pessoa está voando - segue o VTOL
            self.xo = self.boarding_vtol.xo + 10  # Offset para não sobrepor
            self.yo = self.boarding_vtol.yo + 10
        elif self.state == "leaving" and self.exit_animation:
            # Animação de saída - pessoa sobe verticalmente
            self.yo -= self.exit_speed
            if self.yo < -20:  # Saiu da tela
                self.clean = True
                return
        elif self.state == "waiting":
            # Movimento normal para posição de destino dentro do vertiport
            if (self.xo, self.yo) != (self.xd, self.yd):
                self.xo, self.yo = self.path_planner.get_next_point((self.xo, self.yo), (self.xd, self.yd))
            # Verificar se chegou e está saindo
            if (self.bxo, self.byo) == (self.xo, self.yo) and self.state == "leaving":
                # Pessoa parou no vertiporto de destino - inicia saída
                self.exit_animation = True
                self.exit_start_y = self.yo
        
        # Atualiza posição anterior
        self.bxo, self.byo = self.xo, self.yo
        
        # Desenha a pessoa com cor baseada no estado
        color = PERSON_COLOR
        if self.state == "boarding":
            color = (255, 255, 100)  # Amarelo para embarcando
        elif self.state == "flying":
            color = (100, 255, 100)  # Verde para voando
        elif self.state == "leaving":
            color = (255, 200, 100)  # Laranja para saindo
            
        # Draw person safely (check for valid coordinates)
        if self.xo >= 0 and self.yo >= 0:
            pygame.draw.circle(surface, color, (int(self.xo), int(self.yo)), 3)

class PathPlanner(ABC):
    """Interface for route planning strategies"""
    @abstractmethod
    def plan_route(self, origin: Tuple[int, int], destination: Tuple[int, int]) -> List[Tuple[int, int]]:
        pass
    
    @abstractmethod
    def get_next_point(self, current_pos: Tuple[int, int], target_pos: Tuple[int, int]) -> Tuple[int, int]:
        pass

# Path Planner Implementation
class StraightLinePathPlanner(PathPlanner):
    """Straight line route planner"""
    def __init__(self, step=1):
        self.step = step

    def plan_route(self, origin, destination):
        """Plans a simple route from origin to destination"""
        return [origin, destination]
    
    def get_next_point(self, current_pos, target_pos):
        """Calculates the next point towards the target"""
        ox, oy = current_pos
        dx, dy = target_pos
        vx, vy = dx - ox, dy - oy
        dist = (vx ** 2 + vy ** 2) ** 0.5
        if dist == 0 or dist < self.step:
            return target_pos
        next_x = ox + self.step * vx / dist
        next_y = oy + self.step * vy / dist
        return int(next_x), int(next_y)

class VTOL(Drawable):
    """VTOL (Vertical Take-Off and Landing) aircraft that navigates through the vertiport network."""
    
    def __init__(self, x, y, network=None):
        # Position
        self.xo = x
        self.yo = y
        self.bxo = self.xo
        self.byo = self.yo
        
        # Navigation
        self.destination_vertiport = None
        self.current_vertiport = None
        self.flight_path = []
        self.current_path_index = 0
        self.intermediate_target = None
        self.network = network
        
        # State
        self.clean = False
        self.state = "landed"
        self.state_timer = 0
        
        # Circulation properties - Enhanced for JSON routes
        self.is_circulating = False
        self.vtol_id = "VTOL"
        self.planned_route = []  # The planned route from JSON
        self.current_route_index = 0
        self.is_circular_route = False  # True if first == last vertiport
        self.reverse_direction = False  # For non-circular routes (ping-pong)
        self.vertiports_map = {}
        self._next_destination = None
        
        # Journey properties for simulation compatibility
        self.final_destination = None
        self.journey_route = []  # Current leg of the journey (A->B pathfinding)
        
        # Animation
        self.base_width = VTOL_DRAW_SIZE
        self.atual_scale = 0.4
        self.scale_animation = False
        self.scale_target = 0.4
        self.scale_speed = 0.02
        
        # Movement
        self.speed = 4
        self.path_planner = StraightLinePathPlanner(step=self.speed)
        
        # Passenger management
        self.onboard_passengers = []  # List of passengers currently on board
        self.max_passengers = 4  # Maximum passenger capacity
        
        # Anti-stuck mechanisms
        self.landed_timer = 0  # Track how long VTOL has been landed
        self.max_landed_time = 200  # Maximum frames to stay landed before forced takeoff
        self.hover_count = 0  # Track number of hover attempts
        self.max_hover_count = 15  # Maximum hover attempts before abort
        
        # Colors by state
        self.colors = {
            "landed": (80, 150, 200),
            "taking_off": (120, 180, 255),
            "flying": (100, 200, 255),
            "landing": (120, 180, 255),
            "hovering": (255, 255, 100),
            "in_transit": (150, 220, 255)
        }
        
        # Landing control
        self._can_attempt_landing = True
        self._hover_position = None
        
        # Simulation compatibility
        self.departure_time = 0
        self.passengers = 1
        self.status = "WAITING"  # For simulation compatibility
    
    def _set_next_circulation_destination(self):
        """Define the next destination for circulating VTOLs."""
        if not self.network or not self.current_vertiport:
            return False
        
        if hasattr(self, 'planned_route') and self.planned_route:
            return self._set_next_planned_route_destination()
        
        return self._set_next_circular_destination()
    
    def _set_next_planned_route_destination(self):
        """Define next destination based on planned route from JSON."""
        if not self.planned_route or len(self.planned_route) < 2:
            return False

        # Check if route is circular (first == last)
        self.is_circular_route = self.planned_route[0] == self.planned_route[-1]

        if self.is_circular_route:
            # Circular route: just move to next index, wrapping around
            next_index = (self.current_route_index + 1) % len(self.planned_route)
        else:
            # Non-circular route: ping-pong behavior
            if not self.reverse_direction:
                # Going forward
                next_index = self.current_route_index + 1
                if next_index >= len(self.planned_route):
                    # Reached end, start going backwards
                    self.reverse_direction = True
                    next_index = self.current_route_index - 1
            else:
                # Going backwards
                next_index = self.current_route_index - 1
                if next_index < 0:
                    # Reached beginning, start going forward again
                    self.reverse_direction = False
                    next_index = self.current_route_index + 1

        # Validate index
        if next_index < 0 or next_index >= len(self.planned_route):
            return False

        next_vp_id = self.planned_route[next_index]
        if hasattr(self, 'vertiports_map') and next_vp_id in self.vertiports_map:
            next_vertiport = self.vertiports_map[next_vp_id]
            self.state_timer = 15
            self._next_destination = next_vertiport
            return True
        return False
    
    def _set_next_circular_destination(self):
        """Define next destination using default circular logic."""
        if not self.network:
            return False
            
        current_index = None
        nodes_list = list(self.network.nodes)
        
        for i, node in enumerate(nodes_list):
            if node == self.current_vertiport:
                current_index = i
                break
        
        if current_index is not None:
            next_index = (current_index + 1) % len(nodes_list)
            next_vertiport = nodes_list[next_index]
            self.state_timer = 15
            self._next_destination = next_vertiport
            return True
        
        return False
    
    def find_nearest_vertiport(self):
        """Find the nearest vertiport to current position"""
        if not self.network or not hasattr(self.network, 'nodes'):
            return None
        
        min_distance = float('inf')
        nearest_vertiport = None
        
        for vertiport in self.network.nodes:
            center_x = vertiport.x + 30
            center_y = vertiport.y + 30
            distance = ((self.xo - center_x)**2 + (self.yo - center_y)**2)**0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest_vertiport = vertiport
        
        return nearest_vertiport
    
    def set_destination_vertiport(self, destination_vertiport):
        """Set the destination vertiport and calculate route"""
        if not self.network or not hasattr(self.network, 'nodes'):
            return False
            
        if destination_vertiport not in self.network.nodes:
            return False
        
        if not self.current_vertiport:
            self.current_vertiport = self.find_nearest_vertiport()
        
        if not self.current_vertiport:
            return False
        
        # Use NetworkX pathfinding if available
        if hasattr(self.network, 'find_shortest_path'):
            self.flight_path = self.network.find_shortest_path(
                self.current_vertiport, 
                destination_vertiport
            )
        else:
            self.flight_path = [self.current_vertiport, destination_vertiport]
        
        if not self.flight_path:
            return False
        
        self.destination_vertiport = destination_vertiport
        self.current_path_index = 0
        
        if len(self.flight_path) == 1:
            return True
        
        self._start_takeoff()
        return True
    
    def _start_takeoff(self):
        """Start the takeoff sequence"""
        if self.state == "landed":
            # Try to board passengers before takeoff
            self._board_passengers()
            
            if self.current_vertiport and hasattr(self.current_vertiport, 'takeoff_vtol'):
                self.current_vertiport.takeoff_vtol(self)
            
            self.state = "taking_off"
            self.state_timer = 30
            self.scale_target = 1.0
            self.scale_animation = True
            self.current_vertiport = None
    
    def _board_passengers(self):
        """Board passengers at current vertiport before takeoff"""
        if not self.current_vertiport or not self.destination_vertiport:
            return
        
        # Get destination name safely  
        dest_name = getattr(self.destination_vertiport, 'name', str(self.destination_vertiport))
        
        # Get passengers going to our destination
        available_seats = self.max_passengers - len(self.onboard_passengers)
        if available_seats <= 0:
            return
        
        # Get passengers from vertiport
        passengers_to_board = self.current_vertiport.get_passengers_for_destination(
            dest_name, 
            available_seats
        )
        
        for passenger in passengers_to_board:
            passenger.board_vtol(self)
            passenger.state = "flying"
            self.onboard_passengers.append(passenger)
            print(f"VTOL {self.vtol_id}: Boarded passenger going to {dest_name}")
    
    def _disembark_passengers(self):
        """Disembark passengers at destination vertiport"""
        if not self.current_vertiport:
            return
        
        # Get current vertiport name safely
        current_vp_name = getattr(self.current_vertiport, 'name', str(self.current_vertiport))
        
        passengers_to_disembark = []
        for passenger in self.onboard_passengers[:]:
            if (passenger.destination_vertiport and 
                getattr(passenger.destination_vertiport, 'name', str(passenger.destination_vertiport)) == current_vp_name):
                passengers_to_disembark.append(passenger)
        
        for passenger in passengers_to_disembark:
            self.onboard_passengers.remove(passenger)
            self.current_vertiport.receive_passenger(passenger)
            print(f"VTOL {self.vtol_id}: Disembarked passenger at {current_vp_name}")
    
    def get_passenger_count(self):
        """Get current number of passengers on board"""
        return len(self.onboard_passengers)
    
    def _start_landing(self):
        """Start the landing sequence or hover if no space"""
        if self.state in ["flying", "in_transit", "hovering"]:
            if self.destination_vertiport and hasattr(self.destination_vertiport, 'request_landing'):
                if self.destination_vertiport.request_landing(self):
                    self.state = "landing"
                    self.state_timer = 30
                    self.scale_target = 0.4
                    self.scale_animation = True
                else:
                    self._start_hovering()
            else:
                self.state = "landing"
                self.state_timer = 30
                self.scale_target = 0.4
                self.scale_animation = True
    
    def _start_hovering(self):
        """Start hovering state over the vertiport"""
        self.state = "hovering"
        self.state_timer = 60  # Initial hover time
        self.hover_count = getattr(self, 'hover_count', 0) + 1  # Track hover attempts
        if self.destination_vertiport:
            self._hover_position = (
                self.destination_vertiport.x + 30,
                self.destination_vertiport.y + 10
            )
        self._can_attempt_landing = False
        
        print(f"🔄 VTOL {self.vtol_id}: Starting hover #{self.hover_count} at {self.destination_vertiport.name if self.destination_vertiport else 'unknown'}")
        
        # Limit hover attempts to prevent infinite hovering
        if self.hover_count > self.max_hover_count:
            print(f"⚠️  VTOL {self.vtol_id}: Too many hover attempts ({self.hover_count}), aborting mission...")
            self._find_alternative_or_abort()

    def _find_alternative_or_abort(self):
        """Find alternative route or abort mission when hovering too long"""
        # For now, just clean up the VTOL to prevent infinite hovering
        # In a more sophisticated system, we could find alternative vertiports
        print(f"🚁 VTOL {self.vtol_id}: Aborting mission due to excessive hovering")
        
        # Remove from hovering queue if present
        if (self.destination_vertiport and 
            hasattr(self.destination_vertiport, 'hovering_queue') and 
            self in self.destination_vertiport.hovering_queue):
            self.destination_vertiport.hovering_queue.remove(self)
        
        self.clean = True
    
    def _update_scale_animation(self):
        """Update scale animation"""
        if self.scale_animation:
            if abs(self.atual_scale - self.scale_target) > 0.01:
                direction = 1 if self.scale_target > self.atual_scale else -1
                self.atual_scale += direction * self.scale_speed
            else:
                self.atual_scale = self.scale_target
                self.scale_animation = False
    
    def _get_next_waypoint(self):
        """Get the next waypoint in the path"""
        if (self.current_path_index < len(self.flight_path) - 1):
            self.current_path_index += 1
            next_vertiport = self.flight_path[self.current_path_index]
            return (next_vertiport.x + 30, next_vertiport.y + 30)
        return None
    
    def _update_movement(self):
        """Update VTOL movement"""
        if self.state in ["flying", "in_transit"]:
            if not self.intermediate_target:
                self.intermediate_target = self._get_next_waypoint()
                if not self.intermediate_target:
                    self._start_landing()
                    return
            
            self.bxo, self.byo = self.xo, self.yo
            new_pos = self.path_planner.get_next_point(
                (self.xo, self.yo), 
                self.intermediate_target
            )
            self.xo, self.yo = new_pos
            
            distance_to_target = ((self.xo - self.intermediate_target[0])**2 + 
                                (self.yo - self.intermediate_target[1])**2)**0.5
            
            if distance_to_target < 8:
                self.intermediate_target = self._get_next_waypoint()
                if not self.intermediate_target:
                    self._start_landing()
    
    def update(self):
        """Update VTOL state and movement"""
        if self.state_timer > 0:
            self.state_timer -= 1
        
        if self.state == "taking_off":
            self.landed_timer = 0  # Reset landed timer when taking off
            if self.state_timer <= 0:
                self.state = "flying"
                if len(self.flight_path) > 1:
                    next_vertiport = self.flight_path[1]
                    self.intermediate_target = (next_vertiport.x + 30, next_vertiport.y + 30)
                    self.current_path_index = 0
        
        elif self.state == "landing":
            if self.state_timer <= 0:
                if self.destination_vertiport and hasattr(self.destination_vertiport, 'land_vtol'):
                    if self.destination_vertiport.land_vtol(self):
                        self.state = "landed"
                        self.xo = self.destination_vertiport.x + 30
                        self.yo = self.destination_vertiport.y + 30
                        self.current_vertiport = self.destination_vertiport
                        # Disembark passengers after landing
                        self._disembark_passengers()
                    else:
                        self._start_hovering()
                else:
                    self.state = "landed"
                    if self.destination_vertiport:
                        self.xo = self.destination_vertiport.x + 30
                        self.yo = self.destination_vertiport.y + 30
                    self.current_vertiport = self.destination_vertiport
                    # Disembark passengers after landing
                    self._disembark_passengers()
                
                if (self.current_vertiport and 
                    self.destination_vertiport and 
                    self.current_vertiport == self.destination_vertiport):
                    
                    if hasattr(self, 'is_circulating') and self.is_circulating:
                        self._set_next_circulation_destination()
                    else:
                        self.clean = True

        elif self.state == "hovering":
            if self._hover_position:
                self.bxo, self.byo = self.xo, self.yo
                new_pos = self.path_planner.get_next_point(
                    (self.xo, self.yo), 
                    self._hover_position
                )
                self.xo, self.yo = new_pos
            
            # Check for landing opportunity more frequently
            if (self._can_attempt_landing or self.state_timer <= 0):
                if (self.destination_vertiport and 
                    hasattr(self.destination_vertiport, 'can_land') and 
                    self.destination_vertiport.can_land(self)):
                    print(f"🛬 VTOL {self.vtol_id}: Landing spot available, attempting landing...")
                    self._start_landing()
                else:
                    # Reset timer and try again, but with exponentially increasing intervals
                    self.state_timer = min(120, 60 + (self.hover_count * 10))  # Increase wait time
                    self._can_attempt_landing = False
                    print(f"⏳ VTOL {self.vtol_id}: Still hovering (attempt {self.hover_count}), waiting {self.state_timer} frames...")
        
        elif self.state == "landed":
            self.landed_timer += 1  # Increment landed timer
            
            # Anti-stuck mechanism: Force takeoff if landed too long
            if self.landed_timer > self.max_landed_time:
                print(f"⚠️  VTOL {self.vtol_id}: Forced takeoff after {self.landed_timer} frames landed")
                if hasattr(self, 'is_circulating') and self.is_circulating:
                    if not self._set_next_circulation_destination():
                        # If can't set next destination, try to force it
                        print(f"🔄 VTOL {self.vtol_id}: Retrying route continuation...")
                        self.state_timer = 5  # Short timer to retry soon
                else:
                    # For non-circulating VTOLs, clean them up to avoid infinite stuck
                    print(f"🧹 VTOL {self.vtol_id}: Cleaning up non-circulating VTOL")
                    self.clean = True
                self.landed_timer = 0  # Reset timer
            
            # VTOLs circulantes devem continuar suas rotas
            elif (hasattr(self, 'is_circulating') and self.is_circulating and self.state_timer <= 0):
                if hasattr(self, '_next_destination'):
                    next_dest = self._next_destination
                    delattr(self, '_next_destination')
                    
                    if self.set_destination_vertiport(next_dest):
                        if hasattr(self, 'planned_route') and self.planned_route:
                            for i, vp_id in enumerate(self.planned_route):
                                if (hasattr(self, 'vertiports_map') and 
                                    vp_id in self.vertiports_map and 
                                    self.vertiports_map[vp_id] == next_dest):
                                    self.current_route_index = i
                                    break
                        print(f"🚁 VTOL {self.vtol_id}: Starting next leg of route to {getattr(next_dest, 'name', 'unknown')}")
                        self.landed_timer = 0  # Reset timer on departure
                    else:
                        print(f"❌ VTOL {self.vtol_id}: Failed to set destination, will retry...")
                        self.state_timer = 10  # Retry in 10 frames
                else:
                    # Automatically set next destination if not set
                    if self._set_next_circulation_destination():
                        print(f"🔄 VTOL {self.vtol_id}: Continuing circulation route")
                        self.landed_timer = 0  # Reset timer on departure
                    else:
                        # If cannot set next destination, schedule retry
                        print(f"⏳ VTOL {self.vtol_id}: Cannot set next destination, retrying in 15 frames...")
                        self.state_timer = 15  # Retry in 15 frames
                    
            elif (hasattr(self, 'planned_route') and self.planned_route and 
                  self.is_circulating and self.state_timer <= 0):
                # For planned route VTOLs, automatically continue to next destination
                if self.advance_to_next_planned_destination():
                    self.status = "FLYING"
                    self.landed_timer = 0  # Reset timer on departure
                    print(f"✈️  VTOL {self.vtol_id}: Advancing to next planned destination")
                else:
                    print(f"⚠️  VTOL {self.vtol_id}: Failed to advance, retrying...")
                    self.state_timer = 15  # Retry in 15 frames
                    
            # Traditional VTOLs (não-circulantes) também devem poder continuar
            elif not hasattr(self, 'is_circulating') or not self.is_circulating:
                # Para VTOLs tradicionais, verificar se há próximo destino pendente
                if hasattr(self, 'final_destination') and self.final_destination:
                    # Se ainda não chegou ao destino final, continuar
                    if (self.current_vertiport != self.final_destination and 
                        self.state_timer <= 0):
                        print(f"🚁 VTOL {self.vtol_id}: Continuing to final destination")
                        self.set_destination_vertiport(self.final_destination)
                        self.landed_timer = 0  # Reset timer on departure
        
        elif self.state in ["flying", "in_transit"]:
            self._update_movement()
        
        self._update_scale_animation()
        
        # Update status for simulation compatibility - preserve manual status changes
        if self.state == "landed":
            self.status = "LANDED"
        elif self.state in ["flying", "in_transit", "taking_off", "landing"]:
            self.status = "FLYING"
        elif self.status not in ["FLYING", "LANDED"]:  # Only change to WAITING if not manually set
            self.status = "WAITING"
    
    def get_current_color(self):
        """Return color based on current state"""
        return self.colors.get(self.state, self.colors["flying"])
    
    def draw(self, surface):
        """Draw the VTOL"""
        self.update()
        
        size = int(self.base_width * self.atual_scale)
        color = self.get_current_color()
        
        # Main body
        main_rect = pygame.Rect(
            self.xo - size//2, 
            self.yo - int(size * 0.75)//2, 
            size, 
            int(size * 0.75)
        )
        pygame.draw.rect(surface, color, main_rect)
        
        # Visual effects by state
        if self.state in ["flying", "in_transit"]:
            rotor_color = (200, 200, 200)
            rotor_size = size + 2
            pygame.draw.circle(surface, rotor_color, 
                             (self.xo - size//2, self.yo), rotor_size//3, 1)
            pygame.draw.circle(surface, rotor_color, 
                             (self.xo + size//2, self.yo), rotor_size//3, 1)
        
        elif self.state == "taking_off":
            pygame.draw.circle(surface, (255, 255, 255), 
                             (self.xo, self.yo + size//2), size//2, 1)
        
        elif self.state == "landing":
            pygame.draw.circle(surface, (255, 255, 100), 
                             (self.xo, self.yo + size//2), size//2, 1)
        
        elif self.state == "hovering":
            pygame.draw.circle(surface, (255, 255, 0), 
                             (self.xo, self.yo), size//2 + 3, 2)
            pygame.draw.circle(surface, (255, 255, 100), 
                             (self.xo - size//2, self.yo), size//3, 1)
            pygame.draw.circle(surface, (255, 255, 100), 
                             (self.xo + size//2, self.yo), size//3, 1)
        
        # Destination line
        if self.destination_vertiport and self.state in ["flying", "in_transit", "taking_off", "hovering"]:
            dest_x = self.destination_vertiport.x + 30
            dest_y = self.destination_vertiport.y + 30
            pygame.draw.line(surface, (255, 255, 0), 
                           (self.xo, self.yo), (dest_x, dest_y), 1)
        
        # Draw passenger count if carrying passengers
        if len(self.onboard_passengers) > 0:
            if hasattr(pygame, 'font') and pygame.font.get_init():
                font = pygame.font.Font(None, 16)
                passenger_text = str(len(self.onboard_passengers))
                text_surface = font.render(passenger_text, True, (255, 255, 255))
                text_x = self.xo - text_surface.get_width() // 2
                text_y = self.yo - size - 10
                surface.blit(text_surface, (text_x, text_y))
    
    # Compatibility methods for simulation
    def can_depart(self, current_time: int, vertiport_capacity: Dict[str, int]) -> bool:
        """Check if VTOL can depart from current vertiport."""
        if current_time < self.departure_time:
            return False
        
        if self.status != "WAITING":
            return False
        
        # VTOL can always depart if it's waiting and time is reached
        return True
    
    def fly_to_next_vertiport(self, next_vertiport: str):
        """Move VTOL to next vertiport in route."""
        # Find vertiport object by name/id
        target_vertiport = None
        if self.network and hasattr(self.network, 'nodes'):
            for vp in self.network.nodes:
                if str(vp) == next_vertiport or (hasattr(vp, 'name') and vp.name == next_vertiport):
                    target_vertiport = vp
                    break
        
        if target_vertiport:
            # Check if this is the final destination
            if (self.final_destination and hasattr(self.final_destination, 'name') and 
                hasattr(target_vertiport, 'name') and 
                target_vertiport.name == self.final_destination.name):
                # This is the final destination - but still need to fly there visually
                if self.set_destination_vertiport(target_vertiport):
                    self.status = "FLYING"
                else:
                    # Fallback to immediate arrival
                    self.current_vertiport = target_vertiport
                    self.status = "LANDED"
                    self.state = "landed"
            else:
                # Start visual flight to next vertiport
                if self.set_destination_vertiport(target_vertiport):
                    self.status = "FLYING"
                else:
                    # Fallback to immediate movement
                    self.current_vertiport = target_vertiport
                    self.status = "FLYING"
                    self.state = "flying"
    
    def hover(self):
        """Increment hover count."""
        self.hover_count += 1
        if self.state != "hovering":
            self._start_hovering()
    
    def can_hover(self) -> bool:
        """Check if VTOL can still hover."""
        return self.hover_count < self.max_hover_count

    def set_planned_route(self, route: List[str], vertiports_map: Dict[str, object]):
        """Set the planned route for this VTOL from JSON configuration."""
        self.planned_route = route.copy()
        self.vertiports_map = vertiports_map
        self.is_circulating = True
        self.current_route_index = 0
        self.reverse_direction = False
        
        # Determine if route is circular
        self.is_circular_route = len(route) > 1 and route[0] == route[-1]
        
        # Set initial position to first vertiport in route
        if route and route[0] in vertiports_map:
            initial_vertiport = vertiports_map[route[0]]
            self.current_vertiport = initial_vertiport
            # Safe access to x, y attributes
            if hasattr(initial_vertiport, 'x') and hasattr(initial_vertiport, 'y'):
                self.xo = initial_vertiport.x + 30
                self.yo = initial_vertiport.y + 30
                self.bxo = self.xo
                self.byo = self.yo
            self.state = "landed"
            self.status = "WAITING"
    
    def get_next_planned_destination(self) -> Optional[str]:
        """Get the next destination in the planned route."""
        if not self.planned_route or len(self.planned_route) < 2:
            return None
            
        if self.is_circular_route:
            # For circular routes, just move to next index
            next_index = (self.current_route_index + 1) % len(self.planned_route)
        else:
            # For non-circular routes, use ping-pong logic
            if not self.reverse_direction:
                next_index = self.current_route_index + 1
                if next_index >= len(self.planned_route):
                    # Switch direction and go back one step
                    self.reverse_direction = True
                    next_index = self.current_route_index - 1
            else:
                next_index = self.current_route_index - 1
                if next_index < 0:
                    # Switch direction and go forward one step
                    self.reverse_direction = False
                    next_index = self.current_route_index + 1
        
        if 0 <= next_index < len(self.planned_route):
            return self.planned_route[next_index]
        return None
    
    def advance_to_next_planned_destination(self):
        """Move to the next destination in planned route and update index."""
        next_dest_name = self.get_next_planned_destination()
        if not next_dest_name:
            return False
            
        # Update the route index
        if self.is_circular_route:
            self.current_route_index = (self.current_route_index + 1) % len(self.planned_route)
        else:
            if not self.reverse_direction:
                self.current_route_index += 1
                if self.current_route_index >= len(self.planned_route):
                    self.reverse_direction = True
                    self.current_route_index -= 2  # Go back two steps
            else:
                self.current_route_index -= 1
                if self.current_route_index < 0:
                    self.reverse_direction = False
                    self.current_route_index += 2  # Go forward two steps
        
        # Find target vertiport and start movement
        if next_dest_name in self.vertiports_map:
            target_vertiport = self.vertiports_map[next_dest_name]
            return self.set_destination_vertiport(target_vertiport)
        return False

class Vertiport(Drawable):
    """Visual vertiport with capacity management and drawing capabilities."""
    
    def __init__(self, x, y, capacity=2, name=""):
        self.x = x
        self.y = y
        self.capacity = capacity
        self.name = name
        self.occupied_slots = []
        self.hovering_queue = []
        # Initialize passenger management lists
        self.passengers_waiting = []
        self.passengers_arrived = []

    def can_land(self, vtol):
        """Check if there's available space for landing"""
        return len(self.occupied_slots) < self.capacity

    def request_landing(self, vtol):
        """Request landing permission"""
        if self.can_land(vtol):
            return True
        else:
            if vtol not in self.hovering_queue:
                self.hovering_queue.append(vtol)
            return False

    def land_vtol(self, vtol):
        """Execute VTOL landing at vertiport"""
        if self.can_land(vtol):
            self.occupied_slots.append(vtol)
            if vtol in self.hovering_queue:
                self.hovering_queue.remove(vtol)
            return True
        return False

    def takeoff_vtol(self, vtol):
        """Remove VTOL from vertiport (takeoff)"""
        if vtol in self.occupied_slots:
            self.occupied_slots.remove(vtol)
            print(f"🛫 VTOL {vtol.vtol_id}: Took off from {self.name}")
            
            # Reset the VTOL's anti-stuck timers
            vtol.landed_timer = 0
            vtol.hover_count = 0  # Reset hover count on successful takeoff
            
            # Notify all hovering VTOLs that space is available
            if self.hovering_queue:
                print(f"📢 {self.name}: Notifying {len(self.hovering_queue)} hovering VTOLs that space is available")
                for hovering_vtol in self.hovering_queue[:]:  # Copy list to avoid modification during iteration
                    hovering_vtol._can_attempt_landing = True
                    print(f"   → Notified VTOL {hovering_vtol.vtol_id}")
            return True
        return False

    def get_occupancy_info(self):
        """Return vertiport occupancy information"""
        return {
            'capacity': self.capacity,
            'occupied': len(self.occupied_slots),
            'available': self.capacity - len(self.occupied_slots),
            'hovering_count': len(self.hovering_queue),
            'occupancy_rate': len(self.occupied_slots) / self.capacity if self.capacity > 0 else 0
        }
    
    # Passenger management methods
    def get_passenger_spawn_position(self):
        """Return a random position inside the vertiport for spawning passengers"""
        import random
        return (
            random.randint(int(self.x + 5), int(self.x + 55)),
            random.randint(int(self.y + 5), int(self.y + 55))
        )
    
    def add_passenger(self, passenger):
        """Add a passenger to this vertiport's waiting area"""
        self.passengers_waiting.append(passenger)
        passenger.current_vertiport = self
        passenger.state = "waiting"
    
    def receive_passenger(self, passenger):
        """Receive a passenger that arrived at this vertiport"""
        self.passengers_arrived.append(passenger)
        passenger.current_vertiport = self
        passenger.arrive_at_destination()
    
    def get_passengers_for_destination(self, destination_name, count=1):
        """Get passengers waiting for a specific destination"""
        passengers = []
        for passenger in self.passengers_waiting[:]:
            if (passenger.destination_vertiport and 
                getattr(passenger.destination_vertiport, 'name', str(passenger.destination_vertiport)) == destination_name and 
                len(passengers) < count):
                passengers.append(passenger)
                self.passengers_waiting.remove(passenger)
        return passengers

    def draw(self, surface):
        """Draw the vertiport"""
        # Draw vertiport
        pygame.draw.rect(surface, VERTIPORT_COLOR, (self.x, self.y, 60, 60))
        pygame.draw.rect(surface, VERTIPORT_BORDER_COLOR, (self.x, self.y, 60, 60), 3)
        
        # Occupancy indicator
        occupancy = self.get_occupancy_info()
        if occupancy['occupied'] > 0:
            fill_height = int(60 * occupancy['occupancy_rate'])
            fill_rect = pygame.Rect(self.x + 2, self.y + 60 - fill_height - 2, 56, fill_height)
            overlay_color = (255, 200, 100) if occupancy['occupied'] < self.capacity else (255, 100, 100)
            pygame.draw.rect(surface, overlay_color, fill_rect)
        
        # Hovering VTOLs indicator
        if len(self.hovering_queue) > 0:
            hover_indicator = pygame.Rect(self.x + 50, self.y - 10, 15, 8)
            pygame.draw.rect(surface, (255, 255, 0), hover_indicator)
            if hasattr(pygame, 'font') and pygame.font.get_init():
                font = pygame.font.Font(None, 12)
                text = font.render(str(len(self.hovering_queue)), True, (0, 0, 0))
                surface.blit(text, (self.x + 52, self.y - 8))
        
        # Draw vertiport name (above and to the right)
        if hasattr(pygame, 'font') and pygame.font.get_init() and self.name:
            name_font = pygame.font.Font(None, 18)  # Slightly larger font for visibility
            name_text = name_font.render(self.name, True, (255, 255, 255))  # White text
            # Position: above (y - 25) and to the right (x + 65)
            name_x = self.x + 65
            name_y = self.y - 25
            
            # Add a semi-transparent background for better readability
            text_rect = name_text.get_rect()
            bg_rect = pygame.Rect(name_x - 2, name_y - 2, text_rect.width + 4, text_rect.height + 4)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(128)  # Semi-transparent
            bg_surface.fill((0, 0, 0))  # Black background
            surface.blit(bg_surface, (bg_rect.x, bg_rect.y))
            
            # Draw the text
            surface.blit(name_text, (name_x, name_y))
    
    def __str__(self):
        return self.name if self.name else f"VP({self.x},{self.y})"
    
    def __repr__(self):
        return self.__str__()

class Network(Drawable):
    """Network representation using NetworkX with CSV DataFrame input and visual capabilities."""
    
    def __init__(self, vertiports_df: pd.DataFrame, links_df: pd.DataFrame):
        """
        Initialize network from DataFrames.
        
        Args:
            vertiports_df: DataFrame with vertiport info (name, capacity, x, y)
            links_df: DataFrame with adjacency matrix ('x' indicates links)
        """
        self.graph = nx.DiGraph()
        self.vertiports = {}
        self.vertiport_objects = {}  # Store actual Vertiport objects
        
        # Visual properties
        self.link_color = NETWORK_LINK_COLOR
        self.link_highlight_color = NETWORK_LINK_HIGHLIGHT_COLOR
        self.link_width = 3
        self.vertiport_size = 60
        self.highlighted_path = []
        
        # Load vertiports from DataFrame
        for _, row in vertiports_df.iterrows():
            vertiport_id = row['name']
            x, y = float(row['x']), float(row['y'])
            capacity = int(row['capacity'])
            
            # Store vertiport info
            self.vertiports[vertiport_id] = {
                'capacity': capacity,
                'x': x,
                'y': y
            }
            
            # Create visual vertiport object
            vertiport_obj = Vertiport(x, y, capacity, vertiport_id)
            self.vertiport_objects[vertiport_id] = vertiport_obj
            
            # Add to NetworkX graph
            self.graph.add_node(vertiport_obj, 
                              capacity=capacity,
                              x=x,
                              y=y,
                              name=vertiport_id)
        
        # Load links from adjacency matrix DataFrame
        vertiport_names = [col for col in links_df.columns if col != 'X']
        
        for i in range(len(links_df)):
            origin_name = links_df.iloc[i]['X']
            
            for dest_col in vertiport_names:
                cell_value = links_df.iloc[i][dest_col]
                
                # If cell contains 'x', create unidirectional link from origin to destination
                if pd.notna(cell_value) and str(cell_value).strip().lower() == 'x':
                    destination_name = dest_col
                    
                    # Get vertiport objects
                    origin_obj = self.vertiport_objects[origin_name]
                    destination_obj = self.vertiport_objects[destination_name]
                    
                    # Calculate distance between vertiports
                    x1, y1 = origin_obj.x, origin_obj.y
                    x2, y2 = destination_obj.x, destination_obj.y
                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    
                    # Add unidirectional edge between objects
                    self.graph.add_edge(origin_obj, destination_obj, weight=distance, distance=distance)
    
    def get_shortest_path(self, origin: str, destination: str) -> List[str]:
        """Get shortest path between two vertiports."""
        try:
            # Get vertiport objects
            origin_obj = self.vertiport_objects.get(origin)
            destination_obj = self.vertiport_objects.get(destination)
            
            if not origin_obj or not destination_obj:
                return []
                
            path_objects = nx.shortest_path(self.graph, origin_obj, destination_obj, weight='weight')
            
            # Convert back to names
            path_names = []
            for obj in path_objects:
                if hasattr(obj, 'name'):
                    path_names.append(obj.name)
                else:
                    path_names.append(str(obj))
            
            return path_names
        except nx.NetworkXNoPath:
            return []
    
    def find_shortest_path(self, origin_obj, destination_obj):
        """Find shortest path between vertiport objects (for visual VTOLs)."""
        try:
            return nx.shortest_path(self.graph, origin_obj, destination_obj, weight='weight')
        except nx.NetworkXNoPath:
            return []
    
    def get_vertiports(self) -> List[str]:
        """Get list of all vertiport IDs."""
        return list(self.vertiport_objects.keys())
    
    def get_neighbors(self, vertiport: str) -> List[str]:
        """Get neighbors of a vertiport."""
        vertiport_obj = self.vertiport_objects.get(vertiport)
        if not vertiport_obj:
            return []
            
        neighbor_objects = list(self.graph.neighbors(vertiport_obj))
        return [obj.name for obj in neighbor_objects if hasattr(obj, 'name')]
    
    def has_edge(self, origin: str, destination: str) -> bool:
        """Check if there's a direct edge between two vertiports."""
        origin_obj = self.vertiport_objects.get(origin)
        destination_obj = self.vertiport_objects.get(destination)
        
        if not origin_obj or not destination_obj:
            return False
            
        return self.graph.has_edge(origin_obj, destination_obj)
    
    def get_vertiport_info(self, vertiport_id: str) -> Dict:
        """Get vertiport information."""
        return self.vertiports.get(vertiport_id, {})
    
    def get_vertiport_object(self, vertiport_id: str):
        """Get vertiport object by ID."""
        return self.vertiport_objects.get(vertiport_id)
    
    def is_bidirectional(self, origin: str, destination: str) -> bool:
        """Check if link between two vertiports is bidirectional."""
        return self.has_edge(origin, destination) and self.has_edge(destination, origin)
    
    def get_center_position(self, vertiport_obj):
        """Return the center position of a vertiport"""
        return (vertiport_obj.x + self.vertiport_size // 2, vertiport_obj.y + self.vertiport_size // 2)
    
    def highlight_path(self, path):
        """Set a path to be highlighted"""
        self.highlighted_path = path if path else []
    
    def clear_highlight(self):
        """Remove path highlighting"""
        self.highlighted_path = []
    
    def _is_link_highlighted(self, node1, node2):
        """Check if a link is in the highlighted path"""
        if not self.highlighted_path or len(self.highlighted_path) < 2:
            return False
        
        for i in range(len(self.highlighted_path) - 1):
            current = self.highlighted_path[i]
            next_node = self.highlighted_path[i + 1]
            if (current == node1 and next_node == node2) or (current == node2 and next_node == node1):
                return True
        return False
    
    def _draw_arrow(self, surface, start_pos, end_pos, color):
        """Draw an arrow to indicate direction"""
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
        
        dx /= length
        dy /= length
        
        arrow_length = 15
        arrow_angle = math.pi / 6
        
        arrow_pos_x = end_pos[0] - dx * 20
        arrow_pos_y = end_pos[1] - dy * 20
        
        arrow_x1 = arrow_pos_x - arrow_length * (dx * math.cos(arrow_angle) - dy * math.sin(arrow_angle))
        arrow_y1 = arrow_pos_y - arrow_length * (dy * math.cos(arrow_angle) + dx * math.sin(arrow_angle))
        
        arrow_x2 = arrow_pos_x - arrow_length * (dx * math.cos(-arrow_angle) - dy * math.sin(-arrow_angle))
        arrow_y2 = arrow_pos_y - arrow_length * (dy * math.cos(-arrow_angle) + dx * math.sin(-arrow_angle))
        
        pygame.draw.polygon(surface, color, [
            (arrow_pos_x, arrow_pos_y),
            (arrow_x1, arrow_y1),
            (arrow_x2, arrow_y2)
        ])
    
    def draw(self, surface):
        """Draw the network"""
        # Draw connections
        drawn_edges = set()
        
        for edge in self.graph.edges():
            node1, node2 = edge
            
            # Avoid drawing the same undirected edge twice
            edge_key = tuple(sorted([id(node1), id(node2)]))
            if edge_key in drawn_edges:
                continue
            drawn_edges.add(edge_key)
            
            start_pos = self.get_center_position(node1)
            end_pos = self.get_center_position(node2)
            
            is_highlighted = self._is_link_highlighted(node1, node2)
            link_color = self.link_highlight_color if is_highlighted else self.link_color
            link_width = self.link_width + 2 if is_highlighted else self.link_width
            
            pygame.draw.line(surface, link_color, start_pos, end_pos, link_width)
            
            # Draw arrow for directed graph
            if not is_highlighted:
                self._draw_arrow(surface, start_pos, end_pos, link_color)
        
        # Draw vertiports
        for vertiport_obj in self.vertiport_objects.values():
            vertiport_obj.draw(surface)
    
    @property
    def nodes(self):
        """Property for compatibility with visual VTOLs"""
        return set(self.vertiport_objects.values())

class Simulation:
    """Main simulation class with DataFrame input support and JSON route integration."""
    
    def __init__(self, vertiports_df: pd.DataFrame, links_df: pd.DataFrame, 
                 vtol_routes_file: Optional[str] = None):
        """
        Initialize simulation with DataFrames and optional VTOL routes.
        
        Args:
            vertiports_df: DataFrame with vertiport info
            links_df: DataFrame with adjacency matrix
            vtol_routes_file: Optional path to JSON file with VTOL routes
        """
        self.network = Network(vertiports_df, links_df)
        self.vtols = []
        self.current_time = 0
        self.matriz_od: Optional[MatrizOD] = None  # Matriz origem-destino para demanda de passageiros
        self.vertiport_capacities = {}
        self.vtol_routes_config = []
        
        # Initialize vertiport capacities
        for vertiport_id in self.network.get_vertiports():
            vertiport_info = self.network.get_vertiport_info(vertiport_id)
            self.vertiport_capacities[vertiport_id] = vertiport_info.get('capacity', 1)
        
        # Load VTOL routes if provided
        if vtol_routes_file and os.path.exists(vtol_routes_file):
            self.load_vtol_routes(vtol_routes_file)
    
    def load_vtol_routes(self, routes_file: str):
        """Load VTOL routes from JSON file."""
        try:
            with open(routes_file, 'r', encoding='utf-8') as f:
                self.vtol_routes_config = json.load(f)
            print(f"Loaded {len(self.vtol_routes_config)} VTOL routes from {routes_file}")
        except Exception as e:
            print(f"Error loading VTOL routes: {e}")
            self.vtol_routes_config = []
    
    def create_vtols_from_routes(self):
        """Create VTOLs based on loaded routes configuration."""
        if not self.vtol_routes_config:
            print("No VTOL routes configuration loaded.")
            return
        
        # Create vertiports map for VTOLs
        vertiports_map = {}
        for vp_id, vp_obj in self.network.vertiport_objects.items():
            vertiports_map[vp_id] = vp_obj
        
        created_count = 0
        for route_config in self.vtol_routes_config:
            vtol_id = route_config.get('vtol_id', f'VTOL-{created_count+1}')
            route = route_config.get('route', [])
            
            if len(route) < 2:
                print(f"Skipping VTOL {vtol_id}: route too short")
                continue
            
            # Validate that all vertiports in route exist
            invalid_vertiports = [vp for vp in route if vp not in vertiports_map]
            if invalid_vertiports:
                print(f"Skipping VTOL {vtol_id}: invalid vertiports {invalid_vertiports}")
                continue
            
            # Create VTOL at first vertiport in route
            first_vp = vertiports_map[route[0]]
            vtol = VTOL(first_vp.x + 30, first_vp.y + 30, self.network)
            vtol.vtol_id = vtol_id
            vtol.set_planned_route(route, vertiports_map)
            
            self.vtols.append(vtol)
            created_count += 1
            print(f"Created VTOL {vtol_id} with route: {' → '.join(route)}")
        
        print(f"Successfully created {created_count} VTOLs from routes configuration")
    
    def start_planned_routes(self):
        """Start all VTOLs on their planned routes."""
        for vtol in self.vtols:
            if hasattr(vtol, 'planned_route') and vtol.planned_route and vtol.is_circulating:
                if vtol.advance_to_next_planned_destination():
                    vtol.status = "FLYING"
                    print(f"Started VTOL {vtol.vtol_id} on planned route")
    
    def add_vtol(self, vtol_id: int, origin: str, destination: str, 
                 departure_time: int, passengers: int = 1) -> bool:
        """Add a VTOL to the simulation."""
        # Check if vertiports exist
        if origin not in self.network.get_vertiports():
            return False
        if destination not in self.network.get_vertiports():
            return False
        
        # Check if route exists
        route = self.network.get_shortest_path(origin, destination)
        if not route:
            return False
        
        # Get vertiport objects for visual VTOL
        origin_obj = self.network.get_vertiport_object(origin)
        destination_obj = self.network.get_vertiport_object(destination)
        
        if not origin_obj or not destination_obj:
            return False
        
        # Create visual VTOL
        vtol = VTOL(origin_obj.x + 30, origin_obj.y + 30, self.network)
        vtol.vtol_id = str(vtol_id)
        vtol.departure_time = departure_time
        vtol.passengers = passengers
        vtol.current_vertiport = origin_obj
        vtol.status = "WAITING"
        vtol.state = "landed"
        
        # Set final destination for the journey
        vtol.final_destination = destination_obj
        vtol.journey_route = route  # Store string route for compatibility
        vtol.flight_path = [self.network.get_vertiport_object(vp_name) for vp_name in route]
        
        self.vtols.append(vtol)
        return True
    
    def simulate_step(self):
        """Execute one simulation step."""
        self.current_time += 1
        
        # Reset vertiport capacities
        for vertiport_id in self.network.get_vertiports():
            vertiport_info = self.network.get_vertiport_info(vertiport_id)
            self.vertiport_capacities[vertiport_id] = vertiport_info.get('capacity', 1)
        
        # Count VTOLs at each vertiport
        vertiport_usage = {}
        for vtol in self.vtols:
            if vtol.status == "WAITING" or vtol.state == "landed":
                # Get vertiport name from current vertiport object
                if hasattr(vtol.current_vertiport, 'name'):
                    vertiport_name = vtol.current_vertiport.name
                else:
                    vertiport_name = str(vtol.current_vertiport)
                vertiport_usage[vertiport_name] = vertiport_usage.get(vertiport_name, 0) + 1
        
        # Update available capacities
        for vertiport, usage in vertiport_usage.items():
            max_capacity = self.network.get_vertiport_info(vertiport).get('capacity', 1)
            self.vertiport_capacities[vertiport] = max(0, max_capacity - usage)
        
        # Process each VTOL
        for vtol in self.vtols:
            # Handle VTOLs with planned routes (from JSON)
            if hasattr(vtol, 'planned_route') and vtol.planned_route and vtol.is_circulating:
                self._process_planned_route_vtol(vtol)
            else:
                # Handle traditional simulation VTOLs
                self._process_simulation_vtol(vtol)
        
        # Update visual VTOLs
        for vtol in self.vtols:
            if hasattr(vtol, 'update'):
                vtol.update()
    
    def _process_planned_route_vtol(self, vtol):
        """Process a VTOL following a planned route."""
        if vtol.state == "landed" and vtol.status != "FLYING":
            # VTOL is landed and ready to move to next destination
            if vtol.advance_to_next_planned_destination():
                vtol.status = "FLYING"
                # Update departure time for compatibility
                vtol.departure_time = self.current_time
    
    def _process_simulation_vtol(self, vtol):
        """Process a traditional simulation VTOL."""
        # Skip VTOLs that have already reached their final destination
        if vtol.status == "LANDED":
            return
        
        if vtol.can_depart(self.current_time, self.vertiport_capacities):
            # Find next vertiport in route
            if hasattr(vtol, 'journey_route') and vtol.journey_route:
                current_vertiport_name = vtol.current_vertiport.name if hasattr(vtol.current_vertiport, 'name') else str(vtol.current_vertiport)
                try:
                    current_index = vtol.journey_route.index(current_vertiport_name)
                    if current_index < len(vtol.journey_route) - 1:
                        next_vertiport_name = vtol.journey_route[current_index + 1]
                        vtol.fly_to_next_vertiport(next_vertiport_name)
                except ValueError:
                    # Current vertiport not in route, start from beginning
                    if len(vtol.journey_route) > 0:
                        vtol.fly_to_next_vertiport(vtol.journey_route[0])
        elif (vtol.status == "WAITING" or vtol.state == "landed") and vtol.can_hover():
            vtol.hover()
    
    def run_simulation(self, max_time: int = 100):
        """Run simulation for specified time steps."""
        for _ in range(max_time):
            self.simulate_step()
            
            # Check if all VTOLs have landed (for traditional simulation)
            if all(vtol.status == "LANDED" for vtol in self.vtols if not (hasattr(vtol, 'is_circulating') and vtol.is_circulating)):
                break
        
        return self.get_simulation_results()
    
    def get_simulation_results(self) -> Dict:
        """Get simulation results."""
        results = {
            'total_vtols': len(self.vtols),
            'landed_vtols': sum(1 for vtol in self.vtols if vtol.status == "LANDED"),
            'waiting_vtols': sum(1 for vtol in self.vtols if vtol.status == "WAITING"),
            'flying_vtols': sum(1 for vtol in self.vtols if vtol.status == "FLYING"),
            'current_time': self.current_time,
            'vtol_details': []
        }
        
        for vtol in self.vtols:
            # Get current vertiport name
            current_vp_name = vtol.current_vertiport
            if hasattr(vtol.current_vertiport, 'name'):
                current_vp_name = vtol.current_vertiport.name
            elif isinstance(vtol.current_vertiport, str):
                current_vp_name = vtol.current_vertiport
            else:
                current_vp_name = str(vtol.current_vertiport)
            
            # Get route information
            if hasattr(vtol, 'planned_route') and vtol.planned_route:
                # For planned route VTOLs
                origin_name = vtol.planned_route[0] if vtol.planned_route else "Unknown"
                dest_name = vtol.planned_route[-1] if vtol.planned_route else "Unknown"
                route = vtol.planned_route
            else:
                # For traditional simulation VTOLs
                origin_name = vtol.journey_route[0] if vtol.journey_route else "Unknown"
                
                # Get destination name
                if hasattr(vtol, 'final_destination') and vtol.final_destination:
                    if hasattr(vtol.final_destination, 'name'):
                        dest_name = vtol.final_destination.name
                    else:
                        dest_name = str(vtol.final_destination)
                elif hasattr(vtol.destination_vertiport, 'name'):
                    dest_name = vtol.destination_vertiport.name
                elif isinstance(vtol.destination_vertiport, str):
                    dest_name = vtol.destination_vertiport
                else:
                    dest_name = str(vtol.destination_vertiport) if vtol.destination_vertiport else "Unknown"
                
                route = vtol.journey_route
            
            results['vtol_details'].append({
                'id': vtol.vtol_id,
                'origin': origin_name,
                'destination': dest_name,
                'current_vertiport': current_vp_name,
                'status': vtol.status,
                'hover_count': vtol.hover_count,
                'route': route,
                'is_planned_route': hasattr(vtol, 'planned_route') and vtol.planned_route and vtol.is_circulating
            })
        
        return results

# --- Interface de Usuário Pygame ---
class SimulatorUI:
    """Interface de usuário principal usando Pygame"""
    
    def __init__(self, fps: bool = True, demand_file=None):
        self.title_window = "UAM Network Simulator with Passengers"
        self.fps = fps
        self._last_time_update = 0  # Initialize time tracking
        
        # Inicializa pygame
        pygame.init()
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.title_window)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        # Cria simulação básica para demo de passageiros
        self.sim = self.create_demo_simulation(demand_file)

    def create_demo_simulation(self, demand_file):
        """Cria uma simulação de demonstração simples"""
        # Dados básicos para demo
        vertiports_data = {
            'name': ['V1', 'V2', 'V3', 'V4', 'V5'],
            'capacity': [2, 2, 2, 2, 2],
            'x': [100, 300, 500, 700, 400],
            'y': [100, 150, 200, 100, 400]
        }
        
        links_data = {
            'X': ['V1', 'V2', 'V3', 'V4', 'V5'],
            'V1': ['', 'x', 'x', '', ''],
            'V2': ['x', '', 'x', 'x', 'x'],
            'V3': ['x', 'x', '', 'x', 'x'],
            'V4': ['', 'x', 'x', '', 'x'],
            'V5': ['', 'x', 'x', 'x', '']
        }
        
        vertiports_df = pd.DataFrame(vertiports_data)
        links_df = pd.DataFrame(links_data)
        
        # Cria simulação com rede básica
        sim = Simulation(vertiports_df, links_df)
        
        # Adiciona matriz de demanda se fornecida
        if demand_file:
            sim.matriz_od = MatrizOD(demand_file)
        
        return sim
    
    def run(self):
        """Loop principal da simulação"""
        running = True
        frame_count = 0
        
        while running:
            self.clock.tick(FPS)
            if self.fps:
                pygame.display.set_caption(f"{self.title_window} - FPS: {self.clock.get_fps():.2f}")

            # Processa eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Simula passageiros baseado na demanda
            if hasattr(self.sim, 'matriz_od') and self.sim.matriz_od:
                self.process_passenger_demand()
            
            # Adiciona VTOLs ocasionalmente para demonstração
            if frame_count % 300 == 0:  # A cada 5 segundos
                self.spawn_demo_vtol()
            
            # Atualiza simulação
            self.sim.simulate_step()
            
            # Desenha tela
            self.screen.fill((30, 30, 30))
            self.draw_simulation()
            
            pygame.display.flip()
            frame_count += 1

        pygame.quit()
        sys.exit()
    
    def process_passenger_demand(self):
        """Processa demanda de passageiros baseada no tempo"""
        if not hasattr(self.sim, 'matriz_od') or not self.sim.matriz_od:
            return
            
        # Avança tempo a cada segundo
        current_time = pygame.time.get_ticks()
        if current_time - self._last_time_update > 1000:  # 1 segundo
            self.sim.matriz_od.advance_time(1)  # Avança 1 minuto
            self._last_time_update = current_time
        
        # Gera passageiros baseado na demanda atual
        current_demands = self.sim.matriz_od.get_current_demand()
        
        for demand in current_demands:
            # Pequena chance de gerar passageiro a cada frame
            if current_time % 30 == 0:  # A cada meio segundo
                if len(current_demands) > 0:  # Se há demanda
                    self.spawn_passenger(demand['origem'], demand['destino'])
    
    def spawn_passenger(self, origin_name, destination_name):
        """Spawna um passageiro nos vertiportos"""
        # Por enquanto, apenas imprime a demanda (simulação visual básica)
        print(f"Passenger demand: {origin_name} → {destination_name}")
    
    def spawn_demo_vtol(self):
        """Spawna um VTOL para demonstração"""
        if hasattr(self.sim, 'network') and self.sim.network:
            vertiports = list(self.sim.network.vertiport_objects.values())
            if len(vertiports) >= 2:
                import random
                origin = random.choice(vertiports)
                destination = random.choice([vp for vp in vertiports if vp != origin])
                
                # Cria VTOL simples
                vtol = VTOL(origin.x + 30, origin.y + 30, self.sim.network)
                vtol.current_vertiport = origin
                vtol.set_destination_vertiport(destination)
                
                self.sim.vtols.append(vtol)
    
    def draw_simulation(self):
        """Desenha a simulação na tela"""
        # Desenha rede se disponível
        if hasattr(self.sim, 'network') and self.sim.network:
            self.sim.network.draw(self.screen)
        
        # Desenha VTOLs
        if hasattr(self.sim, 'vtols'):
            for vtol in self.sim.vtols:
                if hasattr(vtol, 'draw'):
                    vtol.draw(self.screen)
        
        # Desenha informações de tempo se disponível
        if hasattr(self.sim, 'matriz_od') and self.sim.matriz_od:
            font = pygame.font.Font(None, 24)
            time_text = f"Time: {self.sim.matriz_od.get_current_time_str()}"
            time_surface = font.render(time_text, True, (255, 255, 255))
            self.screen.blit(time_surface, (10, 10))
            
            # Mostra demanda atual
            current_demands = self.sim.matriz_od.get_current_demand()
            if current_demands:
                y_offset = 35
                small_font = pygame.font.Font(None, 18)
                demand_text = f"Current demand routes: {len(current_demands)}"
                demand_surface = small_font.render(demand_text, True, (200, 200, 200))
                self.screen.blit(demand_surface, (10, y_offset))
                
                # Lista algumas demandas
                for i, demand in enumerate(current_demands[:5]):  # Mostra até 5
                    y_offset += 20
                    route_text = f"{demand['origem']} → {demand['destino']}: {demand['demanda']}"
                    route_surface = small_font.render(route_text, True, (150, 150, 255))
                    self.screen.blit(route_surface, (15, y_offset))
        
        # Informações de controle
        font = pygame.font.Font(None, 20)
        control_text = "ESC: Exit | Demo running..."
        control_surface = font.render(control_text, True, (200, 200, 200))
        self.screen.blit(control_surface, (10, HEIGHT - 30))

if __name__ == "__main__":
    # Demo básico
    demand_file = "src/data/demanda_passageiros.csv"
    app = SimulatorUI(fps=True, demand_file=demand_file)
    app.run()
