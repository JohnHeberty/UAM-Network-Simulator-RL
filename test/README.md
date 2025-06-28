# Testes UAM Network Simulator

Esta pasta contém todos os testes e demos do simulador de rede UAM (Urban Air Mobility).

## Estrutura dos Testes

### Testes de Funcionalidade
- `test_json_only.py` - Verifica que apenas o modo JSON funciona (sem modo automático)
- `test_capacity.py` - Testa controle de capacidade dos vertiportos
- `test_hover_final.py` - Teste final de hovering quando vertiport está cheio
- `test_hover_direct.py` - Teste direto de comportamento de hovering
- `test_hovering_fix.py` - Teste de correção do hovering
- `test_extreme_hover.py` - Teste de cenário extremo de hovering
- `test_json_capacity.py` - Teste de capacidade usando configuração JSON
- `test_stress_capacity.py` - Teste de stress para capacidade do sistema

### Testes de Correção de Bugs
- `test_beta2_bug.py` - Teste para bug específico da versão beta 2
- `test_beta2_bug_fixed.py` - Verificação da correção do bug beta 2
- `test_vtol_bug.py` - Teste de bug específico de VTOL
- `test_matriz_od.py` - Teste da matriz origem-destino

### Demos
- `demo_capacity.py` - Demonstração do controle de capacidade
- `demo_size_config.py` - Demonstração de configuração de tamanho
- `final_capacity_demo.py` - Demo final do sistema de capacidade

### Utilitários
- `generate_od_data.py` - Gerador de dados origem-destino

## Como Executar os Testes

### Pré-requisitos
- Python 3.12+
- pygame
- Módulos do simulador na pasta `src/`

### Executar um teste específico
```bash
# A partir da raiz do projeto
python test/test_json_only.py
python test/test_capacity.py
python test/demo_capacity.py
```

### Executar testes em lote
```bash
# Executar todos os testes de JSON
python test/test_json_only.py
python test/test_json_capacity.py

# Executar todos os testes de capacidade
python test/test_capacity.py
python test/test_stress_capacity.py
python test/demo_capacity.py
```

## Descrição dos Principais Testes

### test_json_only.py
Verifica que o sistema:
- ✅ Funciona apenas com arquivos JSON válidos
- ✅ Falha graciosamente com arquivos JSON inválidos/inexistentes  
- ✅ Não tem mais modo automático/circular

### test_hover_final.py
Teste interativo que simula:
- VTOLs circulando entre vertiportos
- Comportamento de hovering quando vertiport está cheio
- Landing automático quando vaga é liberada
- Interface visual para acompanhar o comportamento

### test_capacity.py
Teste que verifica:
- Controle de capacidade dos vertiportos
- Fila de espera (hovering queue)
- Liberação de vagas e notificação de VTOLs

## Estrutura dos Dados de Teste

Os testes usam os arquivos JSON na pasta `src/data/`:
- `vertiports.json` - Configuração dos vertiportos
- `vtol_routes.json` - Configuração das rotas dos VTOLs

## Resultados Esperados

Todos os testes devem:
1. Executar sem erros
2. Mostrar comportamentos corretos do sistema
3. Demonstrar que o modo automático foi removido
4. Validar o controle de capacidade e hovering

## Troubleshooting

### Erro de Import
Se você receber erros de import, verifique:
1. Se está executando da raiz do projeto
2. Se a pasta `src/` está no local correto
3. Se os arquivos JSON estão em `src/data/`

### Erro de Pygame
Para instalar pygame:
```bash
pip install pygame
```

### Arquivos JSON não encontrados
Verifique se os arquivos estão em:
- `src/data/vertiports.json`
- `src/data/vtol_routes.json`
