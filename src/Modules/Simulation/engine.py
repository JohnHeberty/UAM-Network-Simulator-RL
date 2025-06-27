import pygame
import random
from abc import ABC, abstractmethod
import sys

# Constantes
WIDTH, HEIGHT = 1000, 800
FPS = 60
EVTOL_COLOR = (100, 200, 255)
PERSON_COLOR = (255, 100, 100)

class PathPlanner(ABC):
    @abstractmethod
    def get_next_point(self, origin, destination):
        pass

class StraightLinePathPlanner(PathPlanner):
    def __init__(self, step=1):
        self.step = step

    def get_next_point(self, origin, destination):
        ox, oy = origin
        dx, dy = destination
        vx, vy = dx - ox, dy - oy
        dist = (vx ** 2 + vy ** 2) ** 0.5
        if dist == 0 or dist < self.step:
            return destination
        nx = ox + self.step * vx / dist
        ny = oy + self.step * vy / dist
        return int(nx), int(ny)

class Drawable(ABC):
    @abstractmethod
    def draw(self, surface):
        pass

# --- Princípio da Responsabilidade Única (SRP) ---
class Person(Drawable):
    def __init__(self, x, y):
        self.xo = x # origin
        self.xd = self.xo # destination
        self.bxo = self.xo # before
        self.yo = y # origin
        self.yd = self.yo # destination
        self.byo = self.yo # before
        self.path_planner = StraightLinePathPlanner()
        self.clean = False

    def set_destination(self, xd, yd):
        if (self.xd, self.yd) == (self.xo, self.yo):
            self.xd = xd
            self.yd = yd

    def draw(self, surface):
        # Salva a posição anterior antes de atualizar
        self.bxo, self.byo = self.xo, self.yo
        self.xo, self.yo = self.path_planner.get_next_point((self.xo, self.yo), (self.xd, self.yd))
        pygame.draw.circle(surface, PERSON_COLOR, (self.xo, self.yo), 3)
        # Verifica se chegou ao destino ou se parou de se mover
        if (self.xo, self.yo) == (self.xd, self.yd) or (self.bxo, self.byo) == (self.xo, self.yo):
            self.clean = True

# --- Classe EVTOL seguindo Princípio Aberto/Fechado (OCP) ---
class VTOL(Drawable):
    def __init__(self, x, y):
        self.xo = x
        self.xd = self.xo
        self.bxo = self.xo  # before position
        self.yo = y
        self.yd = self.yo
        self.byo = self.yo  # before position
        self.clean = False

        self.state = "landed"
        self.before_state = self.state
        self.base_width = 7
        self.base_scale = 1
        self.atual_scale = self.base_scale
        self.loked_state = False

        self.scale_landed = 0.4
        self.landing_to_landed = [
            row/100 for row in range(int(self.scale_landed * 100), self.base_width * 100, 1)
        ]
        self.landed_to_taking_off = [
            row/100 for row in range(int(self.scale_landed * 100), self.base_width * 100, 1)
        ]
        self.landed_to_taking_off.reverse()
        self.iterator_unloked_state = 0
        self.list_scale = []

        self.evtol_scale = self.scale_landed

        self.path_planner = StraightLinePathPlanner()

    def get_choices(self):
        return ["landed", "taking_off", "flying", "landing"]

    def set_destination(self, xd, yd):
        if (self.xd, self.yd) == (self.xo, self.yo):
            self.xd = xd
            self.yd = yd

    def update_state(self, new_state):
        if self.loked_state:
            return
        update = False
        if self.state == new_state:
            return
        elif self.state == "landed" and new_state == "taking_off": # UP-SCALE
            update = True
            self.loked_state = True
            self.iterator_unloked_state = len(self.landed_to_taking_off)
            self.list_scale = self.landed_to_taking_off
        elif self.state == "taking_off" and new_state == "flying":
            update = True
        elif self.state == "flying" and new_state == "landing":
            update = True
        elif self.state == "landing" and new_state == "landed": # DOWN-SCALE
            update = True
            self.loked_state = True
            self.iterator_unloked_state = len(self.landing_to_landed)
            self.list_scale = self.landing_to_landed
        if update:
            self.before_state = self.state
            self.state = new_state

    def draw(self, surface):
        if self.loked_state:
            self.iterator_unloked_state -= 1
            self.atual_scale = self.list_scale[self.iterator_unloked_state]
            if self.iterator_unloked_state <= 0:
                self.loked_state = False
                self.iterator_unloked_state = 0
        side = int(self.base_width * self.atual_scale)
        # Salva a posição anterior antes de atualizar
        self.bxo, self.byo = self.xo, self.yo
        self.xo, self.yo = self.path_planner.get_next_point((self.xo, self.yo), (self.xd, self.yd))
        pygame.draw.rect(surface, EVTOL_COLOR, (self.xo, self.yo, side, side * (3/4) )) # width, height
        # Verifica se chegou ao destino ou se parou de se mover
        if (self.xo, self.yo) == (self.xd, self.yd) or (self.bxo, self.byo) == (self.xo, self.yo):
            self.clean = True

# --- Princípio da Segregação de Interfaces (ISP) ---
class Vertiport(Drawable):
    def __init__(self, x, y, capacity=2):
        self.x = x
        self.y = y
        self.capacity = capacity

    def draw(self, surface):
        pygame.draw.rect(surface, (180, 180, 180), (self.x, self.y, 60, 60), 2)

# --- Princípio da Inversão de Dependência (DIP) ---
class Simulation:
    def __init__(self):
        self.evtols = []
        self.people = []
        self.vertiports = []

    def spawn_vertiport(self, x=None, y=None):
        x = random.randint(50, WIDTH - 50) if x is None else x
        y = random.randint(50, HEIGHT - 50) if y is None else y
        self.vertiports.append(Vertiport(x, y))

    def spawn_evtol(self, xo=None, yo=None, xd=None, yd=None):
        xo = random.randint(50, WIDTH - 50) if xo is None else xo
        yo = random.randint(50, HEIGHT - 50) if yo is None else yo
        xd = random.randint(50, WIDTH - 50) if xd is None else xd
        yd = random.randint(50, HEIGHT - 50) if yd is None else yd
        vtol = VTOL(xo, yo)
        vtol.set_destination(xd, yd)
        self.evtols.append(vtol)

    def spawn_person(self, xo=None, yo=None, xd=None, yd=None):
        xo = random.randint(50, WIDTH - 50) if xo is None else xo
        yo = random.randint(50, HEIGHT - 50) if yo is None else yo
        xd = random.randint(50, WIDTH - 50) if xd is None else xd
        yd = random.randint(50, HEIGHT - 50) if yd is None else yd
        p = Person(xo, yo)
        p.set_destination(xd, yd)
        self.people.append(p)

    def update(self):
        for evtol in self.evtols:
            # alterna estado para simulação de exemplo
            evtol.update_state(random.choice(evtol.get_choices()))

    def draw(self, surface):
        for v in self.vertiports:
            v.draw(surface)
        for p in self.people:
            if not p.clean: # Se a pessoa não chegou ao destino, desenha
                p.draw(surface)
            else: # Se chegou ao destino, remove a pessoa
                self.people.remove(p)
        for e in self.evtols:
            if not e.clean: # Se o VTOL não chegou ao destino, desenha
                e.draw(surface)
            else: # Se chegou ao destino, remove o VTOL
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

            # Simula chegada de pessoas e evtols
            if random.random() < 0.05:
                self.sim.spawn_person()
            if random.random() < 0.05:
                self.sim.spawn_evtol()

            self.sim.update()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    app = SimulatorUI()
    app.run()
