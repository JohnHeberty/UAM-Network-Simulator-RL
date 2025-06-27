# UAM-Network-Simulator-RL - Em Construção

---

## 🧠 **Objetivo do Simulador**

Simular a operação de uma rede de eVTOLs com diferentes configurações de vertiportos e otimizar suas localizações, capacidades e desempenho operacional. O simulador deve permitir:

* Inserção de demanda (origem-destino) dinâmica
* Teste de diferentes estratégias de alocação de vertiportos
* Avaliação visual e estatística da rede

---

## 🏗️ **Arquitetura Geral**

```plaintext
┌────────────────────────────┐
│        Interface (UI)      │◄── Pygame (visualização, eventos)
└────────────┬───────────────┘
             │
┌────────────▼───────────────┐
│      Simulation Engine     │◄── Gera eventos: voo, decolagem, pouso, embarque, desembarque, recarga
└────────────┬───────────────┘
             │
   ┌─────────▼─────────────┐
   │     Optimization      │◄── Algoritmos: k-median, genetic, RL, etc.
   └─────────┬─────────────┘
             │
   ┌─────────▼─────────────┐
   │      Network Model    │◄── Grafo com nós = vertiportos, arestas = rotas
   └─────────┬─────────────┘
             │
   ┌─────────▼─────────────┐
   │     Demand Generator  │◄── OD matrix, stocástico, picos de tráfego
   └─────────┬─────────────┘
             │
   ┌─────────▼─────────────┐
   │      Metrics Engine   │◄── KPIs: tempo de viagem, ocupação, lucro
   └───────────────────────┘
```

---

## 🔍 **Módulos Detalhados**

### 1. **Interface (Pygame UI)**

* Visualização da rede: vertiportos como nós, rotas como linhas
* Animação dos eVTOLs em voo
* Painéis laterais com KPIs (tempo médio, congestionamento, uso por vertiporto)

### 2. **Simulation Engine**

* Lida com ciclos de tempo discretos
* Atualiza posição, fila, recarga, eventos de chegada/partida
* Coordena comunicação entre módulos

### 3. **Optimization Module**

* Recebe grafo atual + demanda → devolve configuração ótima
* Algoritmos possíveis:
  * K-Median (scikit-learn ou heurístico)
  * Algoritmo Genético (DEAP)
  * Reinforcement Learning (Stable-Baselines3)
* Critérios: distância total percorrida, balanceamento de carga, cobertura

### 4. **Network Model**

* Grafo dirigido com:

  * Nós = vertiportos, cada um com capacidade de pouso e recarga
  * Arestas = rotas aéreas possíveis com tempo e custo
* Pode carregar mapas baseados em grid, coordenadas reais ou mockup

### 5. **Demand Generator**

* Matriz OD gerada com:

  * Distribuição uniforme ou centrada em hotspots
  * Cenários de pico (rush hour)
  * Possibilidade de carregamento via CSV/GeoJSON

### 6. **Metrics Engine**

* Calcula em tempo real:

  * Tempo médio de viagem
  * Utilização dos vertiportos
  * Número de voos pendentes/cancelados
  * Lucro estimado (com receita e custo por voo)

---

## 📌 Extensões Futuras

* Integração com mapas reais (OpenStreetMap)
* Simulação de falhas, clima, interrupções
* Voo em 3D com congestionamento por altitude
* Interface web (usando `pygame-web` ou integração com Flask/FastAPI)

---