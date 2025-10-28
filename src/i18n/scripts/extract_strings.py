#!/usr/bin/env python3
"""
Skrypt do automatycznej ekstrakcji stringów wymagających tłumaczenia
Analizuje pliki Pythona i identyfikuje stringi UI, które powinny być opakowane w tr()
"""

import os
import re
import ast
from typing import List, Dict, Set, Tuple
from pathlib import Path


class StringExtractor:
    """Ekstrator stringów z kodu Pythona"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        
        # Wzorce stringów do ignorowania (techniczne, nie UI)
        self.ignore_patterns = [
            r'^[a-z_]+$',  # Nazwy zmiennych/kluczy (np. "column_type", "task_id")
            r'^\d+$',  # Same liczby
            r'^[A-Z_]+$',  # Stałe (np. "UTF-8", "ISO")
            r'^#[0-9a-fA-F]{6}$',  # Kody kolorów
            r'^\.[a-z]+$',  # Rozszerzenia plików
            r'^(True|False|None)$',  # Wartości Pythona
            r'^(left|right|center|top|bottom)$',  # Wartości wyrównania
            r'^(int|float|str|bool|date|datetime)$',  # Typy
            r'^\s*$',  # Puste stringi
        ]
        
        # Słowa kluczowe Qt - nie tłumaczymy
        self.qt_keywords = {
            'Fusion', 'Windows', 'WindowsVista', 'Macintosh',
            'HLine', 'VLine', 'Sunken', 'Raised', 'Plain',
            'StyledPanel', 'Box', 'Panel',
        }
        
        # Metody Qt wymagające tłumaczenia
        self.ui_methods = {
            'setWindowTitle', 'setTitle', 'setText', 'setPlaceholderText',
            'setToolTip', 'setStatusTip', 'setWhatsThis',
            'addItem', 'addItems', 'insertItem', 'setItemText',
            'setHeaderLabel', 'setHeaderLabels',
            'addAction', 'insertAction',
            'information', 'warning', 'critical', 'question',  # QMessageBox
            'addMenu', 'setLabel', 'setTabText',
        }
        
        # Pliki do analizy
        self.py_files: List[Path] = []
        self.strings_by_file: Dict[str, List[Dict]] = {}
        
    def should_ignore_string(self, s: str) -> bool:
        """Sprawdza czy string powinien być zignorowany"""
        # Usuń białe znaki
        s = s.strip()
        
        # Puste stringi
        if not s:
            return True
        
        # Sprawdź wzorce
        for pattern in self.ignore_patterns:
            if re.match(pattern, s):
                return True
        
        # Qt keywords
        if s in self.qt_keywords:
            return True
        
        # Ścieżki plików
        if '/' in s or '\\' in s or s.endswith(('.py', '.db', '.json', '.ts', '.qm')):
            return True
        
        # SQL queries
        if any(keyword in s.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER']):
            return True
        
        return False
    
    def is_ui_string(self, s: str, context: str = '') -> bool:
        """Sprawdza czy string jest elementem UI wymagającym tłumaczenia"""
        # Ignorowane
        if self.should_ignore_string(s):
            return False
        
        # Jeśli zawiera polskie znaki - prawdopodobnie UI
        if re.search(r'[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', s):
            return True
        
        # Jeśli jest w metodzie UI
        if context:
            for method in self.ui_methods:
                if method in context:
                    return True
        
        # Jeśli zawiera spacje i duże litery (prawdopodobnie etykieta)
        if ' ' in s and any(c.isupper() for c in s):
            return True
        
        # Jeśli kończy się dwukropkiem (etykiety)
        if s.endswith(':'):
            return True
        
        return False
    
    def find_python_files(self) -> List[Path]:
        """Znajduje wszystkie pliki Pythona w projekcie"""
        files = []
        
        # src/ui/*.py - główny priorytet
        ui_dir = self.src_dir / "ui"
        if ui_dir.exists():
            files.extend(ui_dir.glob("*.py"))
        
        # src/utils/*.py
        utils_dir = self.src_dir / "utils"
        if utils_dir.exists():
            files.extend(utils_dir.glob("*.py"))
        
        # main.py
        main_file = self.project_root / "main.py"
        if main_file.exists():
            files.append(main_file)
        
        # Filtruj __init__ i __pycache__
        files = [f for f in files if '__pycache__' not in str(f) and f.name != '__init__.py']
        
        return sorted(files)
    
    def extract_strings_from_file(self, filepath: Path) -> List[Dict]:
        """Ekstrahuje stringi z pojedynczego pliku"""
        strings = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parsuj AST
            tree = ast.parse(content)
            
            # Przejdź przez wszystkie węzły
            for node in ast.walk(tree):
                # String literals
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    s = node.value
                    
                    # Pobierz kontekst (próbuj znaleźć metodę)
                    context = self._get_context(node, tree)
                    
                    if self.is_ui_string(s, context):
                        strings.append({
                            'string': s,
                            'line': node.lineno,
                            'context': context,
                            'type': 'constant'
                        })
                
        except Exception as e:
            print(f"Błąd podczas przetwarzania {filepath}: {e}")
        
        return strings
    
    def _get_context(self, node, tree) -> str:
        """Próbuje określić kontekst stringu (np. nazwę metody)"""
        # To jest uproszczona wersja - w praktyce można rozbudować
        return ''
    
    def analyze_project(self):
        """Analizuje cały projekt"""
        print("🔍 Rozpoczynam analizę projektu...")
        
        # Znajdź pliki
        self.py_files = self.find_python_files()
        print(f"📁 Znaleziono {len(self.py_files)} plików Pythona")
        
        # Analizuj każdy plik
        total_strings = 0
        for filepath in self.py_files:
            rel_path = filepath.relative_to(self.project_root)
            strings = self.extract_strings_from_file(filepath)
            
            if strings:
                self.strings_by_file[str(rel_path)] = strings
                total_strings += len(strings)
                print(f"  ✓ {rel_path}: {len(strings)} stringów")
        
        print(f"\n📊 Znaleziono łącznie {total_strings} stringów do tłumaczenia")
        
    def generate_report(self, output_file: str = None):
        """Generuje raport w formacie Markdown"""
        if output_file is None:
            output_file = self.project_root / "src" / "i18n" / "extraction_report.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Raport ekstrakcji stringów\n\n")
            f.write(f"**Data:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Znalezionych stringów:** {sum(len(strings) for strings in self.strings_by_file.values())}\n")
            f.write(f"**Plików:** {len(self.strings_by_file)}\n\n")
            
            f.write("---\n\n")
            
            # Szczegóły dla każdego pliku
            for filepath, strings in sorted(self.strings_by_file.items()):
                f.write(f"## {filepath}\n\n")
                f.write(f"**Stringów:** {len(strings)}\n\n")
                
                # Top 20 stringów
                f.write("### Przykładowe stringi:\n\n")
                for i, item in enumerate(strings[:20], 1):
                    f.write(f"{i}. Linia {item['line']}: `{item['string'][:60]}...`\n")
                
                if len(strings) > 20:
                    f.write(f"\n*...i {len(strings) - 20} więcej*\n")
                
                f.write("\n---\n\n")
        
        print(f"\n📄 Raport zapisano do: {output_file}")
    
    def generate_todo_list(self, output_file: str = None):
        """Generuje listę TODO z plikami do konwersji"""
        if output_file is None:
            output_file = self.project_root / "src" / "i18n" / "conversion_todo.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Lista plików do konwersji na tr()\n\n")
            
            # Sortuj po liczbie stringów (od najmniejszej)
            sorted_files = sorted(
                self.strings_by_file.items(),
                key=lambda x: len(x[1])
            )
            
            f.write("## Kolejność konwersji (od najprostszych):\n\n")
            for i, (filepath, strings) in enumerate(sorted_files, 1):
                status = "[ ]"  # Checkbox
                f.write(f"{i}. {status} **{filepath}** - {len(strings)} stringów\n")
            
            f.write("\n## Instrukcje konwersji:\n\n")
            f.write("1. Otwórz plik\n")
            f.write("2. Znajdź stringi literalne (użyj raportu jako pomocy)\n")
            f.write("3. Zamień na `self.tr(\"tekst\")`\n")
            f.write("4. Dla stringów z formatowaniem użyj: `self.tr(\"Tekst: %1\").arg(value)`\n")
            f.write("5. Przetestuj czy aplikacja działa\n")
            f.write("6. Zaznacz checkbox ✓\n")
        
        print(f"📋 Lista TODO zapisana do: {output_file}")


def main():
    """Główna funkcja"""
    # Pobierz ścieżkę do projektu (skrypt jest w src/i18n/scripts/)
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent.parent  # 3 poziomy wyżej: scripts -> i18n -> src -> root
    
    print("=" * 60)
    print("EKSTRAKCJA STRINGÓW DO TŁUMACZENIA")
    print("=" * 60)
    print(f"📂 Katalog projektu: {project_root}")
    print()
    
    # Utwórz ekstraktor
    extractor = StringExtractor(str(project_root))
    
    # Analizuj projekt
    extractor.analyze_project()
    
    # Generuj raporty
    print()
    extractor.generate_report()
    extractor.generate_todo_list()
    
    print()
    print("✅ Analiza zakończona!")
    print()
    print("Następne kroki:")
    print("1. Przejrzyj raport: src/i18n/extraction_report.md")
    print("2. Użyj listy TODO: src/i18n/conversion_todo.md")
    print("3. Zacznij konwersję od najprostszych plików")


if __name__ == "__main__":
    main()
