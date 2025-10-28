#!/usr/bin/env python3
"""
Skrypt do kompilacji plików .ts do .qm
Używa lrelease do utworzenia binarnych plików tłumaczeń
"""

import subprocess
import sys
from pathlib import Path


def compile_ts_file(ts_file: Path, qm_file: Path) -> bool:
    """Kompiluje pojedynczy plik .ts do .qm"""
    print(f"\n📦 Kompilowanie: {ts_file.name} → {qm_file.name}")
    
    try:
        # lrelease w PyQt6
        result = subprocess.run(
            ["lrelease", str(ts_file), "-qm", str(qm_file)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"❌ Błąd kompilacji! Kod: {result.returncode}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            return False
        
        # Sprawdź czy plik został utworzony
        if qm_file.exists():
            size = qm_file.stat().st_size
            print(f"✅ Utworzono {qm_file.name} ({size} bajtów)")
            return True
        else:
            print(f"❌ Plik {qm_file.name} nie został utworzony!")
            return False
            
    except FileNotFoundError:
        print("❌ lrelease nie znaleziony! Zainstaluj PyQt6-tools:")
        print("   pip install PyQt6-tools")
        return False
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return False


def main():
    """Główna funkcja"""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent.parent
    translations_dir = project_root / "src" / "i18n" / "translations"
    
    print("=" * 60)
    print("KOMPILACJA TŁUMACZEŃ .TS → .QM")
    print("=" * 60)
    print(f"📂 Katalog tłumaczeń: {translations_dir}")
    print()
    
    # Znajdź wszystkie pliki .ts
    ts_files = list(translations_dir.glob("*.ts"))
    
    if not ts_files:
        print("❌ Nie znaleziono plików .ts do kompilacji!")
        print(f"   Szukano w: {translations_dir}")
        return 1
    
    print(f"📋 Znaleziono {len(ts_files)} plików .ts:")
    for ts_file in sorted(ts_files):
        print(f"  - {ts_file.name}")
    
    # Kompiluj każdy plik
    successful = 0
    failed = 0
    
    for ts_file in sorted(ts_files):
        # Nazwa pliku .qm
        qm_file = ts_file.with_suffix(".qm")
        
        if compile_ts_file(ts_file, qm_file):
            successful += 1
        else:
            failed += 1
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("📊 PODSUMOWANIE")
    print("=" * 60)
    print(f"✅ Sukces: {successful}")
    print(f"❌ Błędy: {failed}")
    
    if successful > 0:
        print(f"\n✅ Pliki .qm są gotowe do użycia!")
        print(f"   Lokalizacja: {translations_dir}")
        
        # Wylistuj pliki .qm
        qm_files = list(translations_dir.glob("*.qm"))
        if qm_files:
            print(f"\n📦 Utworzone pliki .qm:")
            for qm_file in sorted(qm_files):
                size = qm_file.stat().st_size
                print(f"  - {qm_file.name} ({size} bajtów)")
    
    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
