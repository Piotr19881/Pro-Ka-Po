#!/usr/bin/env python3
"""
Pro-Ka-Po V2 - Aplikacja do organizacji zadań
Główny punkt wejścia aplikacji
"""

import sys
import os

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.main_window import main

if __name__ == "__main__":
    main()