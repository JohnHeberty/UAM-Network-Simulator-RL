"""
Demo de Passageiros - UAM Network Simulator

Demonstra o novo sistema de passageiros baseado em demanda do arquivo CSV:
- Passageiros são gerados nos vertiportos com base na demanda temporal
- Passageiros embarcam em VTOLs
- Após chegarem ao destino, fazem animação de saída (sobem verticalmente)
- Sistema de tempo baseado no arquivo demanda_passageiros.csv
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.Modules.Simulation.engine import SimulatorUI

def main():
    """Demo do sistema de passageiros"""
    print("UAM Network Simulator - Demo de Passageiros")
    print("=" * 45)
    print("Funcionalidades demonstradas:")
    print("- Geração de passageiros baseada em demanda temporal")
    print("- Passageiros esperam nos vertiportos")
    print("- Embarque e desembarque de passageiros em VTOLs")
    print("- Animação de saída após chegada ao destino")
    print("- Sistema de tempo baseado no CSV de demanda")
    print()
    print("Controles:")
    print("- ESC: Sair")
    print("- Observe os passageiros aparecendo nos vertiportos")
    print("- W: passageiros esperando, A: passageiros chegando")
    print()
    
    # Caminho para o arquivo de demanda
    demand_file = "src/data/demanda_passageiros.csv"
    
    try:
        # Inicializa simulador com sistema de passageiros
        app = SimulatorUI(fps=True, demand_file=demand_file)
        print("Iniciando simulação com sistema de passageiros...")
        app.run()
    except FileNotFoundError:
        print(f"Erro: Arquivo de demanda {demand_file} não encontrado!")
        print("Verifique se o arquivo existe no diretório correto.")
    except Exception as e:
        print(f"Erro durante a simulação: {e}")

if __name__ == "__main__":
    main()
