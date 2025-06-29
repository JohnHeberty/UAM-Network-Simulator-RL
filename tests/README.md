# Testes do UAM Network Simulator

Este diretório contém todos os testes do simulador de rede UAM, organizados por funcionalidade.

## 📋 **Visão Geral dos Testes**

### **Testes Principais**

#### `test_simulation.py` 
**Teste abrangente do motor de simulação**
- Carregamento de dados CSV
- Criação da rede NetworkX
- Lógica de simulação
- Componentes pygame (modo headless/visual)
- Simulação visual básica

```bash
# Execução padrão (modo visual)
python tests/test_simulation.py

# Modo headless (sem interface)
python tests/test_simulation.py  # Escolher 'n' quando perguntado
```

#### `test_visual.py` 
**Teste visual interativo completo**
- Teste de componentes estáticos
- Simulação dinâmica com interface
- Controles interativos (SPACE, ESC)
- Múltiplos VTOLs em movimento

```bash
# Execução com janelas pygame
python tests/test_visual.py
```

### **Testes Específicos**

#### `test_csv_integration.py`
**Integração com dados CSV**
- Carregamento de DataFrames
- Validação de estrutura de dados
- Parsing de matriz de adjacência
- Criação de rede a partir de CSV

#### `test_pygame_components.py`
**Componentes pygame individuais**
- Teste de classes Vertiport, VTOL, Network
- Renderização de componentes
- Validação de estados visuais

#### `test_pygame_headless.py`
**Teste sem interface gráfica**
- Simulação completa modo headless
- Validação de lógica sem pygame
- Performance testing

## 🚀 **Como Executar**

### **Teste Rápido Visual**
```bash
# Teste visual mais completo
python tests/test_visual.py
```

### **Teste Completo**
```bash
# Teste abrangente com opção visual
python tests/test_simulation.py
```

### **Testes Específicos**
```bash
# Integração CSV
python tests/test_csv_integration.py

# Componentes pygame
python tests/test_pygame_components.py

# Modo headless
python tests/test_pygame_headless.py
```

### **Todos os Testes (pytest)**
```bash
# Executar toda a suite de testes
python -m pytest tests/ -v

# Executar teste específico
python -m pytest tests/test_simulation.py -v
```

## 🎮 **Controles dos Testes Visuais**

### **Durante Testes Visuais:**
- **ESC**: Continuar para próximo teste
- **SPACE**: Pausar/Retomar simulação
- **Fechar janela**: Sair do teste

### **Informações Exibidas:**
- Estado atual dos VTOLs
- Tempo de simulação
- Contadores de frame
- Estatísticas em tempo real

## 📊 **Estrutura dos Testes**

```
tests/
├── test_simulation.py       # Teste principal abrangente
├── test_visual.py          # Teste visual interativo
├── test_csv_integration.py # Teste de integração CSV
├── test_pygame_components.py # Componentes pygame
├── test_pygame_headless.py # Teste headless
├── __init__.py             # Inicialização dos testes
└── README.md               # Esta documentação
```

## ✅ **Validações dos Testes**

Cada teste valida:

1. **Carregamento de Dados**: CSV parsing correto
2. **Criação de Rede**: NetworkX graph construction
3. **Lógica de Simulação**: Estados e transições de VTOLs
4. **Renderização Visual**: Componentes pygame funcionais
5. **Performance**: Execução sem erros e vazamentos de memória

## 🐛 **Debugging**

### **Problemas Comuns:**

**Erro de display pygame:**
```bash
# Se pygame não conseguir criar display
export SDL_VIDEODRIVER=dummy  # Linux/Mac
set SDL_VIDEODRIVER=dummy     # Windows
```

**Erro de import:**
```bash
# Garantir que está no diretório raiz do projeto
cd /path/to/UAM-Network-Simulator-RL
python tests/test_simulation.py
```

**Dados CSV não encontrados:**
```bash
# Verificar se os arquivos CSV existem
ls src/data/matriz_od_*.csv
```

## 📈 **Resultados Esperados**

### **Teste Bem-sucedido:**
```
🎉 ALL TESTS PASSED!
✓ CSV data loading
✓ NetworkX integration
✓ Simulation logic
✓ Pygame visualization
✓ Visual simulation
```

### **Estados de VTOL Típicos:**
- `landed`: VTOLs estacionados em vertiportos
- `taking_off`: Iniciando decolagem
- `flying`: Em movimento entre vertiportos
- `landing`: Processo de pouso
- `hovering`: Aguardando vaga para pouso

---

**Nota**: Para melhor experiência visual, execute `test_visual.py` que oferece interface mais interativa e controles completos.
