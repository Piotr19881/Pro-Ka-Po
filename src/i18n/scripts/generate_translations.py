#!/usr/bin/env python3
"""
Skrypt do automatycznego generowania plików tłumaczeń .ts
Używa pylupdate6 do ekstrakcji wszystkich tr() stringów z kodu
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Uruchamia polecenie i wyświetla wynik"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Komenda: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print(f"❌ Błąd! Kod wyjścia: {result.returncode}")
            return False
        else:
            print("✅ Sukces!")
            return True
            
    except Exception as e:
        print(f"❌ Wyjątek: {e}")
        return False


def main():
    """Główna funkcja"""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent.parent
    
    print("=" * 60)
    print("GENEROWANIE PLIKÓW TŁUMACZEŃ .TS")
    print("=" * 60)
    print(f"📂 Katalog projektu: {project_root}")
    print()
    
    # Pliki źródłowe do przetworzenia
    source_files = [
        "src/ui/main_window.py",
        "src/ui/quick_task_dialog.py",
        "src/ui/pomodoro_view.py",
        "src/ui/alarms_view.py",
        "src/ui/alarm_popup.py",
        "src/ui/kanban_view.py",
        "src/ui/notes_view.py",
        "src/ui/tasks_view.py",
        "src/ui/column_dialog.py",
        "src/ui/column_delegate.py",
        "src/ui/table_dialogs.py",
        "src/ui/list_dialogs.py",
        "src/ui/tag_dialog.py",
        "src/ui/math_column_dialog.py",
        "src/ui/task_list_content_dialog.py",
        "src/ui/theme_manager.py",
        "src/utils/backup_manager.py",
        "main.py",
    ]
    
    # Języki docelowe
    languages = [
        ("en", "English"),
        ("de", "German"),
    ]
    
    # Zmień katalog roboczy
    import os
    os.chdir(project_root)
    
    # Generuj dla każdego języka
    for lang_code, lang_name in languages:
        ts_file = f"src/i18n/translations/pro_ka_po_{lang_code}.ts"
        
        print(f"\n{'🌍 ' + lang_name + ' (' + lang_code + ')':=^60}")
        
        # Buduj komendę pylupdate6
        cmd = ["pylupdate6", "--verbose", "--ts", ts_file] + source_files
        
        success = run_command(
            cmd,
            f"Generowanie {ts_file}"
        )
        
        if not success:
            print(f"\n❌ Nie udało się wygenerować {ts_file}")
            continue
        
        # Sprawdź czy plik istnieje
        if Path(ts_file).exists():
            size = Path(ts_file).stat().st_size
            print(f"\n✅ Plik {ts_file} utworzony ({size} bajtów)")
        else:
            print(f"\n❌ Plik {ts_file} nie został utworzony!")
    
    print("\n" + "=" * 60)
    print("📊 PODSUMOWANIE")
    print("=" * 60)
    
    # Sprawdź wszystkie pliki .ts
    translations_dir = project_root / "src" / "i18n" / "translations"
    ts_files = list(translations_dir.glob("*.ts"))
    
    if ts_files:
        print(f"\n✅ Utworzono {len(ts_files)} plików .ts:")
        for ts_file in sorted(ts_files):
            size = ts_file.stat().st_size
            print(f"  - {ts_file.name} ({size:,} bajtów)")
    else:
        print("\n❌ Nie znaleziono plików .ts")
    
    print("\n📝 Następne kroki:")
    print("1. Otwórz pliki .ts w Qt Linguist")
    print("2. Przetłumacz stringi")
    print("3. Zapisz pliki")
    print("4. Skompiluj do .qm używając: python src/i18n/scripts/compile_translations.py")
    print()


if __name__ == "__main__":
    main()
