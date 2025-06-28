# UAM Network Simulator - SOLID Architecture

---

## 🎯 **Status do Projeto: Versão 2.0 - Refatorado com Princípios SOLID**

✅ **Arquitetura SOLID implementada**  
✅ **Configuração apenas via JSON**  
✅ **Controle robusto de capacidade dos vertiportos**  
✅ **Sistema de hovering inteligente**  
✅ **Organização limpa do código**  
✅ **Remoção completa do modo automático**  

---

## 🧠 **Objetivo do Simulador**

Simular a operação de uma rede de eVTOLs (Urban Air Mobility) com diferentes configurações de vertiportos e otimizar suas localizações, capacidades e desempenho operacional. O simulador implementa:

* ✅ **Configuração via JSON apenas**: Vertiportos e rotas de VTOLs definidos em arquivos JSON
* ✅ **Controle de capacidade**: Vertiportos com capacidade limitada e fila de espera
* ✅ **Sistema de hovering**: VTOLs pairam quando não há vaga e pousam automaticamente quando liberada
* ✅ **Princípios SOLID**: Arquitetura limpa, extensível e mantível
* ✅ **Separação de responsabilidades**: Código de produção em `src/`, testes em `test/`

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
│   │       └── engine.py         # Motor principal (SOLID)
│   └── data/                     # Dados de configuração
│       ├── vertiports.json       # Configuração dos vertiportos
│       ├── vtol_routes.json      # Rotas dos VTOLs
│       └── *.csv                 # Dados adicionais
├── test/                         # Testes e demos
│   ├── README.md                 # Documentação dos testes
│   ├── test_*.py                 # Testes funcionais
│   ├── demo_*.py                 # Demonstrações
│   └── generate_od_data.py       # Utilitários
├── fix_imports.py                # Script de correção de imports
└── README.md                     # Este arquivo
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
│  └─────────┘ └──────────────┘   │
├─────────────────────────────────┤
│     Interfaces SOLID            │◄── Contratos bem definidos
│  Drawable | Movable | Cleanable │
└─────────────────────────────────┘
```

---

## 🚀 **Como Usar**

### **Configuração Obrigatória via JSON**

1. **Configure vertiportos** em `src/data/vertiports.json`:
```json
{
  "vertiports": [
    {
      "id": "V1",
      "name": "Aeroporto Central", 
      "x": 200, "y": 150,
      "capacity": 3
    }
  ],
  "connections": [
    {"from": "V1", "to": "V2"}
  ]
}
```

2. **Configure VTOLs** em `src/data/vtol_routes.json`:
```json
{
  "vtol_routes": [
    {
      "id": "ALPHA-1",
      "route": ["V1", "V2", "V3"],
      "loop": true
    }
  ]
}
```

3. **Execute a simulação**:
```python
from src.Modules.Simulation.engine import Simulation

sim = Simulation(
    vertiports_json="src/data/vertiports.json",
    vtol_routes_json="src/data/vtol_routes.json"
)
```

### **Executar Testes**

```bash
# Teste principal: modo JSON obrigatório
python test/test_json_only.py

# Demo interativa de capacidade
python test/demo_capacity.py

# Teste de hovering 
python test/test_hover_final.py
```

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
- Rotas personalizadas via JSON com suporte a loops e ida-e-volta
- Navegação baseada em pathfinding na rede de vertiportos
- Animações visuais de escala e cor baseadas no estado

### **✅ Rede de Vertiportos Flexível**
- Configuração completa via JSON
- Conexões automáticas baseadas em configuração
- Algoritmo de caminho mais curto (BFS)
- Estatísticas da rede (densidade, conectividade)

### **✅ Interface Visual Rica**
- Pygame com animações suaves
- Cores dinâmicas baseadas no estado dos VTOLs
- Indicadores visuais de capacidade dos vertiportos
- Linhas de destino e rotas destacadas

### **✅ Arquitetura Limpa**
- Separação clara entre produção (`src/`) e testes (`test/`)
- Interfaces bem definidas seguindo SOLID
- Código autodocumentado e manutenível
- Gestão de memória com cleanup automático

---

## 🧪 **Testes Disponíveis**

O projeto inclui uma suíte abrangente de testes organizados:

### **Testes Funcionais**
- `test_json_only.py` - Verifica modo JSON obrigatório
- `test_capacity.py` - Controle de capacidade
- `test_hover_*.py` - Comportamento de hovering
- `test_stress_capacity.py` - Teste de stress

### **Demos Interativas**  
- `demo_capacity.py` - Demonstração visual de capacidade
- `final_capacity_demo.py` - Demo completa do sistema

Consulte `test/README.md` para instruções detalhadas.

---

## 🔧 **Requisitos**

- **Python 3.12+**
- **pygame** - Interface gráfica
- **Arquivos JSON** - Configuração obrigatória

```bash
pip install pygame
```

---

## 📌 **Próximas Extensões**

### **Módulos Futuros**
- **Optimization Module**: K-median, algoritmos genéticos, RL
- **Demand Generator**: Geração dinâmica de demanda com picos
- **Metrics Engine**: KPIs detalhados (tempo de viagem, lucro, eficiência)
- **3D Visualization**: Simulação com altitude e congestionamento vertical

### **Integrações Planejadas**
- Mapas reais (OpenStreetMap)
- Simulação de falhas e clima
- Interface web (Flask/FastAPI)
- Machine Learning para otimização de rotas

### **Melhorias de Engenharia**
- Logging estruturado
- Configuração via arquivo YAML/TOML
- Dockerização
- CI/CD Pipeline
- Documentação automática (Sphinx)

---

## 🏆 **Conquistas da Refatoração**

✅ **Remoção completa do modo automático**  
✅ **Implementação rigorosa dos princípios SOLID**  
✅ **Organização limpa do código (src/ e test/)**  
✅ **Sistema robusto de capacidade e hovering**  
✅ **Configuração 100% via JSON**  
✅ **Arquitetura extensível e manutenível**  
✅ **Testes abrangentes e documentação clara**  

O projeto agora está pronto para futuras extensões mantendo alta qualidade de código e facilidade de manutenção.

---