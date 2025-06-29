# UAM Network Simulator - Modern Architecture

---

## 🎯 **Status do Projeto: Versão 3.0 - Refatorado com DataFrame CSV + Pygame**

✅ **Arquitetura moderna implementada**  
✅ **Configuração via CSV DataFrame**: Entrada de dados via `matriz_od_info.csv` e `matriz_od_link.csv`  
✅ **Controle robusto de capacidade dos vertiportos**  
✅ **Sistema de hovering inteligente**  
✅ **Organização limpa do código**  
✅ **Visualização pygame**: Interface gráfica completa em tempo real  
✅ **NetworkX**: Integração com NetworkX para roteamento avançado e análise de grafos  
✅ **Links direcionais**: Suporte completo para redes direcionais e bidirecionais  
✅ **Testes abrangentes**: Suite completa de testes organizados
✅ **Sistema de passageiros**: Passageiros gerados com base em demanda temporal do CSV
✅ **Embarque/desembarque automatizado**: Passageiros embarcam e desembarcam nos VTOLs automaticamente
✅ **Animações visuais**: Passageiros sobem verticalmente e desaparecem ao sair dos vertiportos

---

## 🧠 **Objetivo do Simulador**

Simular a operação de uma rede de eVTOLs (Urban Air Mobility) com diferentes configurações de vertiportos e otimizar suas localizações, capacidades e desempenho operacional. O simulador implementa:

* ✅ **Configuração via CSV**: Vertiportos e links definidos em arquivos CSV com pandas DataFrame
* ✅ **Controle de capacidade**: Vertiportos com capacidade limitada e fila de espera
* ✅ **Sistema de hovering**: VTOLs pairam quando não há vaga e pousam automaticamente quando liberada
* ✅ **Separação de responsabilidades**: Código de produção em `src/`, testes em `tests/`
* ✅ **Visualização em tempo real**: Interface pygame completa para monitoramento gráfico
* ✅ **Roteamento NetworkX**: Algoritmos avançados de grafos para encontrar rotas ótimas
* ✅ **Links direcionais**: Suporte para redes unidirecionais e bidirecionais
* ✅ **Demos interativas**: Scripts demonstrativos para diferentes funcionalidades
* ✅ **Sistema de passageiros**: Passageiros gerados com base em demanda temporal do CSV
* ✅ **Embarque/desembarque automatizado**: Passageiros embarcam e desembarcam nos VTOLs automaticamente
* ✅ **Animações visuais**: Passageiros sobem verticalmente e desaparecem ao sair dos vertiportos

---

## 📁 **Estrutura do Projeto**

```plaintext
UAM-Network-Simulator-RL/
├── src/                          # Código de produção
│   ├── __init__.py
│   ├── Modules/
│   │   ├── __init__.py
│   │   └── Simulation/
│   │       ├── __init__.py
│   │       └── engine.py         # Motor principal (CSV + pygame)
│   └── data/                     # Dados CSV
│       ├── matriz_od_info.csv    # Informações dos vertiportos
│       ├── matriz_od_link.csv    # Matriz de adjacência direcional
│       ├── demanda_passageiros.csv # Demanda temporal de passageiros
│       └── vtol_routes.json      # Rotas históricas (compatibilidade)
├── tests/                        # Testes organizados
│   ├── README.md                 # Documentação dos testes
│   ├── __init__.py
│   ├── test_simulation.py        # Teste principal do engine
│   ├── test_csv_integration.py   # Teste de integração CSV
│   ├── test_pygame_components.py # Teste de componentes pygame
│   └── test_pygame_headless.py   # Teste headless (sem display)
├── demo_pygame_visualization.py  # Demo interativa completa
├── demo_csv_routing.py           # Demo de roteamento CSV
├── demo_vtol_routing.py          # Demo de rotas VTOL
├── requirements.txt              # Dependências do projeto
└── README.md                     # Esta documentação
```

---

## 🗂️ **Configuração de Dados**

### **1. `matriz_od_info.csv` - Informações dos Vertiportos**
```csv
name;capacity;x;y;
V1;2;200;150;
V2;2;500;200;
V3;2;300;400;
V4;2;700;350;
V5;2;600;550;
```

**Campos:**
- `name`: ID único do vertiport
- `capacity`: Capacidade máxima de VTOLs simultâneos  
- `x`, `y`: Coordenadas na tela para visualização

### **2. `matriz_od_link.csv` - Matriz de Links Direcionais**
```csv
X;V1;V2;V3;V4;V5
V1;;x;x;;
V2;x;;x;x;
V3;;;x;;x
V4;;;x;;x
V5;;;x;;;
```

**Como Interpretar:**
- **Linhas = Origem**, **Colunas = Destino**
- `x` = Link permitido nesta direção
- Vazio = Sem link nesta direção

**Exemplo - Links do arquivo acima:**
- V1 → V2: ✅ Permitido
- V2 → V1: ✅ Permitido (bidirecional)
- V1 → V3: ✅ Permitido  
- V3 → V1: ❌ NÃO permitido (unidirecional)
- V5 → V3: ✅ Permitido
- V3 → V5: ❌ NÃO permitido (unidirecional)
│   ├── test_simulation.py        # Teste principal do engine
│   ├── test_csv_integration.py   # Integração CSV
│   ├── test_pygame_components.py # Componentes pygame
│   └── test_pygame_headless.py   # Testes visuais headless
│   ├── test_*.py                 # Testes funcionais
│   ├── demo_*.py                 # Demonstrações
│   └── generate_od_data.py       # Utilitários
├── fix_imports.py                # Script de correção de imports
└── README.md                     # Este arquivo
```

---

## 👥 **Sistema de Passageiros**

O simulador inclui um sistema completo de passageiros baseado em demanda temporal:

### **Funcionalidades do Sistema de Passageiros**

1. **Geração Baseada em Demanda**
   - Passageiros são spawneados automaticamente com base no arquivo `demanda_passageiros.csv`
   - A demanda varia por horário do dia (ex: maior demanda em horários de rush)
   - Passageiros são gerados apenas dentro dos vertiportos (nunca fora)

2. **Estados dos Passageiros**
   - **waiting**: Aguardando no vertiporto de origem
   - **boarding**: Embarcando no VTOL
   - **flying**: Voando no VTOL para o destino
   - **arrived**: Chegou ao destino
   - **leaving**: Saindo do vertiporto (animação de subida)

3. **Embarque e Desembarque Automatizado**
   - VTOLs automaticamente embarcam passageiros ao decolar
   - Apenas passageiros com destino correto embarcam
   - Desembarque automático ao chegar no destino
   - Capacidade limitada por VTOL (máximo 4 passageiros)

4. **Animações Visuais**
   - Passageiros são exibidos como círculos coloridos
   - Cores diferentes para cada estado (vermelho=waiting, amarelo=boarding, etc.)
   - Animação de saída: passageiros sobem verticalmente e desaparecem
   - Contador visual de passageiros nos VTOLs

### **Formato do CSV de Demanda**

```csv
vertiport_origem,vertiport_destino,hora_inicio,hora_fim,demanda
V1,V2,04:00,05:00,15
V2,V3,07:00,09:00,25
V3,V1,17:00,19:00,20
```

### **Uso do Sistema de Passageiros**

```python
from src.Modules.Simulation.engine import MatrizOD

# Adicionar sistema de passageiros à simulação
simulation.matriz_od = MatrizOD('src/data/demanda_passageiros.csv')
simulation.matriz_od.current_time_minutes = 4 * 60  # Iniciar às 04:00

# Spawnar passageiros baseado na demanda atual
current_demands = simulation.matriz_od.get_current_demand()
for demand in current_demands:
    # Lógica de spawn implementada no demo_main.py
    spawn_passengers_from_demand(simulation)
```

---

## 🏗️ **Arquitetura SOLID Implementada**

O simulador agora segue rigorosamente os princípios SOLID:

### **Single Responsibility Principle (SRP)**
- `VTOL`: Gerencia apenas estado e movimento de um VTOL
- `Vertiport`: Controla apenas capacidade e operações de pouso/decolagem  
- `Network`: Administra apenas a topologia da rede
- `Simulation`: Coordena apenas a simulação geral

### **Open/Closed Principle (OCP)**
- Interfaces `Drawable`, `Movable`, `Stateful`, `Cleanable`
- Sistema extensível via composição e polimorfismo

### **Liskov Substitution Principle (LSP)**
- Todas as implementações respeitam os contratos das interfaces
- Substituição transparente de componentes

### **Interface Segregation Principle (ISP)**
- Interfaces específicas e focadas: `PathPlanner`, `NetworkManager`
- Clientes dependem apenas do que precisam

### **Dependency Inversion Principle (DIP)**
- Simulação depende de abstrações, não implementações
- Inversão de controle via injeção de dependência

```plaintext
┌─────────────────────────────────┐
│         Simulation              │◄── Coordenação geral
├─────────────────────────────────┤
│  ┌─────────┐ ┌──────────────┐   │
│  │ Network │ │ MatrizOD     │   │◄── Componentes especializados  
│  └─────────┘ └──────────────┘   │
├─────────────────────────────────┤
│  ┌─────────┐ ┌──────────────┐   │
│  │  VTOL   │ │  Vertiport   │   │◄── Entidades do domínio
---

## 🚀 **Como Usar**

### **Instalação e Requisitos**

```bash
# Instalar dependências
pip install -r requirements.txt

# Requisitos principais:
# - pygame (interface gráfica)
# - pandas (manipulação de dados CSV)
# - networkx (algoritmos de grafos)
```

### **Execução Básica**

```python
import pygame
import pandas as pd
from src.Modules.Simulation.engine import Simulation

# Carregar dados CSV
vertiports_df = pd.read_csv('src/data/matriz_od_info.csv', sep=';')
links_df = pd.read_csv('src/data/matriz_od_link.csv', sep=';')

# Criar simulação
simulation = Simulation(vertiports_df, links_df)

# Adicionar VTOLs
simulation.add_vtol(1, "V1", "V5", 0, 1)  # id, origem, destino, start_time, speed

# Executar simulação (modo headless)
for step in range(100):
    simulation.simulate_step()
    print(f"Step {step}: {len(simulation.vtols)} VTOLs ativos")
```

### **Execução com Visualização Pygame**

```python
import pygame
from src.Modules.Simulation.engine import Simulation

# Inicializar pygame
pygame.init()
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("UAM Network Simulator")

# Carregar dados e criar simulação
vertiports_df = pd.read_csv('src/data/matriz_od_info.csv', sep=';')
links_df = pd.read_csv('src/data/matriz_od_link.csv', sep=';')
simulation = Simulation(vertiports_df, links_df)

# Adicionar VTOLs
simulation.add_vtol(1, "V1", "V5", 0, 1)

# Loop principal
running = True
clock = pygame.time.Clock()

while running:
    # Eventos pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                simulation.paused = not simulation.paused
            elif event.key == pygame.K_ESCAPE:
                running = False
    
    # Atualizar simulação
    if not simulation.paused:
        simulation.simulate_step()
    
    # Renderizar
    screen.fill((40, 40, 60))
    simulation.network.draw(screen)
    
    for vtol in simulation.vtols:
        vtol.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```

### **Execução Principal**

Execute o simulador principal unificado:

```bash
# Simulador principal com menu interativo
python main.py
```

**Opções do Menu:**
1. **🎮 Simulação Completa (Visual)**: Interface pygame completa com todas as funcionalidades
2. **🧪 Teste de Passageiros**: Validação automática do sistema de embarque/desembarque  
3. **📊 Ambos**: Executa teste seguido da simulação visual
4. **❌ Sair**: Encerra o programa

**Funcionalidades da Simulação Visual:**
- VTOLs com rotas planejadas do JSON (circulares e ping-pong)
- VTOLs de simulação tradicional (ponto-a-ponto)
- Sistema de passageiros baseado em demanda temporal
- Embarque/desembarque automatizado de passageiros
- Visualização em tempo real com informações detalhadas
- Controles interativos:
  - **SPACE**: Pausar/Retomar simulação
  - **I**: Alternar exibição de informações
  - **R**: Alternar exibição de rotas
  - **P**: Alternar exibição de passageiros
  - **T**: Executar teste de passageiros em tempo real
  - **S**: Reiniciar rotas planejadas
  - **ESC**: Sair

**Outros Arquivos de Execução:**
```bash
# Simulador principal unificado (RECOMENDADO)
python main.py

# Demo visual alternativo
python visual_demo.py

# Teste de timing da simulação
python test_timing.py
```

---

## 👥 **Sistema de Passageiros**

O simulador inclui um sistema completo de passageiros baseado em demanda temporal:

### **Funcionalidades do Sistema de Passageiros**

1. **Geração Baseada em Demanda**
   - Passageiros são spawneados automaticamente com base no arquivo `demanda_passageiros.csv`
   - A demanda varia por horário do dia (ex: maior demanda em horários de rush)
   - Passageiros são gerados apenas dentro dos vertiportos (nunca fora)

2. **Estados dos Passageiros**
   - **waiting**: Aguardando no vertiporto de origem
   - **boarding**: Embarcando no VTOL
   - **flying**: Voando no VTOL para o destino
   - **arrived**: Chegou ao destino
   - **leaving**: Saindo do vertiporto (animação de subida)

3. **Embarque e Desembarque Automatizado**
   - VTOLs automaticamente embarcam passageiros ao decolar
   - Apenas passageiros com destino correto embarcam
   - Desembarque automático ao chegar no destino
   - Capacidade limitada por VTOL (máximo 4 passageiros)

4. **Animações Visuais**
   - Passageiros são exibidos como círculos coloridos
   - Cores diferentes para cada estado (vermelho=waiting, amarelo=boarding, etc.)
   - Animação de saída: passageiros sobem verticalmente e desaparecem
   - Contador visual de passageiros nos VTOLs

### **Formato do CSV de Demanda**

```csv
vertiport_origem,vertiport_destino,hora_inicio,hora_fim,demanda
V1,V2,04:00,05:00,15
V2,V3,07:00,09:00,25
V3,V1,17:00,19:00,20
```

### **Uso do Sistema de Passageiros**

```python
from src.Modules.Simulation.engine import MatrizOD

# Adicionar sistema de passageiros à simulação
simulation.matriz_od = MatrizOD('src/data/demanda_passageiros.csv')
simulation.matriz_od.current_time_minutes = 4 * 60  # Iniciar às 04:00

# Spawnar passageiros baseado na demanda atual
current_demands = simulation.matriz_od.get_current_demand()
for demand in current_demands:
    # Lógica de spawn implementada no demo_main.py
    spawn_passengers_from_demand(simulation)
```

---

## 🎮 **Funcionalidades Pygame**

### **Componentes Visuais**

1. **Rede de Vertiportos**
   - Vertiportos exibidos como retângulos com indicadores de capacidade
   - Links direcionais com setas mostrando conectividade
   - Distinção visual entre links bidirecionais e unidirecionais
   - Destaque de rotas para visualização de caminhos

2. **Animação de VTOLs**
   - Movimento em tempo real entre vertiportos
   - Representação visual baseada no estado:
     - `landed`: Aeronave azul no vertiport
     - `taking_off`: Animação de escala com efeitos de decolagem
     - `flying`: Aeronave em movimento com animações de rotor
     - `landing`: Sequência de pouso com indicadores
     - `hovering`: Efeitos amarelos de pairar quando aguardando pouso
   - Contador de passageiros exibido acima de cada VTOL

3. **Passageiros**
   - Círculos coloridos representando passageiros nos vertiportos
   - Animação de movimento e estado visual
   - Contador de passageiros por estado no overlay de informações

4. **Gerenciamento de Vertiportos**
   - Indicadores de ocupação em tempo real
   - Visualização de gerenciamento de capacidade
   - Exibição de fila de pairar para vertiportos ocupados

### **Controles Interativos**

- **SPACE**: Pausar/Retomar simulação
- **I**: Alternar exibição de informações
- **ESC**: Sair da simulação

### **Exibição de Informações**

- Tempo atual da simulação
- Contagem de VTOLs por estado
- Taxas de ocupação dos vertiportos
- Filas de pairar

---

## 🔍 **Funcionalidades Implementadas**

### **✅ Sistema de Capacidade Robusto**
- Vertiportos com capacidade limitada configurável
- Fila de espera automática (hovering queue)
- VTOLs pairam quando não há vaga disponível
- Pouso automático quando vaga é liberada
- Indicadores visuais de ocupação

### **✅ Gestão Inteligente de VTOLs**
- Estados bem definidos: `landed`, `taking_off`, `flying`, `landing`, `hovering`
- Rotas baseadas em roteamento NetworkX com pathfinding automático
- Navegação com suporte a redes direcionais/bidirecionais
- Animações visuais de escala e cor baseadas no estado

### **✅ Rede de Vertiportos Flexível**
- Configuração completa via CSV DataFrame
- Suporte para links direcionais e bidirecionais
- Algoritmos de caminho mais curto (NetworkX)
- Estatísticas da rede (densidade, conectividade)

### **✅ Interface Visual Rica**
- Pygame com animações suaves e controles interativos
- Cores dinâmicas baseadas no estado dos VTOLs
- Indicadores visuais de capacidade dos vertiportos
- Linhas de destino e rotas destacadas
- Modo pausar/retomar para análise detalhada

### **✅ Arquitetura Moderna**
- Separação clara entre produção (`src/`) e testes (`tests/`)
- Entrada de dados via pandas DataFrame (CSV)
- NetworkX para algoritmos avançados de grafos
- Código autodocumentado e manutenível
- Gestão de memória com cleanup automático

### **✅ Sistema de Passageiros**
- Geração de passageiros com base em demanda temporal do CSV
- Embarque e desembarque automatizados nos VTOLs
- Animações visuais de passageiros subindo e descendo verticalmente

---

## 🧪 **Testes Disponíveis**

O projeto inclui uma suíte abrangente de testes organizados em `tests/`:

### **Testes Principais**
- `test_simulation.py` - Teste completo do motor de simulação
- `test_csv_integration.py` - Integração com dados CSV
- `test_pygame_components.py` - Componentes da interface pygame
- `test_pygame_headless.py` - Teste headless (sem display)

### **Demos e Testes**  
- `demo_main.py` - Demo principal unificado com todas as funcionalidades
- `visual_demo.py` - Demonstração visual básica
- `test_timing.py` - Teste de desempenho e timing

```bash
# Executar todos os testes
python -m pytest tests/

# Executar teste específico
python tests/test_simulation.py

# Executar demo interativo
python demo_pygame_visualization.py
```

Consulte `tests/README.md` para instruções detalhadas sobre os testes.

---

## 🔧 **Requisitos Técnicos**

### **Dependências Python**
- **Python 3.8+**
- **pygame** - Interface gráfica e visualização
- **pandas** - Manipulação de dados CSV
- **networkx** - Algoritmos de grafos e roteamento

### **Instalação**
```bash
pip install -r requirements.txt
```

### **Arquivos de Dados Obrigatórios**
- `src/data/matriz_od_info.csv` - Informações dos vertiportos
- `src/data/matriz_od_link.csv` - Matriz de conectividade direcional

---

## 📌 **Próximas Extensões**

### **Módulos Futuros**
- **Optimization Module**: Algoritmos de otimização (K-median, genéticos, RL)
- **Demand Generator**: Geração dinâmica de demanda com variações temporais
- **Metrics Engine**: KPIs detalhados (tempo de viagem, eficiência, throughput)
- **3D Visualization**: Simulação com altitude e congestionamento vertical
- **Real-time Analytics**: Dashboard com métricas em tempo real

### **Integrações Planejadas**
- Mapas reais (OpenStreetMap, coordenadas geográficas)
- Simulação de condições climáticas e falhas
- Interface web (Flask/FastAPI) para controle remoto
- Machine Learning para otimização dinâmica de rotas
- APIs para integração com sistemas externos

### **Melhorias de Engenharia**
- Logging estruturado com diferentes níveis
- Configuração via arquivo YAML/TOML
- Containerização com Docker
- Pipeline CI/CD automatizado
- Documentação automática (Sphinx)
- Profiling e otimização de performance

---

## 🏆 **Conquistas da Refatoração**

✅ **Migração completa para CSV DataFrame**: Substituição do JSON por pandas para maior flexibilidade  
✅ **Interface pygame restaurada**: Visualização completa e interativa funcionando  
✅ **Arquitetura NetworkX**: Roteamento avançado com algoritmos de grafos  
✅ **Suporte a links direcionais**: Redes unidirecionais e bidirecionais  
✅ **Organização limpa do código**: Estrutura `src/` e `tests/` bem definida  
✅ **Sistema robusto de capacidade**: Hovering e gestão de filas implementados  
✅ **Testes abrangentes**: Suite completa validando todas as funcionalidades  
✅ **Documentação consolidada**: README unificado com toda informação relevante

O projeto agora está em uma arquitetura moderna e extensível, pronto para futuras expansões mantendo alta qualidade de código e facilidade de manutenção.

---

## 📄 **Licença**

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**UAM Network Simulator** - Simulação avançada de redes de mobilidade aérea urbana com visualização em tempo real e análise de grafos.