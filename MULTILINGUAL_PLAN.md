# 🌍 Plan Implementacji Wielojęzyczności (i18n) - Pro-Ka-Po

## 📋 Spis Treści
1. [Analiza Obecnego Stanu](#analiza-obecnego-stanu)
2. [Wybór Technologii](#wybór-technologii)
3. [Struktura Plików](#struktura-plików)
4. [Plan Implementacji](#plan-implementacji)
5. [Języki do Dodania](#języki-do-dodania)
6. [Harmonogram](#harmonogram)

---

## 1. Analiza Obecnego Stanu

### Problemy do rozwiązania:
- ✗ Wszystkie teksty hardcoded w kodzie (PL)
- ✗ Brak systemu tłumaczeń
- ✗ Brak możliwości zmiany języka w runtime
- ✗ Nazwy kolumn w bazie danych po polsku
- ✗ Komunikaty systemowe po polsku

### Co należy przetłumaczyć:
1. **Interfejs użytkownika** (~500-800 stringów)
   - Menu i przyciski
   - Etykiety pól
   - Komunikaty dialogowe
   - Tooltips
   - Statusy

2. **Komunikaty systemowe** (~100-200 stringów)
   - Błędy
   - Ostrzeżenia
   - Potwierdzenia
   - Powiadomienia

3. **Nazwy domyślne** (~50 stringów)
   - Nazwy kolumn
   - Nazwy widoków
   - Nazwy kategorii
   - Domyślne wartości

4. **Dokumentacja** (~20-30 plików)
   - README.md
   - Pomoc kontekstowa
   - Tooltips rozszerzone

---

## 2. Wybór Technologii

### Opcja A: PyQt6 Qt Linguist (ZALECANE) ⭐
```
Zalety:
✓ Natywna integracja z PyQt6
✓ Qt Linguist - profesjonalne narzędzie do tłumaczeń
✓ Runtime switching - zmiana języka bez restartu
✓ Wsparcie dla kontekstu i liczby mnogiej
✓ Pliki .ts (XML) - łatwe do edycji
✓ Kompilacja do .qm (binarne, szybkie)

Wady:
✗ Wymaga Qt Linguist (dodatkowo ~50 MB)
✗ Bardziej skomplikowana konfiguracja
```

### Opcja B: Python gettext
```
Zalety:
✓ Standardowa biblioteka Python
✓ Lekka (~1 MB)
✓ Proste w użyciu
✓ Pliki .po (text) - łatwe do edycji

Wady:
✗ Wymaga restartu aplikacji po zmianie języka
✗ Brak wsparcia dla kontekstu Qt
✗ Mniej funkcji niż Qt Linguist
```

### Opcja C: JSON/YAML (Custom)
```
Zalety:
✓ Bardzo proste
✓ Łatwe do edycji (JSON/YAML)
✓ Pełna kontrola

Wady:
✗ Brak wsparcia dla plurals
✗ Brak narzędzi do tłumaczenia
✗ Trzeba wszystko zaimplementować samemu
```

### 🎯 REKOMENDACJA: Opcja A (PyQt6 Qt Linguist)

---

## 3. Struktura Plików

### Proponowana struktura katalogów:
```
Pro-Ka-Po V2/
├── src/
│   ├── i18n/                      # Nowy folder dla tłumaczeń
│   │   ├── __init__.py
│   │   ├── translator.py          # Manager tłumaczeń
│   │   └── languages/
│   │       ├── pl_PL.ts          # Polski (źródłowy)
│   │       ├── pl_PL.qm          # Polski (skompilowany)
│   │       ├── en_US.ts          # Angielski
│   │       ├── en_US.qm
│   │       ├── de_DE.ts          # Niemiecki
│   │       ├── de_DE.qm
│   │       ├── es_ES.ts          # Hiszpański
│   │       ├── es_ES.qm
│   │       ├── fr_FR.ts          # Francuski
│   │       ├── fr_FR.qm
│   │       └── it_IT.ts          # Włoski
│   │           └── it_IT.qm
│   └── ...
└── tools/
    ├── generate_translations.py   # Skrypt do generowania .ts
    ├── compile_translations.py    # Kompilacja .ts → .qm
    └── update_translations.py     # Aktualizacja istniejących .ts
```

### Baza danych:
```sql
-- Nowa tabela dla tłumaczeń dynamicznych
CREATE TABLE translations (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL,           -- Klucz tłumaczenia
    language TEXT NOT NULL,      -- Kod języka (pl_PL, en_US)
    value TEXT NOT NULL,         -- Przetłumaczony tekst
    context TEXT,                -- Kontekst (opcjonalny)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(key, language)
);

-- Nowa kolumna w app_settings
ALTER TABLE app_settings ADD COLUMN language TEXT DEFAULT 'pl_PL';
```

---

## 4. Plan Implementacji

### FAZA 1: Przygotowanie (1-2 dni)

#### Krok 1.1: Instalacja narzędzi
```bash
pip install PyQt6-tools  # Zawiera pylupdate6 i lrelease
```

#### Krok 1.2: Utworzenie struktury
```python
# src/i18n/__init__.py
from .translator import TranslationManager

__all__ = ['TranslationManager']
```

```python
# src/i18n/translator.py
from PyQt6.QtCore import QTranslator, QLocale, QCoreApplication
from PyQt6.QtWidgets import QApplication
import os

class TranslationManager:
    def __init__(self, app: QApplication):
        self.app = app
        self.translator = QTranslator()
        self.current_language = 'pl_PL'
        
    def load_language(self, language_code: str):
        """Ładuje język"""
        qm_file = f"src/i18n/languages/{language_code}.qm"
        
        if os.path.exists(qm_file):
            self.app.removeTranslator(self.translator)
            self.translator = QTranslator()
            
            if self.translator.load(qm_file):
                self.app.installTranslator(self.translator)
                self.current_language = language_code
                return True
        return False
    
    def get_available_languages(self):
        """Zwraca listę dostępnych języków"""
        languages_dir = "src/i18n/languages"
        languages = []
        
        if os.path.exists(languages_dir):
            for file in os.listdir(languages_dir):
                if file.endswith('.qm'):
                    lang_code = file.replace('.qm', '')
                    languages.append(lang_code)
        
        return languages
```

#### Krok 1.3: Modyfikacja main.py
```python
# main.py
import sys
from PyQt6.QtWidgets import QApplication
from src.i18n import TranslationManager
from src.ui.main_window import TaskManagerApp

def main():
    app = QApplication(sys.argv)
    
    # Inicjalizacja tłumaczeń
    translator = TranslationManager(app)
    
    # Wczytaj zapisany język lub domyślny
    saved_language = load_language_setting()  # Z bazy
    translator.load_language(saved_language)
    
    # Utwórz okno główne
    window = TaskManagerApp(translator)
    window.show()
    
    sys.exit(app.exec())
```

---

### FAZA 2: Ekstrakcja Tekstów (2-3 dni)

#### Krok 2.1: Zmiana hardcoded tekstów na QCoreApplication.translate()

**PRZED:**
```python
button = QPushButton("Zapisz")
label = QLabel("Nazwa:")
```

**PO:**
```python
button = QPushButton(self.tr("Zapisz"))
label = QLabel(self.tr("Nazwa:"))
```

#### Krok 2.2: Automatyczna ekstrakcja
```bash
# Generuje plik .ts ze wszystkimi tekstami do przetłumaczenia
pylupdate6 -verbose src/**/*.py -ts src/i18n/languages/pl_PL.ts
```

#### Krok 2.3: Utworzenie skryptu pomocniczego
```python
# tools/generate_translations.py
import subprocess
import os

LANGUAGES = ['pl_PL', 'en_US', 'de_DE', 'es_ES', 'fr_FR', 'it_IT']
TS_DIR = 'src/i18n/languages'

def generate_ts_files():
    """Generuje pliki .ts dla wszystkich języków"""
    os.makedirs(TS_DIR, exist_ok=True)
    
    for lang in LANGUAGES:
        ts_file = f'{TS_DIR}/{lang}.ts'
        
        # Generuj/aktualizuj .ts
        subprocess.run([
            'pylupdate6',
            '-verbose',
            'src/**/*.py',
            '-ts', ts_file
        ])
        
        print(f'✓ Wygenerowano: {ts_file}')

if __name__ == '__main__':
    generate_ts_files()
```

---

### FAZA 3: Tłumaczenie (3-5 dni na język)

#### Krok 3.1: Użycie Qt Linguist
```
1. Otwórz Qt Linguist
2. File → Open → wybierz src/i18n/languages/en_US.ts
3. Tłumacz string po stringu
4. File → Save
```

#### Krok 3.2: Alternatywnie - edycja XML (.ts)
```xml
<!-- src/i18n/languages/en_US.ts -->
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en_US">
<context>
    <name>MainWindow</name>
    <message>
        <source>Zapisz</source>
        <translation>Save</translation>
    </message>
    <message>
        <source>Anuluj</source>
        <translation>Cancel</translation>
    </message>
</context>
</TS>
```

#### Krok 3.3: Kompilacja .ts → .qm
```python
# tools/compile_translations.py
import subprocess
import os

TS_DIR = 'src/i18n/languages'

def compile_ts_files():
    """Kompiluje pliki .ts do .qm"""
    for file in os.listdir(TS_DIR):
        if file.endswith('.ts'):
            ts_file = os.path.join(TS_DIR, file)
            qm_file = ts_file.replace('.ts', '.qm')
            
            subprocess.run(['lrelease', ts_file, '-qm', qm_file])
            print(f'✓ Skompilowano: {qm_file}')

if __name__ == '__main__':
    compile_ts_files()
```

---

### FAZA 4: Integracja z UI (1-2 dni)

#### Krok 4.1: Dodanie wyboru języka w Ustawieniach
```python
# W create_general_settings_tab()
language_group = QGroupBox(self.tr("Język / Language"))
language_layout = QVBoxLayout()

self.language_combo = QComboBox()
languages = {
    'pl_PL': '🇵🇱 Polski',
    'en_US': '🇬🇧 English',
    'de_DE': '🇩🇪 Deutsch',
    'es_ES': '🇪🇸 Español',
    'fr_FR': '🇫🇷 Français',
    'it_IT': '🇮🇹 Italiano'
}

for code, name in languages.items():
    self.language_combo.addItem(name, code)

self.language_combo.currentIndexChanged.connect(self.on_language_changed)
language_layout.addWidget(self.language_combo)
language_group.setLayout(language_layout)
```

#### Krok 4.2: Obsługa zmiany języka
```python
def on_language_changed(self, index):
    """Zmienia język aplikacji"""
    language_code = self.language_combo.itemData(index)
    
    if self.translator.load_language(language_code):
        # Zapisz w bazie
        self.save_language_setting(language_code)
        
        # Pokaż komunikat o restarcie
        QMessageBox.information(
            self,
            self.tr("Zmiana języka"),
            self.tr("Aplikacja zostanie zrestartowana aby zastosować nowy język.")
        )
        
        # Restart aplikacji
        self.restart_application()
```

---

### FAZA 5: Tłumaczenie Bazy Danych (1 dzień)

#### Krok 5.1: Domyślne nazwy kolumn
```python
# Zamiast hardcoded:
default_columns = [
    {'name': 'Zadanie', 'type': 'text'},
    {'name': 'Priorytet', 'type': 'list'}
]

# Używaj kluczy tłumaczeń:
default_columns = [
    {'name': self.tr('column.task'), 'type': 'text'},
    {'name': self.tr('column.priority'), 'type': 'list'}
]
```

#### Krok 5.2: Migracja istniejących danych
```python
# tools/migrate_database_translations.py
def migrate_column_names():
    """Migruje nazwy kolumn do systemu tłumaczeń"""
    mapping = {
        'Zadanie': 'column.task',
        'Priorytet': 'column.priority',
        'Status': 'column.status',
        # ... etc
    }
    
    for old_name, translation_key in mapping.items():
        # Aktualizuj w bazie
        pass
```

---

## 5. Języki do Dodania

### Priorytet 1 (Podstawowe):
- ✓ **Polski (pl_PL)** - już jest (źródłowy)
- 🔵 **Angielski (en_US)** - międzynarodowy
- 🔵 **Niemiecki (de_DE)** - duży rynek EU

### Priorytet 2 (Rozszerzenie EU):
- 🟡 **Hiszpański (es_ES)** - duża społeczność
- 🟡 **Francuski (fr_FR)** - EU + Afryka
- 🟡 **Włoski (it_IT)** - EU

### Priorytet 3 (Opcjonalnie):
- 🟢 **Czeski (cs_CZ)** - sąsiad
- 🟢 **Ukraiński (uk_UA)** - duża emigracja do PL
- 🟢 **Rosyjski (ru_RU)** - szerokie użycie

### Priorytet 4 (Przyszłość):
- ⚪ **Chiński uproszczony (zh_CN)** - największy rynek
- ⚪ **Japoński (ja_JP)** - productivity market
- ⚪ **Koreański (ko_KR)**

---

## 6. Harmonogram

### Tydzień 1-2: Fundament
- [ ] Day 1-2: Instalacja narzędzi i struktura
- [ ] Day 3-5: Zmiana hardcoded → tr()
- [ ] Day 6-7: Ekstrakcja tekstów, generacja .ts

### Tydzień 3-4: Angielski
- [ ] Day 8-10: Tłumaczenie EN (Qt Linguist)
- [ ] Day 11-12: Kompilacja, testy
- [ ] Day 13-14: Integracja UI, wybór języka

### Tydzień 5-6: Niemiecki + Testy
- [ ] Day 15-17: Tłumaczenie DE
- [ ] Day 18-19: Testy, poprawki
- [ ] Day 20-21: Dokumentacja

### Tydzień 7+: Kolejne języki
- [ ] Hiszpański (3-4 dni)
- [ ] Francuski (3-4 dni)
- [ ] Włoski (3-4 dni)

---

## 7. Szacunki

### Liczba stringów do przetłumaczenia:
```
Interfejs UI:        ~600 stringów
Komunikaty:          ~150 stringów
Nazwy domyślne:      ~50 stringów
Dokumentacja:        ~30 plików
------------------------
RAZEM:               ~800 stringów + doc
```

### Czas tłumaczenia (1 język):
```
Automatyczne (Google Translate): 1 dzień
Weryfikacja natywna:             2-3 dni
Testy:                           1 dzień
------------------------
RAZEM na język:                  4-5 dni
```

### Koszt tłumaczenia profesjonalnego:
```
Opcja A - Tłumacz ludzki:
800 stringów × 0.10 PLN/słowo × 3 słowa avg = ~240 PLN/język

Opcja B - Google Translate API:
800 stringów × $0.000020/char × 30 chars = ~$0.50/język

Opcja C - Community (darmowe):
GitHub contributors, forum users
```

---

## 8. Narzędzia Pomocnicze

### Automatyczne tłumaczenie (draft):
```python
# tools/auto_translate.py
from googletrans import Translator
import xml.etree.ElementTree as ET

def auto_translate_ts(source_ts, target_lang):
    """Automatycznie tłumaczy plik .ts używając Google Translate"""
    translator = Translator()
    tree = ET.parse(source_ts)
    root = tree.getroot()
    
    for message in root.findall('.//message'):
        source = message.find('source').text
        
        if source:
            translation = translator.translate(source, dest=target_lang).text
            trans_elem = message.find('translation')
            
            if trans_elem is not None:
                trans_elem.text = translation
                trans_elem.attrib.pop('type', None)  # Usuń "unfinished"
    
    tree.write(source_ts.replace('.ts', f'_auto_{target_lang}.ts'))
```

### Weryfikacja kompletności:
```python
# tools/check_translations.py
def check_translation_completeness(ts_file):
    """Sprawdza ile % tłumaczenia jest kompletne"""
    tree = ET.parse(ts_file)
    root = tree.getroot()
    
    total = 0
    translated = 0
    
    for message in root.findall('.//message'):
        total += 1
        trans = message.find('translation')
        
        if trans is not None and 'type' not in trans.attrib:
            translated += 1
    
    percentage = (translated / total * 100) if total > 0 else 0
    print(f'{ts_file}: {percentage:.1f}% ({translated}/{total})')
```

---

## 9. Aktualizacja PyInstaller

### Dołączenie plików .qm do exe:
```python
# pro-ka-po.spec
datas = [
    ('src/i18n/languages/*.qm', 'i18n/languages'),
]
```

---

## 10. Testowanie

### Checklist testów dla każdego języka:
- [ ] Wszystkie menu przetłumaczone
- [ ] Wszystkie dialogi przetłumaczone
- [ ] Wszystkie komunikaty błędów przetłumaczone
- [ ] Tooltips przetłumaczone
- [ ] Formatowanie daty/czasu (locale)
- [ ] Formatowanie liczb (separatory)
- [ ] Długie teksty się mieszczą (UI nie pęka)
- [ ] Znaki specjalne wyświetlane poprawnie
- [ ] Zmiana języka działa (restart)
- [ ] Zapisywanie wyboru języka

---

## 11. Dokumentacja dla Tłumaczy

### Stwórz CONTRIBUTING_TRANSLATIONS.md:
```markdown
# Jak dodać tłumaczenie

1. Pobierz Qt Linguist lub edytuj .ts ręcznie
2. Otwórz plik src/i18n/languages/JĘZYK.ts
3. Przetłumacz stringi
4. Zapisz plik
5. Wyślij Pull Request

Wskazówki:
- Zachowaj formatowanie (%1, %2, %s, %d)
- Sprawdź kontekst przed tłumaczeniem
- Używaj naturalnego języka (nie tłumacz słowo w słowo)
```

---

## 🎯 NASTĘPNY KROK

Czy chcesz abym:
1. **Rozpoczął implementację** (FAZA 1) - utworzenie struktury i TranslationManager?
2. **Przygotował przykład** - pokazał jak zmienić 1-2 pliki na system tłumaczeń?
3. **Stworzył narzędzia** - skrypty do automatyzacji (generate, compile, check)?

**Polecam zacząć od opcji 1 lub 2** - to pozwoli zobaczyć jak to działa w praktyce przed pełną implementacją.
