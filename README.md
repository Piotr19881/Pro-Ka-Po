# Pro-Ka-Po V2
## Aplikacja do organizacji zadań

Aplikacja oparta na PyQt6 i SQLite do zarządzania zadaniami z interfejsem Kanban.

### Instalacja

1. Aktywuj środowisko wirtualne:
```powershell
.\.venv\Scripts\Activate.ps1
```

2. Zainstaluj zależności:
```powershell
pip install -r requirements.txt
```

3. Uruchom aplikację:
```powershell
python main.py
```

Lub użyj pliku `run.bat` na Windowsie.

### Funkcjonalności

✅ **Zaimplementowane:**
- ✅ Podstawowy interfejs z trzema sekcjami (nowy poziomy układ)
- ✅ Przyciski nawigacji poziomo (Zadania, KanBan, Tabele, Ustawienia)
- ✅ Sekcja dodawania zadań z polami:
  - Pole tekstowe na zadanie
  - Lista wyboru kategorii
  - Lista wyboru priorytetu
  - Kalendarz wyboru daty i godziny
  - Przycisk "Dodaj"
- ✅ Baza danych SQLite z tabelami zadań i kategorii
- ✅ Podstawowy widok listy zadań
- ✅ **Zarządzanie tabelami i listami słownikowymi:**
  - Zakładka "Tabele" z dwoma sekcjami: Tabele i Listy
  - Przyciski: Dodaj nową, Edytuj, Usuń
  - Dialogi dodawania/edycji tabel (table_dialogs.py)
  - Dialogi dodawania/edycji list słownikowych (list_dialogs.py)
- ✅ Zaawansowany widok ustawień z zakładkami:
  - **Ogólne:** Motyw, język, autostart, powiadomienia
  - **Zadania:** Domyślne ustawienia, automatyzacja
  - **Pomodori:** Czasy pracy/przerw, opcje automatyzacji
  - **KanBan:** Konfiguracja kolumn, limity WIP
  - **Tabele:** Ustawienia wyświetlania, eksport
  - **Pomoc:** Informacje o aplikacji, skróty klawiszowe
- ✅ Sekcja dodawania zadań z polami:
  - Pole tekstowe na zadanie
  - Lista wyboru kategorii
  - Lista wyboru priorytetu
  - Kalendarz wyboru daty i godziny
  - Przycisk "Dodaj zadanie"
- ✅ Baza danych SQLite z tabelami zadań i kategorii
- ✅ Podstawowy widok listy zadań

🚧 **Do rozbudowy:**
- Widok KanBan (przeciąganie zadań)
- Widok tabel z sortowaniem i filtrowaniem
- Edycja i usuwanie zadań
- Zaawansowane ustawienia
- Eksport/import danych
- Powiadomienia i przypomnienia

### Struktura projektu

```
├── src/
│   ├── ui/             # Komponenty interfejsu użytkownika
│   │   └── main_window.py
│   ├── database/       # Warstwa dostępu do danych
│   │   └── db_manager.py
│   └── __init__.py
├── data/               # Pliki bazy danych
├── .venv/             # Środowisko wirtualne Python
├── main.py            # Punkt wejścia aplikacji
├── run.bat            # Skrypt uruchamiający (Windows)
└── requirements.txt   # Zależności Python
```

### Użytkowanie

1. **Nawigacja:** Użyj przycisków u góry okna do przełączania między sekcjami (Zadania, KanBan, Tabele, Alarmy, Ustawienia)
2. **Dodawanie zadań:** W dolnej sekcji wypełnij pole zadania, wybierz opcje i kliknij "Dodaj zadanie"
3. **Widok zadań:** Lista zadań pojawi się w środkowej sekcji
4. **Zarządzanie tabel:** W Ustawieniach → Tabele można tworzyć tabele z różnymi typami kolumn
5. **Alarmy:** Sekcja zarządzania alarmami (popup w rozwoju)
6. **Ustawienia:** Kompleksowa konfiguracja aplikacji w 6 zakładkach
7. **Kategorie:** Dostępne kategorie: Praca, Dom, Nauka, Hobby

### Nowy układ interfejsu

**Sekcja górna:** Poziomy pasek nawigacji z przyciskami
**Sekcja środkowa:** Główna zawartość (widoki: Zadania/KanBan/Tabele/Listy/Ustawienia)  
**Sekcja dolna:** Poziomy panel dodawania zadań (2 wiersze):
- **Wiersz 1:** Pole tekstowe zadania + Przycisk "Dodaj zadanie"
- **Wiersz 2:** Kategoria | Priorytet | Termin (wszystko w jednej linii)

### Wymagania systemowe

- Windows 10/11
- Python 3.8+
- PyQt6
- SQLite (wbudowane w Python)