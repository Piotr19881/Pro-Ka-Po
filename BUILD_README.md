# Optymalizacja Rozmiaru i Budowanie Instalatora

## 📦 Podsumowanie Optymalizacji

### Zmiany wprowadzone:
1. ✅ Usunięto **PyQt6-WebEngine** (-50 MB)
2. ✅ Usunięto **PyQt6-tools** (potrzebne tylko do developmentu)
3. ✅ Zaktualizowano `requirements.txt` 
4. ✅ Utworzono `pro-ka-po.spec` z wykluczeniami modułów
5. ✅ Utworzono skrypt budowania `build.ps1`

### Szacowany rozmiar przed optymalizacją:
- **Instalator**: ~160-200 MB
- **Po instalacji**: ~220 MB

### Szacowany rozmiar PO optymalizacji:
- **Instalator**: ~60-90 MB  (✅ -60% rozmiaru!)
- **Po instalacji**: ~140-180 MB

---

## 🚀 Jak zbudować exe

### Krok 1: Zainstaluj PyInstaller
```powershell
pip install pyinstaller
```

### Krok 2: (Opcjonalnie) Zainstaluj UPX dla lepszej kompresji
1. Pobierz UPX: https://github.com/upx/upx/releases
2. Rozpakuj do `C:\upx` lub dodaj do PATH

### Krok 3: Uruchom skrypt budowania
```powershell
.\build.ps1
```

LUB manualnie:
```powershell
pyinstaller pro-ka-po.spec
```

### Krok 4: Znajdź exe
Plik będzie w: `dist\Pro-Ka-Po.exe`

---

## 📋 Zawartość pliku pro-ka-po.spec

Plik `pro-ka-po.spec` wykluczamoduły PyQt6:
- ❌ QtWebEngine (~50 MB)
- ❌ Qt3D* (~20 MB)
- ❌ QtCharts (~10 MB)
- ❌ QtQuick* (~15 MB)
- ❌ Inne nieużywane moduły (~20 MB)

**Łączna oszczędność: ~80-115 MB**

---

## 🎯 Następne kroki (dla mniejszego instalatora)

### Opcja A: Użyj Inno Setup (ZALECANE)
1. Pobierz Inno Setup: https://jrsoftware.org/isdl.php
2. Użyj kompresji LZMA2
3. **Końcowy rozmiar instalatora: ~40-60 MB**

### Opcja B: Użyj NSIS
1. Pobierz NSIS: https://nsis.sourceforge.io/
2. Skonfiguruj kompresję LZMA
3. **Końcowy rozmiar instalatora: ~45-65 MB**

---

## 🔧 Dodatkowe optymalizacje (zaawansowane)

### 1. Wyłącz debugging w spec file:
```python
debug=False,
strip=True,  # Usuwa symbole debug (-5-10 MB)
```

### 2. Użyj kompresji UPX:
```python
upx=True,
upx_exclude=[],  # ~30% redukcja rozmiaru
```

### 3. Wykluczlokalizacje języków Qt (jeśli nie potrzebujesz):
```python
# W sekcji excludes:
'PyQt6.QtCore.Qt.Locales',
```

---

## 📊 Porównanie z konkurencją

| Aplikacja | Rozmiar Instalatora | Po instalacji |
|-----------|---------------------|---------------|
| Notion    | ~150 MB            | ~400 MB       |
| Todoist   | ~120 MB            | ~350 MB       |
| Microsoft To Do | ~80 MB      | ~250 MB       |
| **Pro-Ka-Po** | **~60-90 MB** | **~150-180 MB** |

✅ **Pro-Ka-Po jest mniejszy niż większość konkurencji!**

---

## 🆘 Rozwiązywanie problemów

### Problem: "Module not found" po zbudowaniu
**Rozwiązanie**: Dodaj brakujący moduł do `hiddenimports` w `pro-ka-po.spec`

### Problem: Exe jest za duży (>150 MB)
**Rozwiązanie**: 
1. Sprawdź czy UPX działa: `upx --version`
2. Upewnij się że excludes są aktywne
3. Użyj: `pyinstaller --log-level=DEBUG pro-ka-po.spec` i sprawdź logi

### Problem: Aplikacja nie działa po zbudowaniu
**Rozwiązanie**:
1. Uruchom: `dist\Pro-Ka-Po.exe` z konsoli aby zobaczyć błędy
2. Sprawdź czy wszystkie pliki data/ są dołączone
3. Sprawdź `datas` w spec file

---

## 📝 Uwagi

- Baza danych SQLite nie jest dołączana do exe - tworzona przy pierwszym uruchomieniu
- Ikona aplikacji: dodaj plik `icon.ico` w głównym katalogu
- Dla development używaj wersji bez kompilacji: `python main.py`

---

## 🔄 Aktualizacja zależności

Aby zaktualizować wszystkie zależności:
```powershell
pip install --upgrade -r requirements.txt
```

Aby sprawdzić aktualne wersje:
```powershell
pip list --outdated
```
