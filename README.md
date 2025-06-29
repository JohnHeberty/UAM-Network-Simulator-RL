# 🚁 UAM Network Simulator

**Simulador de Rede de Mobilidade Aérea Urbana (Urban Air Mobility)**

---

## 🎯 **Objetivo do Projeto**

O UAM Network Simulator é um sistema avançado de simulação para **Mobilidade Aérea Urbana (UAM)** que permite modelar, visualizar e otimizar redes de transporte de eVTOLs (veículos elétricos de decolagem e pouso vertical) em ambientes urbanos.

### **Finalidades Principais:**

🔹 **Planejamento de Infraestrutura**: Otimizar localização e capacidade de vertiportos  
🔹 **Análise de Demanda**: Simular padrões de tráfego baseados em dados temporais reais  
🔹 **Otimização de Rotas**: Encontrar rotas eficientes usando algoritmos de grafos  
🔹 **Gerenciamento de Capacidade**: Modelar filas, hovering e limitações operacionais  
🔹 **Visualização em Tempo Real**: Interface gráfica para monitoramento e análise  
🔹 **Validação de Conceitos**: Testar cenários UAM antes da implementação real  

### **Casos de Uso:**

- **Planejadores Urbanos**: Avaliar impacto de redes UAM na mobilidade urbana
- **Empresas de eVTOL**: Testar operações e otimizar frotas
- **Pesquisadores**: Estudar algoritmos de otimização e padrões de tráfego
- **Autoridades Regulatórias**: Avaliar segurança e eficiência de propostas UAM

---

## 🛣️ **Roadmap do Projeto**

### ✅ **Implementado (v3.0)**

#### **🏗️ Arquitetura e Infraestrutura**
- [x] Arquitetura SOLID com separação clara de responsabilidades
- [x] Sistema modular com `src/` (produção) e `tests/` (validação)
- [x] Configuração via arquivos CSV para flexibilidade
- [x] Integração NetworkX para algoritmos avançados de grafos

#### **🌐 Rede e Conectividade**
- [x] Rede de vertiportos configurável via CSV
- [x] Suporte completo para links direcionais e bidirecionais  
- [x] Algoritmos de pathfinding automático (caminho mais curto)
- [x] Matriz de adjacência dinâmica para topologias complexas
- [x] Validação de conectividade e análise de grafos

#### **🚁 Sistema de eVTOLs**
- [x] Estados bem definidos: `landed`, `taking_off`, `flying`, `landing`, `hovering`
- [x] Rotas planejadas via JSON (circulares e ping-pong)
- [x] Sistema de capacidade com filas de hovering inteligentes
- [x] Anti-stuck mechanisms para evitar deadlocks
- [x] Animações visuais baseadas em estados
- [x] Embarque/desembarque automatizado de passageiros

#### **👥 Sistema de Passageiros**
- [x] Geração baseada em demanda temporal do CSV
- [x] Estados visuais: `waiting`, `boarding`, `flying`, `arrived`, `leaving`
- [x] Embarque automático baseado em compatibilidade de destinos
- [x] Animações de entrada/saída nos vertiportos
- [x] Capacidade limitada por eVTOL (máx. 4 passageiros)
- [x] Sistema de filas nos vertiportos

#### **🎮 Interface Visual (Pygame)**
- [x] Simulação em tempo real com 60 FPS
- [x] Visualização de vertiportos com indicadores de capacidade
- [x] **Nomes dos vertiportos exibidos acima e à direita** ⭐ *Novo!*
- [x] Animações suaves de movimento e transição
- [x] Controles interativos (pausar, informações, rotas)
- [x] Sistema de cores dinâmico baseado em estados
- [x] Overlays informativos em tempo real

#### **🧪 Sistema de Testes**
- [x] Suite completa de testes unitários e integração
- [x] Testes visuais e headless (sem interface)
- [x] Validação de componentes pygame
- [x] Testes de integração CSV e NetworkX
- [x] Sistema unificado `main.py` para todos os demos

### 🚧 **Em Desenvolvimento (v4.0)**

#### **🔧 Otimização e Performance**
- [ ] Algoritmos de otimização (K-median, genéticos)
- [ ] Reinforcement Learning para rotas dinâmicas
- [ ] Paralelização de simulações
- [ ] Cache inteligente para cálculos repetitivos

#### **📊 Analytics Avançados**
- [ ] Dashboard web em tempo real
- [ ] KPIs detalhados (tempo de viagem, throughput, eficiência)
- [ ] Relatórios automáticos de performance
- [ ] Análise de gargalos e otimização de capacidade

#### **🌍 Funcionalidades Avançadas**
- [ ] Integração com mapas reais (OpenStreetMap)
- [ ] Simulação de condições climáticas
- [ ] Modelagem de falhas de equipamentos
- [ ] Múltiplos tipos de eVTOL com características diferentes

### 💡 **Planejado (v5.0+)**

#### **🤖 IA e Machine Learning**
- [ ] Previsão de demanda com ML
- [ ] Otimização automática de rotas
- [ ] Detecção de padrões anômalos
- [ ] Sistema de recomendações inteligente

#### **🌐 Integração e APIs**
- [ ] API REST para integração externa
- [ ] Conectores para sistemas de gestão de tráfego aéreo
- [ ] Interface para simuladores de voo
- [ ] Integração com sistemas GIS profissionais

---

## 📁 **Estrutura do Projeto**

```
UAM-Network-Simulator-RL/
├── 📂 src/                           # 🏭 Código de Produção
│   ├── __init__.py
│   ├── 📂 Modules/
│   │   ├── __init__.py
│   │   ├── 📂 Simulation/
│   │   │   ├── __init__.py
│   │   │   └── engine.py             # 🚀 Motor Principal da Simulação
│   │   └── 📂 Optimization/          # 🔧 Módulos de Otimização (futuro)
│   └── 📂 data/                      # 📊 Dados de Configuração
│       ├── matriz_od_info.csv        # 🏢 Informações dos Vertiportos
│       ├── matriz_od_link.csv        # 🔗 Matriz de Conectividade
│       ├── demanda_passageiros.csv   # 👥 Demanda Temporal de Passageiros
│       └── vtol_routes.json          # 🚁 Rotas Pré-definidas dos eVTOLs
│
├── 📂 tests/                         # 🧪 Sistema de Testes
│   ├── __init__.py
│   ├── README.md                     # 📖 Documentação dos Testes
│   ├── test_simulation.py            # 🔬 Teste Principal do Motor
│   ├── test_csv_integration.py       # 📊 Teste de Integração CSV
│   ├── test_pygame_components.py     # 🎮 Teste de Componentes Visuais
│   ├── test_pygame_headless.py       # 🖥️ Teste Headless (sem display)
│   └── test_visual.py                # 👁️ Teste Visual Interativo
│
├── 📄 main.py                        # 🎯 Ponto de Entrada Principal
├── 📄 requirements.txt               # 📦 Dependências Python
├── 📄 README.md                      # 📚 Esta Documentação
├── 📄 LICENSE                        # ⚖️ Licença MIT
└── 📄 .gitignore                     # 🚫 Arquivos Ignorados pelo Git
```

### **🔍 Descrição dos Componentes Principais**

| Arquivo/Pasta | Descrição | Responsabilidade |
|---------------|-----------|------------------|
| `src/Modules/Simulation/engine.py` | Motor principal da simulação | Classes VTOL, Vertiport, Network, Simulation, Person |
| `src/data/` | Dados de configuração | CSVs de vertiportos, links, demanda e JSON de rotas |
| `main.py` | Interface unificada | Menu principal com todas as funcionalidades |
| `tests/` | Suite de testes | Validação de componentes e integração |

---

## 🚀 **Instalação e Configuração**

### **1. Pré-requisitos**

- **Python 3.8+** (recomendado 3.10+)
- **Git** (para clonar o repositório)
- **Sistema Operacional**: Windows, macOS ou Linux

### **2. Clonar o Repositório**

```bash
git clone https://github.com/seu-usuario/UAM-Network-Simulator-RL.git
cd UAM-Network-Simulator-RL
```

### **3. Instalar Dependências**

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### **4. Verificar Instalação**

```bash
# Teste rápido
python main.py
```

### **📦 Dependências Principais**

| Biblioteca | Versão | Finalidade |
|------------|--------|------------|
| `pygame` | `>=2.0` | Interface gráfica e visualização |
| `pandas` | `>=1.3` | Manipulação de dados CSV |
| `networkx` | `>=2.6` | Algoritmos de grafos e roteamento |

---

## 📊 **Arquivos de Configuração**

### **1. `matriz_od_info.csv` - Informações dos Vertiportos**

Define as características físicas e operacionais dos vertiportos:

```csv
name;capacity;x;y;
V1;2;200;150;
V2;2;500;200;
V3;2;300;400;
V4;2;700;350;
V5;2;600;550;
```

**Campos:**
- `name`: Identificador único do vertiporto
- `capacity`: Número máximo de eVTOLs simultâneos
- `x`, `y`: Coordenadas na tela (pixels)

### **2. `matriz_od_link.csv` - Conectividade da Rede**

Define as conexões direcionais entre vertiportos:

```csv
X;V1;V2;V3;V4;V5
V1;;x;x;;
V2;x;;x;x;
V3;;;x;;x
V4;;;x;;x
V5;;;x;;;
```

**Interpretação:**
- **Linhas = Origem**, **Colunas = Destino**
- `x` = Conexão permitida nesta direção
- Vazio = Sem conexão

**Exemplo:**
- V1 → V2: ✅ (bidirecional com V2 → V1)
- V1 → V3: ✅ (unidirecional, V3 ↛ V1)

### **3. `demanda_passageiros.csv` - Demanda Temporal**

Define padrões de demanda de passageiros ao longo do dia:

```csv
intervalo,hora_inicio,hora_fim,vertiport_origem,vertiport_destino,demanda
1,04:00,04:30,V3,V1,1
2,04:30,05:00,V2,V5,1
3,05:00,05:30,V1,V2,1
```

**Campos:**
- `intervalo`: ID do intervalo temporal
- `hora_inicio/fim`: Horário de início/fim da demanda
- `vertiport_origem/destino`: Rota da demanda
- `demanda`: Número de passageiros neste intervalo

### **4. `vtol_routes.json` - Rotas dos eVTOLs**

Define rotas pré-planejadas para eVTOLs:

```json
[
  {
    "vtol_id": "ALPHA-1",
    "route": ["V1", "V2", "V4", "V5", "V1"]
  },
  {
    "vtol_id": "BETA-2", 
    "route": ["V3", "V1", "V2"]
  }
]
```

**Tipos de Rota:**
- **Circular**: Primeiro = último elemento (ex: V1→V2→V4→V5→V1)
- **Ping-Pong**: Vai e volta (ex: V3→V1→V2→V1→V3→...)

---

## 🏗️ **Arquitetura do Sistema**

### **📐 Diagrama de Arquitetura**

```
┌─────────────────────────────────────────────────────────────┐
│                   🎮 INTERFACE PYGAME                       │
│               (Visualização e Controles)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 🎯 SIMULATION                               │
│              (Coordenação Central)                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ 🌐 Network │ 👥 MatrizOD │  🚁 VTOLs  │  🏢 Vtpors  │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                📊 DADOS E CONFIGURAÇÃO                      │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │    CSV      │    CSV      │    CSV      │    JSON     │  │
│  │ Vertiportos │   Links     │  Demanda    │   Rotas     │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### **🔧 Princípios SOLID Implementados**

#### **Single Responsibility (SRP)**
```python
class VTOL:        # Responsabilidade: Estado e movimento de um eVTOL
class Vertiport:   # Responsabilidade: Operações de vertiporto
class Network:     # Responsabilidade: Topologia e roteamento
class Simulation:  # Responsabilidade: Coordenação da simulação
```

#### **Open/Closed (OCP)**
```python
# Interfaces extensíveis
class Drawable(ABC):     # Componentes visuais
class Movable(ABC):      # Entidades móveis  
class PathPlanner(ABC):  # Algoritmos de roteamento

### **🔄 Fluxo de Dados**

```
📊 CSV/JSON Files
        ↓
📈 Pandas DataFrames  
        ↓
🌐 NetworkX Graph
        ↓
🎯 Simulation Engine
        ↓
🎮 Pygame Visualization
```

### **🧩 Componentes Principais**

#### **1. Network (Rede)**
- **Responsabilidade**: Gerencia topologia e conectividade
- **Tecnologia**: NetworkX para algoritmos de grafos
- **Funcionalidades**: Pathfinding, análise de conectividade, validação

#### **2. VTOL (eVTOL)**
- **Responsabilidade**: Comportamento individual dos veículos
- **Estados**: `landed`, `taking_off`, `flying`, `landing`, `hovering`
- **Funcionalidades**: Movimento, embarque/desembarque, anti-stuck

#### **3. Vertiport (Vertiporto)**
- **Responsabilidade**: Operações de infraestrutura
- **Funcionalidades**: Controle de capacidade, filas, pouso/decolagem

#### **4. Person (Passageiro)**
- **Responsabilidade**: Comportamento de passageiros
- **Estados**: `waiting`, `boarding`, `flying`, `arrived`, `leaving`
- **Funcionalidades**: Animações, embarque automático

#### **5. MatrizOD (Demanda)**
- **Responsabilidade**: Gerenciamento de demanda temporal
- **Funcionalidades**: Parsing de CSV, cálculo de demanda atual

---

## 🎮 **Como Usar o Simulador**

### **🚀 Execução Principal**

```bash
python main.py
```

**Menu de Opções:**
1. **🎮 Simulação Completa (Visual)** - Interface gráfica completa
2. **🧪 Teste de Passageiros** - Validação do sistema de passageiros  
3. **📊 Ambos** - Teste + Simulação
4. **❌ Sair**

### **🎮 Controles da Simulação**

| Tecla | Ação | Descrição |
|-------|------|-----------|
| `SPACE` | Pausar/Retomar | Pausa a simulação para análise |
| `I` | Informações | Alterna overlay de informações |
| `R` | Rotas | Exibe/oculta rotas dos eVTOLs |
| `P` | Passageiros | Alterna visualização de passageiros |
| `T` | Teste | Executa teste de passageiros |
| `S` | Reiniciar | Reinicia rotas JSON |
| `ESC` | Sair | Encerra a simulação |

### **📊 Informações em Tempo Real**

Durante a simulação, o sistema exibe:

- ⏰ **Tempo atual** da simulação
- 📈 **Contagem de eVTOLs** por estado (voando, pousados, etc.)
- 🏢 **Ocupação dos vertiportos** com indicadores visuais
- 👥 **Demanda atual** de passageiros
- 🚁 **Filas de hovering** quando vertiportos estão cheios

---

## 🔍 **Como a Simulação Funciona**

### **🎯 Fluxo Principal da Simulação**

#### **1. Inicialização**
```python
# 1. Carregamento de dados
vertiports_df = pd.read_csv('matriz_od_info.csv', sep=';')
links_df = pd.read_csv('matriz_od_link.csv', sep=';')
demand_data = MatrizOD('demanda_passageiros.csv')

# 2. Criação da rede
network = Network(vertiports_df, links_df)

# 3. Spawn de eVTOLs
vtols = create_vtols_from_json('vtol_routes.json')
```

#### **2. Loop Principal (60 FPS)**
```python
while running:
    # 1. Atualizar estados dos eVTOLs
    for vtol in vtols:
        vtol.update()  # Estado, movimento, embarque/desembarque
    
    # 2. Spawnar passageiros baseado em demanda
    spawn_passengers_from_demand(simulation)
    
    # 3. Renderizar tudo
    draw_network(screen)
    draw_vtols(screen)
    draw_passengers(screen)
    
    # 4. Processar eventos
    handle_input_events()
```

### **🚁 Sistema de eVTOLs**

#### **Estados e Transições**
```
    LANDED ──────► TAKING_OFF ──────► FLYING
       ▲                                │
       │                                ▼
   HOVERING ◄──────── LANDING ◄──── IN_TRANSIT
```

#### **Lógica de Movimento**
1. **Pathfinding**: NetworkX calcula rota mais curta
2. **Movimento**: Interpolação linear entre pontos
3. **Capacidade**: Verifica disponibilidade no destino
4. **Hovering**: Aguarda em fila se vertiporto cheio

#### **Anti-Stuck Mechanisms**
```python
# Forçar decolagem se ficou muito tempo pousado
if landed_timer > max_landed_time:
    force_takeoff()

# Abortar hovering se ficou muito tempo esperando  
if hover_count > max_hover_count:
    find_alternative_destination()
```

### **👥 Sistema de Passageiros**

#### **Geração Baseada em Demanda**
```python
def spawn_passengers_from_demand():
    current_demands = demand_system.get_current_demand()
    for demand in current_demands:
        origem = demand['origem']
        destino = demand['destino'] 
        quantidade = demand['demanda']
        
        # Spawnar com probabilidade baseada na demanda
        for _ in range(quantidade):
            if random.random() < spawn_probability:
                passenger = Person(origem, destino)
                origem_vertiport.add_passenger(passenger)
```

#### **Embarque Automático**
```python
def _board_passengers(vtol):
    dest_name = vtol.destination_vertiport.name
    available_seats = vtol.max_passengers - len(vtol.onboard_passengers)
    
    # Buscar passageiros com destino compatível
    passengers = vertiport.get_passengers_for_destination(dest_name, available_seats)
    
    for passenger in passengers:
        passenger.board_vtol(vtol)
        vtol.onboard_passengers.append(passenger)
```

### **🏢 Sistema de Vertiportos**

#### **Controle de Capacidade**
```python
def request_landing(vtol):
    if len(occupied_slots) < capacity:
        return True  # Pouso aprovado
    else:
        hovering_queue.append(vtol)  # Adicionar à fila
        return False
```

#### **Liberação de Vagas**
```python
def takeoff_vtol(vtol):
    occupied_slots.remove(vtol)
    
    # Notificar eVTOLs em hovering
    for hovering_vtol in hovering_queue:
        hovering_vtol.can_attempt_landing = True
```

### **🎨 Sistema Visual**

#### **Renderização em Camadas**
1. **Fundo**: Rede de conexões
2. **Vertiportos**: Retângulos com indicadores
3. **📍 Nomes dos vertiportos** (acima e à direita) ⭐
4. **eVTOLs**: Círculos coloridos por estado
5. **Passageiros**: Pontos pequenos nos vertiportos
6. **Interface**: Informações e controles

#### **Sistema de Cores**
```python
COLORS = {
    'landed': (80, 150, 200),      # Azul
    'flying': (100, 200, 255),     # Azul claro
    'hovering': (255, 255, 100),   # Amarelo
    'taking_off': (120, 180, 255), # Azul médio
    'landing': (120, 180, 255)     # Azul médio
}
```

### **🔄 Algoritmos de Roteamento**

#### **NetworkX Pathfinding**
```python
def find_route(origin, destination):
    try:
        # Algoritmo de caminho mais curto
        path = nx.shortest_path(graph, origin, destination)
        return path
    except nx.NetworkXNoPath:
        # Sem rota disponível
        return None
```

#### **Rotas Circulares**
```python
def get_next_destination_circular():
    current_index = route.index(current_vertiport)
    next_index = (current_index + 1) % len(route)
    return route[next_index]
```

#### **Rotas Ping-Pong**
```python
def get_next_destination_pingpong():
    if not reverse_direction:
        next_index = current_index + 1
        if next_index >= len(route):
            reverse_direction = True
            next_index = current_index - 1
    else:
        next_index = current_index - 1
        if next_index < 0:
            reverse_direction = False
            next_index = current_index + 1
    return route[next_index]
```

---

## 🧪 **Sistema de Testes**

### **Tipos de Teste**

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `test_simulation.py` | Integração | Teste completo do motor |
| `test_csv_integration.py` | Unitário | Carregamento de dados |
| `test_pygame_components.py` | Unitário | Componentes visuais |
| `test_pygame_headless.py` | Sistema | Teste sem interface |
| `test_visual.py` | Manual | Teste visual interativo |

### **Execução dos Testes**

```bash
# Teste individual
python tests/test_simulation.py

# Todos os testes
python -m pytest tests/

# Teste visual
python tests/test_visual.py
```

---

## 📈 **Próximos Passos**

### **Contribuições Bem-vindas**

🔹 **Algoritmos de Otimização**: K-median, algoritmos genéticos, RL  
🔹 **Analytics**: Dashboard web, métricas avançadas  
🔹 **Realismo**: Integração com mapas reais, condições climáticas  
🔹 **Performance**: Paralelização, otimizações de rendering  

### **Como Contribuir**

1. Fork do repositório
2. Criar branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Criar Pull Request

---

## 📄 **Licença**

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo `LICENSE` para detalhes.

---

## 👥 **Créditos e Contato**

**Desenvolvido por**: [Seu Nome]  
**Versão**: 3.0  
**Última Atualização**: Junho 2025  

Para dúvidas, sugestões ou colaborações, entre em contato através dos issues do GitHub.

---

**🚁 UAM Network Simulator - Modelando o futuro da mobilidade aérea urbana!**

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

### **✅ Sistema de Passageiros**
- Geração de passageiros com base em demanda temporal do CSV
- Embarque e desembarque automatizados nos VTOLs
- Animações visuais de passageiros subindo e descendo verticalmente

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

## 📌 **Próximas Extensões**

### **Módulos Futuros**
- **Optimization Module**: Algoritmos de otimização (K-median, genéticos, RL)
- **Demand Generator**: Geração dinâmica de demanda com variações temporais
- **Metrics Engine**: KPIs detalhados (tempo de viagem, eficiência, throughput)
- **Real-time Analytics**: Dashboard com métricas em tempo real

### **Integrações Planejadas**
- Mapas reais (OpenStreetMap, coordenadas geográficas)
- Simulação de condições climáticas e falhas
- Interface web (Flask/FastAPI) para controle remoto
- Machine Learning para otimização dinâmica de rotas


## 📄 **Licença**

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---