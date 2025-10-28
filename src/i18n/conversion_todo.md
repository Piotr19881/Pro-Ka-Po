# Lista plików do konwersji na tr()

## Kolejność konwersji (od najprostszych):

1. [ ] **main.py** - 1 stringów
2. [ ] **src\ui\column_delegate.py** - 15 stringów
3. [ ] **src\ui\tag_dialog.py** - 19 stringów
4. [ ] **src\utils\backup_manager.py** - 25 stringów
5. [ ] **src\ui\column_dialog.py** - 29 stringów
6. [ ] **src\ui\task_list_content_dialog.py** - 35 stringów
7. [ ] **src\ui\kanban_view.py** - 39 stringów
8. [ ] **src\ui\quick_task_dialog.py** - 42 stringów
9. [ ] **src\ui\alarm_popup.py** - 68 stringów
10. [ ] **src\ui\math_column_dialog.py** - 72 stringów
11. [ ] **src\ui\list_dialogs.py** - 86 stringów
12. [ ] **src\ui\table_dialogs.py** - 99 stringów
13. [ ] **src\ui\notes_view.py** - 104 stringów
14. [ ] **src\ui\tasks_view.py** - 107 stringów
15. [ ] **src\ui\pomodoro_view.py** - 131 stringów
16. [ ] **src\ui\alarms_view.py** - 144 stringów
17. [ ] **src\ui\theme_manager.py** - 144 stringów
18. [ ] **src\ui\main_window.py** - 690 stringów

## Instrukcje konwersji:

1. Otwórz plik
2. Znajdź stringi literalne (użyj raportu jako pomocy)
3. Zamień na `self.tr("tekst")`
4. Dla stringów z formatowaniem użyj: `self.tr("Tekst: %1").arg(value)`
5. Przetestuj czy aplikacja działa
6. Zaznacz checkbox ✓
