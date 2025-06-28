#!/usr/bin/env python3
"""
Script para corrigir imports em todos os arquivos de teste após reorganização
"""
import os
import glob
import re

def fix_test_file_imports(test_dir):
    """Corrige imports em todos os arquivos .py na pasta test"""
    
    # Padrões de import a corrigir
    patterns_to_fix = [
        # sys.path.append patterns
        (
            r'sys\.path\.append\(os\.path\.join\(os\.path\.dirname\(__file__\), [\'"]Modules[\'"], [\'"]Simulation[\'"]\)\)',
            'src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), \'src\')\nif src_path not in sys.path:\n    sys.path.append(src_path)'
        ),
        (
            r'src_path = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\nif src_path not in sys\.path:\n    sys\.path\.append\(src_path\)',
            'src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), \'src\')\nif src_path not in sys.path:\n    sys.path.append(src_path)'
        ),
        # Import engine patterns
        (r'from engine import', 'from Modules.Simulation.engine import'),
        # JSON file paths
        (r'vertiports_json="vertiports\.json"', 'vertiports_json=os.path.join(data_path, "vertiports.json")'),
        (r'vtol_routes_json="vtol_routes\.json"', 'vtol_routes_json=os.path.join(data_path, "vtol_routes.json")'),
    ]
    
    # Processa todos os arquivos .py na pasta test
    for file_path in glob.glob(os.path.join(test_dir, "*.py")):
        print(f"Processando {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplica as correções de padrões
        for pattern, replacement in patterns_to_fix:
            content = re.sub(pattern, replacement, content)
        
        # Adiciona definição de data_path se necessário e não existe
        if 'os.path.join(data_path,' in content and 'data_path =' not in content:
            # Adiciona data_path após os imports
            import_section_end = content.find('\n\n')
            if import_section_end > 0:
                before = content[:import_section_end]
                after = content[import_section_end:]
                content = before + '\n\n# Define path to data directory\ndata_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), \'src\', \'data\')' + after
        
        # Salva apenas se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Corrigido")
        else:
            print(f"  ⏭️  Nenhuma correção necessária")

if __name__ == "__main__":
    test_dir = os.path.join(os.path.dirname(__file__), "test")
    fix_test_file_imports(test_dir)
    print("✅ Correção de imports concluída!")
