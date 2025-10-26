import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QComboBox, 
                             QDateTimeEdit, QLabel, QFrame, QSplitter, QStackedWidget,
                             QTabWidget, QCheckBox, QSpinBox, QGroupBox, QGridLayout,
                             QTreeWidget, QTreeWidgetItem, QHeaderView, QDialog,
                             QMessageBox, QTableWidget, QTableWidgetItem,
                             QStyledItemDelegate, QDateEdit, QCalendarWidget,
                             QDoubleSpinBox, QFormLayout, QListWidget, QLineEdit,
                             QScrollArea, QInputDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QDateTime, QDate, QTimer
from PyQt6.QtGui import QFont, QIcon, QKeyEvent, QColor, QPalette
from .pomodoro_view import PomodoroView
from .theme_manager import ThemeManager

class EditableTableWidget(QTableWidget):
    """Rozszerzona QTableWidget z obsługą Enter dla dodawania rekordów"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = None
    
    def set_main_window(self, main_window):
        """Ustaw referencję do głównego okna"""
        self.main_window = main_window
    
    def keyPressEvent(self, e: QKeyEvent | None):
        """Obsługuje naciśnięcia klawiszy"""
        if e and (e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter):
            current_row = self.currentRow()
            
            # Jeśli to ostatni wiersz i jest wypełniony
            if (self.main_window and current_row == self.rowCount() - 1 and 
                self.main_window.is_row_filled(current_row)):
                print("Zatwierdzono nowy rekord klawiszem Enter")
                self.main_window.add_empty_row()
                # Przejdź do nowego pustego wiersza
                self.setCurrentCell(current_row + 1, 1)  # Ustaw kursor na kolumnie "Nazwa"
            else:
                # Domyślne zachowanie Enter
                super().keyPressEvent(e)
        else:
            # Domyślne zachowanie dla innych klawiszy
            super().keyPressEvent(e)

# Dodaj ścieżkę do modułów
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import Database


class DateDelegate(QStyledItemDelegate):
    """Delegat dla kolumn daty - otwiera kalendarz po dwukrotnym kliknięciu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        """Tworzy edytor z kalendarzem"""
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDate(QDate.currentDate())
        return editor
    
    def setEditorData(self, editor, index):
        """Ustawia dane w edytorze"""
        if not isinstance(editor, QDateEdit):
            return
            
        value = ""
        model = index.model()
        if model:
            value = model.data(index, Qt.ItemDataRole.EditRole)
            
        if value:
            try:
                if isinstance(value, str):
                    date = QDate.fromString(value, "yyyy-MM-dd")
                    if date.isValid():
                        editor.setDate(date)
                    else:
                        editor.setDate(QDate.currentDate())
                else:
                    editor.setDate(QDate.currentDate())
            except:
                editor.setDate(QDate.currentDate())
        else:
            editor.setDate(QDate.currentDate())
    
    def setModelData(self, editor, model, index):
        """Zapisuje dane z edytora do modelu"""
        if not isinstance(editor, QDateEdit) or not model:
            return
            
        date = editor.date()
        model.setData(index, date.toString("yyyy-MM-dd"), Qt.ItemDataRole.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Aktualizuje geometrię edytora"""
        if editor:
            editor.setGeometry(option.rect)


class ComboBoxDelegate(QStyledItemDelegate):
    """Delegat dla kolumn lista - pokazuje dropdown z opcjami"""
    
    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.options = options or []
    
    def createEditor(self, parent, option, index):
        """Tworzy edytor ComboBox"""
        editor = QComboBox(parent)
        editor.addItems(self.options)
        return editor
    
    def setEditorData(self, editor, index):
        """Ustawia dane w edytorze"""
        if not isinstance(editor, QComboBox):
            return
            
        value = ""
        model = index.model()
        if model:
            value = model.data(index, Qt.ItemDataRole.EditRole)
            
        if value and value in self.options:
            editor.setCurrentText(str(value))
        elif self.options:
            editor.setCurrentIndex(0)
    
    def setModelData(self, editor, model, index):
        """Zapisuje dane z edytora do modelu"""
        if not isinstance(editor, QComboBox) or not model:
            return
            
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Aktualizuje geometrię edytora"""
        if editor:
            editor.setGeometry(option.rect)


class CurrencyDelegate(QStyledItemDelegate):
    """Delegat dla kolumn walutowych - formatuje jako walutę"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        """Tworzy edytor dla wartości walutowych"""
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(2)
        editor.setMinimum(0.0)
        editor.setMaximum(999999999.99)
        editor.setSuffix(" zł")  # Można dodać suffix dla waluty
        return editor
    
    def setEditorData(self, editor, index):
        """Ustawia dane w edytorze"""
        if not isinstance(editor, QDoubleSpinBox):
            return
            
        value = 0.0
        model = index.model()
        if model:
            raw_value = model.data(index, Qt.ItemDataRole.EditRole)
            if raw_value:
                try:
                    # Usuń znaki waluty i przekonwertuj na float
                    clean_value = str(raw_value).replace(" zł", "").replace(",", ".").strip()
                    value = float(clean_value) if clean_value else 0.0
                except (ValueError, TypeError):
                    value = 0.0
                    
        editor.setValue(value)
    
    def setModelData(self, editor, model, index):
        """Zapisuje dane z edytora do modelu"""
        if not isinstance(editor, QDoubleSpinBox) or not model:
            return
            
        value = editor.value()
        # Zapisz jako sformatowaną wartość z walutą
        formatted_value = f"{value:.2f} zł"
        model.setData(index, formatted_value, Qt.ItemDataRole.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Aktualizuje geometrię edytora"""
        if editor:
            editor.setGeometry(option.rect)
    
    def displayText(self, value, locale):
        """Formatuje tekst wyświetlany w komórce"""
        if value:
            try:
                # Jeśli wartość już zawiera walutę, zwróć ją
                if " zł" in str(value):
                    return str(value)
                # Jeśli nie, sformatuj jako walutę
                clean_value = str(value).replace(",", ".").strip()
                number = float(clean_value)
                return f"{number:.2f} zł"
            except (ValueError, TypeError):
                return str(value)
        return "0.00 zł"


class TaskManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.db_manager = self.db  # Alias dla kompatybilności
        self.theme_manager = ThemeManager()  # Dodaj ThemeManager
        self.current_columns_config = []  # Przechowuje konfigurację kolumn aktualnej tabeli
        
        # Debouncing timer dla optymalizacji
        self.navigation_update_timer = QTimer()
        self.navigation_update_timer.setSingleShot(True)
        self.navigation_update_timer.timeout.connect(self._delayed_navigation_update)
        
        self.init_ui()
        
        # Zastosuj początkowy motyw
        self.apply_theme_to_main_window()
        
        # Dodaj testowe dane tylko jeśli nie ma żadnych tabel I żadnych list słownikowych
        user_tables = self.db.get_user_tables()
        if not user_tables:
            # Sprawdź czy są jakieś listy słownikowe
            dictionary_lists = self.db.get_dictionary_lists()
            if not dictionary_lists:
                print("DEBUG: Brak tabel i list - tworzenie testowych danych")
                self.setup_test_data()  # Dodaj testowe dane
                # Przeładuj po dodaniu testowych danych
                self.load_user_tables()
            else:
                print("DEBUG: Brak tabel ale są listy słownikowe - pomijanie testowych danych")
        else:
            print(f"DEBUG: Znaleziono {len(user_tables)} tabel - pomijanie testowych danych")
    
    def apply_theme_to_main_window(self):
        """Stosuje motyw do głównego okna i nawigacji"""
        self.setStyleSheet(self.theme_manager.get_main_window_style())
        
        # Zastosuj style do nawigacji
        if hasattr(self, 'nav_widget'):
            self.nav_widget.setStyleSheet(self.theme_manager.get_navigation_style())
    
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        self.setWindowTitle("Pro-Ka-Po V2 - Organizator Zadań")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Główny widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Główny layout pionowy
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Górna sekcja - przyciski nawigacji (poziomy układ)
        self.create_navigation_section(main_layout)
        
        # Środkowa sekcja - główna zawartość (pionowy układ)
        self.create_main_content_section(main_layout)
        
        # Dolna sekcja - dodawanie zadań (poziomy układ)
        self.create_add_task_section(main_layout)
        
        # Pokaż domyślną sekcję zadań
        self.show_tasks_view()
        
        # Zastosuj początkowe style do wszystkich komponentów
        if hasattr(self, 'settings_tabs'):  # Jeśli ustawienia już istnieją
            self.apply_theme_to_settings()
    
    def create_navigation_section(self, parent_layout):
        """Tworzy sekcję nawigacji z przyciskami ułożonymi poziomo"""
        nav_frame = QFrame()
        nav_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        nav_frame.setMaximumHeight(80)
        nav_frame.setMinimumHeight(60)
        
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(5)  # Mniejszy spacing
        
        # Przyciski nawigacji w poziomie - wypełniają całą przestrzeń
        self.nav_buttons = {}
        self.current_active_view = "tasks"  # Śledzenie aktywnego widoku
        
        buttons_config = [
            ("Zadania", "tasks"),
            ("KanBan", "kanban"),
            ("Tabele", "tables"),
            ("Notatki", "notes"),
            ("Pomodoro", "pomodoro"),
            ("Alarmy", "alarms"),
            ("Ustawienia", "settings")
        ]
        
        for button_text, button_id in buttons_config:
            btn = QPushButton(button_text)
            btn.setMinimumHeight(40)
            # Ustaw politykę rozmiaru aby przyciski rozciągały się równomiernie
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda checked, bid=button_id: self.switch_view(bid))
            self.nav_buttons[button_id] = btn
            nav_layout.addWidget(btn)
        
        # Ustaw pierwszy przycisk jako aktywny
        self.update_navigation_styles()
        
        parent_layout.addWidget(nav_frame)
    
    def update_navigation_styles(self):
        """Aktualizuje style przycisków nawigacji z debouncing"""
        # Zatrzymaj poprzedni timer i uruchom nowy
        self.navigation_update_timer.stop()
        self.navigation_update_timer.start(50)  # 50ms delay
    
    def _delayed_navigation_update(self):
        """Wykonuje rzeczywistą aktualizację stylów nawigacji"""
        try:
            # Pobierz style dla aktywnego i nieaktywnego przycisku
            active_style = self.theme_manager.get_active_navigation_button_style()
            inactive_style = self.theme_manager.get_navigation_button_style()
            
            # Zastosuj style do wszystkich przycisków
            for button_id, button in self.nav_buttons.items():
                if button_id == self.current_active_view:
                    button.setStyleSheet(active_style)
                else:
                    button.setStyleSheet(inactive_style)
                    
        except Exception as e:
            print(f"Błąd aktualizacji stylów nawigacji: {e}")
    
    def create_main_content_section(self, parent_layout):
        """Tworzy główną sekcję zawartości"""
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Stacked widget dla różnych widoków
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Zapewnij istnienie standardowych kolumn przed utworzeniem widoków
        self.ensure_standard_task_columns()
        
        # Tworzenie różnych widoków
        self.create_tasks_view()
        self.create_kanban_view()
        self.create_tables_view()
        self.create_notes_view()
        self.create_pomodoro_view()
        self.create_alarms_view()
        self.create_settings_view()
        
        parent_layout.addWidget(main_frame)
    
    def create_add_task_section(self, parent_layout):
        """Tworzy sekcję dodawania zadań w układzie poziomym"""
        add_task_frame = QFrame()
        add_task_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        add_task_frame.setMaximumHeight(120)
        add_task_frame.setMinimumHeight(100)
        
        add_task_layout = QVBoxLayout(add_task_frame)
        add_task_layout.setContentsMargins(10, 5, 10, 5)
        add_task_layout.setSpacing(5)
        
        # Tytuł sekcji
        add_title = QLabel("DODAJ ZADANIE")
        add_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        add_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        add_task_layout.addWidget(add_title)
        
        # Pierwszy wiersz - pole tekstowe i przycisk dodaj
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(10)
        
        # Etykieta zadania
        first_row_layout.addWidget(QLabel("Zadanie:"))
        
        # Pole tekstowe zadania
        self.task_input = QTextEdit()
        self.task_input.setMaximumHeight(40)
        self.task_input.setPlaceholderText("Wpisz zadanie...")
        first_row_layout.addWidget(self.task_input, 4)
        
        # Przycisk dodaj
        self.add_button = QPushButton("Dodaj zadanie")
        self.add_button.setMinimumHeight(40)
        self.add_button.setMaximumWidth(120)
        self.add_button.clicked.connect(self.add_new_task)
        first_row_layout.addWidget(self.add_button)
        
        # Checkbox Kanban
        self.kanban_checkbox = QCheckBox("Kanban")
        self.kanban_checkbox.setMinimumHeight(40)
        first_row_layout.addWidget(self.kanban_checkbox)
        
        add_task_layout.addLayout(first_row_layout)

        # Drugi wiersz - wszystkie opcje w jednej linii (kontrolowane przez ustawienia)
        self.second_row_layout = QHBoxLayout()
        self.second_row_layout.setSpacing(15)
        
        # Kategoria
        self.category_label = QLabel("Kategoria:")
        self.second_row_layout.addWidget(self.category_label)
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(100)
        self.load_categories()
        self.second_row_layout.addWidget(self.category_combo)
        
        # Separator 1
        self.separator1 = QLabel("|")
        self.second_row_layout.addWidget(self.separator1)
        
        # Priorytet
        self.priority_label = QLabel("Priorytet:")
        self.second_row_layout.addWidget(self.priority_label)
        self.priority_combo = QComboBox()
        self.priority_combo.setMinimumWidth(100)
        self.priority_combo.addItems(["Niski", "Średni", "Wysoki", "Krytyczny"])
        self.priority_combo.setCurrentText("Średni")
        self.second_row_layout.addWidget(self.priority_combo)
        
        # Separator 2
        self.separator2 = QLabel("|")
        self.second_row_layout.addWidget(self.separator2)
        
        # Data i godzina
        self.datetime_label = QLabel("Termin:")
        self.second_row_layout.addWidget(self.datetime_label)
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setMinimumWidth(150)
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        self.second_row_layout.addWidget(self.datetime_edit)
        
        # Wypełnij pozostałą przestrzeń
        self.second_row_layout.addStretch()
        
        add_task_layout.addLayout(self.second_row_layout)
        
        # Inicjalizuj widoczność elementów dolnego paska
        self.update_bottom_panel_visibility()
        
        parent_layout.addWidget(add_task_frame)
    
    def create_tasks_view(self):
        """Tworzy zaawansowany widok zadań"""
        try:
            from .tasks_view import TasksView
            from database.db_manager import Database
            
            db = Database()
            self.tasks_view = TasksView(db, self.theme_manager)
            self.stacked_widget.addWidget(self.tasks_view)
            
            # Połącz sygnały
            self.tasks_view.task_created.connect(self.on_task_created)
            self.tasks_view.task_updated.connect(self.on_task_updated)
            self.tasks_view.task_deleted.connect(self.on_task_deleted)
            
            # Podepnij funkcjonalność przycisków notatek
            self.setup_note_buttons_functionality()
            
        except Exception as e:
            print(f"Błąd podczas tworzenia widoku zadań: {e}")
            # Fallback do prostego widoku
            tasks_widget = QWidget()
            layout = QVBoxLayout(tasks_widget)
            
            title = QLabel("ZADANIA")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            error_label = QLabel(f"Błąd ładowania widoku zadań: {e}")
            error_label.setStyleSheet(self.theme_manager.get_error_label_style())
            layout.addWidget(error_label)
            
            self.stacked_widget.addWidget(tasks_widget)
    
    def create_kanban_view(self):
        """Tworzy widok KanBan"""
        kanban_widget = QWidget()
        layout = QVBoxLayout(kanban_widget)
        
        title = QLabel("KANBAN")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Placeholder dla KanBan
        placeholder = QLabel("Widok KanBan będzie tutaj...")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(self.theme_manager.get_secondary_label_style())
        layout.addWidget(placeholder)
        
        self.stacked_widget.addWidget(kanban_widget)
    
    def create_tables_view(self):
        """Tworzy widok tabel"""
        tables_widget = QWidget()
        layout = QVBoxLayout(tables_widget)
        
        title = QLabel("TABELE")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, 0)  # Nie rozciągaj
        
        # Panel wyboru tabeli
        tables_selection_panel = self.create_tables_selection_panel()
        layout.addWidget(tables_selection_panel, 0)  # Nie rozciągaj
        
        # Główna tabela z danymi - zajmuje większość miejsca
        self.main_data_table = self.create_editable_data_table()
        layout.addWidget(self.main_data_table, 1)  # Rozciągaj maksymalnie
        
        self.stacked_widget.addWidget(tables_widget)
    
    def create_notes_view(self):
        """Tworzy nowoczesny widok notatek z zagnieżdżaniem"""
        try:
            from .notes_view import NotesView
            
            # Utwórz nowy widok notatek z ThemeManager
            self.notes_view = NotesView(self, self.theme_manager)
            
            # Podłącz sygnały
            self.notes_view.note_created.connect(self.on_note_created)
            self.notes_view.note_updated.connect(self.on_note_updated)
            self.notes_view.note_deleted.connect(self.on_note_deleted)
            
            self.stacked_widget.addWidget(self.notes_view)
            
        except ImportError as e:
            print(f"Błąd importu NotesView: {e}")
            # Fallback - stwórz prosty widok
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)
            error_label = QLabel("Błąd ładowania widoku notatek")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            self.stacked_widget.addWidget(fallback_widget)
    
    def create_tables_selection_panel(self):
        """Tworzy panel wyboru tabeli"""
        panel = QGroupBox("Wybór tabeli")
        layout = QHBoxLayout(panel)
        
        # Etykieta
        layout.addWidget(QLabel("Tabela:"))
        
        # Lista wyboru tabel
        self.tables_combo = QComboBox()
        self.load_user_tables()
        self.tables_combo.currentTextChanged.connect(self.on_table_changed)
        layout.addWidget(self.tables_combo)
        
        layout.addStretch()
        
        # Przycisk konfiguracji tabeli
        config_btn = QPushButton("⚙ Konfiguruj tabelę")
        config_btn.clicked.connect(self.open_table_config)
        config_btn.setToolTip("Otwórz dialog konfiguracji kolumn tabeli")
        layout.addWidget(config_btn)
        
        # Informacje o tabeli
        self.table_info_label = QLabel("Rekordów: 5 | Kolumn: 6")
        # Usuń hardcoded style - zostanie ustawiony przez apply_theme_to_tables_view
        layout.addWidget(self.table_info_label)
        
        return panel
    
    def load_user_tables(self):
        """Ładuje tabele użytkownika z bazy danych"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            db = Database()
            user_tables = db.get_user_tables()
            
            # Wyczyść obecne opcje
            self.tables_combo.clear()
            
            # Dodaj tabele użytkownika
            for table in user_tables:
                self.tables_combo.addItem(table['name'])
            
            print(f"DEBUG: Załadowano {len(user_tables)} tabel użytkownika")
            
            # Jeśli nie ma tabel użytkownika, nie dodawaj placeholderów
            if not user_tables:
                self.tables_combo.addItem("Brak tabel - dodaj nową")
                
        except Exception as e:
            print(f"Błąd podczas ładowania tabel: {e}")
            # Fallback
            self.tables_combo.addItem("Błąd ładowania tabel")
    
    def open_table_config(self):
        """Otwiera konfigurację aktualnej tabeli"""
        from .table_dialogs import TableDialog
        
        current_table = self.tables_combo.currentText()
        print(f"Otwieranie konfiguracji tabeli: {current_table}")
        
        if not current_table or current_table in ["Brak tabel - dodaj nową", "Błąd ładowania tabel"]:
            print("DEBUG: Brak wybranej tabeli do edycji")
            return
        
        try:
            # Pobierz pełne dane tabeli z bazy danych
            table_data = self.get_table_data_for_editing(current_table)
            
            if table_data:
                print(f"DEBUG: Otwieranie dialogu edycji dla tabeli: {table_data.get('name')}")
                dialog = TableDialog(self, table_data, self.theme_manager)
            else:
                print("DEBUG: Nie można pobrać danych tabeli, otwieranie pustego dialogu")
                dialog = TableDialog(self, None, self.theme_manager)
                
            if dialog.exec() == QDialog.DialogCode.Accepted:
                print("Konfiguracja tabeli została zaktualizowana")
                # Odśwież listę tabel
                self.load_user_tables()
                # Odśwież widok tabeli
                self.on_table_changed(current_table)
                
        except Exception as e:
            print(f"DEBUG: Błąd podczas otwierania konfiguracji tabeli: {e}")
            import traceback
            traceback.print_exc()

    def get_table_data_for_editing(self, table_name):
        """Pobiera pełne dane tabeli dla trybu edycji"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            db = Database()
            user_tables = db.get_user_tables()
            
            # Znajdź tabelę o podanej nazwie
            for table in user_tables:
                if table['name'] == table_name:
                    print(f"DEBUG: Znaleziono dane tabeli '{table_name}' z {len(table.get('columns', []))} kolumnami")
                    return table
            
            print(f"DEBUG: Nie znaleziono tabeli '{table_name}' w bazie danych")
            return None
            
        except Exception as e:
            print(f"DEBUG: Błąd podczas pobierania danych tabeli: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_editable_data_table(self):
        """Tworzy edytowalną tabelę danych z pustym wierszem na końcu"""
        from PyQt6.QtWidgets import QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout
        from PyQt6.QtCore import Qt
        
        table = EditableTableWidget()
        table.set_main_window(self)
        table.setRowCount(6)  # 5 rekordów + 1 pusty wiersz
        table.setColumnCount(6)
        
        # Nagłówki kolumn (zgodnie z naszą konfiguracją)
        headers = ["ID", "Nazwa projektu", "Data utworzenia", "Status", "Zakończone", "Priorytet"]
        table.setHorizontalHeaderLabels(headers)
        
        # Przykładowe dane (5 rekordów)
        sample_data = [
            ["1", "Aplikacja Pro-Ka-Po", "2024-10-01", "W trakcie", False, "Wysoki"],
            ["2", "Strona internetowa", "2024-10-15", "Gotowe", True, "Średni"],
            ["3", "System CRM", "2024-10-20", "Nowy", False, "Wysoki"],
            ["4", "Aplikacja mobilna", "2024-10-22", "W trakcie", False, "Niski"],
            ["5", "Dashboard analityczny", "2024-10-24", "Planowane", False, "Średni"],
        ]
        
        # Wypełnienie tabeli danymi
        for row, row_data in enumerate(sample_data):
            for col, value in enumerate(row_data):
                if col == 4:  # Kolumna "Zakończone" (CheckBox)
                    self.create_checkbox_cell(table, row, col, value)
                else:
                    # Zwykły edytowalny tekst
                    item = QTableWidgetItem(str(value))
                    if col == 0:  # ID - tylko do odczytu
                        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    table.setItem(row, col, item)
        
        # Pusty wiersz na końcu (do dodawania nowych rekordów)
        empty_row = len(sample_data)
        base_color, alternate_color, _, text_color = self._get_table_theme_colors()
        for col in range(table.columnCount()):
            if col == 4:  # CheckBox
                self.create_checkbox_cell(table, empty_row, col, False)
            elif col == 0:  # Auto-generowane ID
                next_id = str(len(sample_data) + 1)
                item = QTableWidgetItem(next_id)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                item.setBackground(alternate_color)
                table.setItem(empty_row, col, item)
            else:
                # Puste edytowalne pole z subtelnym podświetleniem
                item = QTableWidgetItem("")
                item.setBackground(base_color)
                # Użyj koloru tekstu motywu, aby wyróżnić stan edycji
                item.setForeground(text_color)
                table.setItem(empty_row, col, item)
        
        # Ustawienia tabeli
        table.resizeColumnsToContents()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Rozciągnij tabelę na cały dostępny obszar
        header = table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)  # Ostatnia kolumna rozciąga się
            # Opcjonalnie: wszystkie kolumny proporcjonalnie
            # header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Ustaw stałą wysokość wierszy (nie rozciągaj)
        vertical_header = table.verticalHeader()
        if vertical_header:
            vertical_header.setDefaultSectionSize(35)  # Ustaw stałą wysokość 35px
            vertical_header.setStretchLastSection(False)  # Nie rozciągaj ostatniego wiersza
        
        # Ustaw minimalną wysokość tabeli
        table.setMinimumHeight(400)
        
        # Zastosuj styl z theme managera zamiast hardcoded style
        table.setStyleSheet(self.theme_manager.get_table_style())
        
        # Obsługa dodawania nowych rekordów
        table.itemChanged.connect(self.on_table_item_changed)
        
        # Przechowaj referencję do tabeli dla obsługi Enter
        self.current_data_table = table
        
        return table
    
    def create_checkbox_cell(self, table, row, col, checked):
        """Tworzy komórkę z CheckBox'em"""
        # Utwórz widget z checkboxem
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        self.configure_table_widget(checkbox)
        checkbox.stateChanged.connect(lambda state, r=row: self.on_data_checkbox_changed(r, state))
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        
        # Ustaw widget w komórce
        table.setCellWidget(row, col, checkbox_widget)
        
        # Utwórz pustą komórkę i ustaw ją jako nieedytowalną żeby zapobiec pokazywaniu edytora tekstowego
        item = QTableWidgetItem("")
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Wyłącz edycję
        table.setItem(row, col, item)
    
    def load_table_columns_config(self, table_name):
        """Ładuje konfigurację kolumn dla wybranej tabeli"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            db = Database()
            user_tables = db.get_user_tables()
            
            # Znajdź tabelę o podanej nazwie
            for table in user_tables:
                if table['name'] == table_name:
                    return table['columns']
            
            return []
        except Exception as e:
            print(f"Błąd podczas ładowania konfiguracji kolumn: {e}")
            return []

    def on_table_changed(self, table_name):
        """Obsługuje zmianę wybranej tabeli"""
        if table_name and table_name != "Brak tabel - dodaj nową" and table_name != "Błąd ładowania tabel":
            print(f"DEBUG: Ładowanie tabeli: {table_name}")
            
            try:
                # Zapisz szerokości kolumn poprzedniej tabeli
                if hasattr(self, 'current_table_id') and self.current_table_id:
                    self.save_current_column_widths()
                
                # Znajdź ID tabeli
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                from database.db_manager import Database
                
                db = Database()
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM user_tables WHERE name = ?', (table_name,))
                result = cursor.fetchone()
                
                if result:
                    self.current_table_id = result[0]
                    print(f"DEBUG: Ustawiono current_table_id: {self.current_table_id}")
                else:
                    self.current_table_id = None
                    print(f"DEBUG: Nie znaleziono ID dla tabeli: {table_name}")
                
                # Załaduj konfigurację kolumn
                columns_config = self.load_table_columns_config(table_name)
                print(f"DEBUG: Załadowano {len(columns_config)} kolumn")
                
                if columns_config:
                    # Zaktualizuj tabelę według konfiguracji
                    self.update_table_with_config(columns_config)
                else:
                    # Fallback - użyj starych przykładowych danych
                    print("DEBUG: Używam fallback danych")
                    self.load_fallback_table_data(table_name)
                    
            except Exception as e:
                print(f"DEBUG: Błąd podczas ładowania tabeli: {e}")
                import traceback
                traceback.print_exc()
                self.clear_table()
        else:
            # Zapisz szerokości kolumn przed czyszczeniem
            if hasattr(self, 'current_table_id') and self.current_table_id:
                self.save_current_column_widths()
            
            # Wyczyść tabelę lub pokaż komunikat
            print("DEBUG: Czyszczenie tabeli")
            self.current_table_id = None
            self.clear_table()
    
    def update_table_with_config(self, columns_config):
        """Aktualizuje tabelę zgodnie z konfiguracją kolumn"""
        if not columns_config:
            self.clear_table()
            return
        
        # Ustaw liczbę kolumn
        self.main_data_table.setColumnCount(len(columns_config))
        
        # Ustaw nagłówki kolumn
        headers = [col['name'] for col in columns_config]
        self.main_data_table.setHorizontalHeaderLabels(headers)
        
        # Zapisz konfigurację kolumn dla późniejszego użycia
        self.current_columns_config = columns_config
        
        # Wyczyść obecne dane
        self.main_data_table.setRowCount(1)  # Jeden pusty wiersz na start
        
        # Ustaw edytory komórek zgodnie z typami kolumn
        self.setup_column_editors()
        
        # Popraw kolorystykę i wygląd tabeli
        self.apply_table_styling(self.main_data_table)
        
        # Przywróć zapisane szerokości kolumn
        self.restore_column_widths()
        
        # Skonfiguruj śledzenie zmian szerokości kolumn
        self.setup_column_width_tracking()
        
        # Dodaj pusty wiersz do edycji
        self.add_empty_row()
        
        print(f"DEBUG: Skonfigurowano tabelę z {len(columns_config)} kolumnami")
    
    def apply_table_styling(self, table, resize_columns=True):
        """Stosuje jednolity styl dla tabeli z opcjonalnym resizing"""
        # Ustaw stałą wysokość wierszy (nie rozciągaj)
        vertical_header = table.verticalHeader()
        if vertical_header:
            vertical_header.setDefaultSectionSize(35)  # Ustaw stałą wysokość 35px
            vertical_header.setStretchLastSection(False)  # Nie rozciągaj ostatniego wiersza
        
        # Ustaw zachowanie kolumn
        header = table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)  # Ostatnia kolumna rozciąga się
        
        # Zastosuj styl z theme managera zamiast hardcoded style
        table.setStyleSheet(self.theme_manager.get_table_style())
        
        # Ustaw podstawowe właściwości
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Resize columns tylko gdy jest to wymagane
        if resize_columns:
            table.resizeColumnsToContents()
    
    def apply_tree_styling(self, tree):
        """Stosuje jednolity styl dla drzew"""
        # Ustaw stałą wysokość wierszy
        tree.setUniformRowHeights(True)
        
        # Zastosuj styl z theme managera zamiast hardcoded style
        tree.setStyleSheet(self.theme_manager.get_tree_style())
    
    def _get_table_theme_colors(self):
        """Wygodny zestaw kolorów tabeli zgodny z aktywnym motywem"""
        colors = self.theme_manager.get_current_colors()
        base_color = QColor(colors['widget_bg'])
        alternate_color = QColor(colors.get('alternating_row', colors['widget_bg']))
        warning_color = QColor(colors.get('warning_color', colors.get('selection_bg', '#ffd43b')))
        text_color = QColor(colors['text_color'])
        return base_color, alternate_color, warning_color, text_color

    def configure_table_widget(self, widget):
        """Konfiguruje widget w komórce tabeli z minimalną stylizacją"""
        # Usuń wszystkie style CSS - zostaw domyślne Qt
        widget.setStyleSheet("")
        colors = self.theme_manager.get_current_colors()
        base_color = QColor(colors['widget_bg'])
        text_color = QColor(colors['text_color'])
        selection_color = QColor(colors['selection_bg'])
        selection_text = QColor(colors['selection_text'])
        
        # Dodatkowe właściwości dla ComboBox
        if isinstance(widget, QComboBox):
            widget.setMinimumHeight(28)
            widget.setMaximumHeight(28)
            # Ustaw font bezpośrednio
            font = widget.font()
            font.setPointSize(9)
            font.setFamily("Segoe UI")
            widget.setFont(font)
            # Ustaw kolory bezpośrednio w palecie
            palette = widget.palette()
            palette.setColor(QPalette.ColorRole.Base, base_color)
            palette.setColor(QPalette.ColorRole.Button, base_color)
            palette.setColor(QPalette.ColorRole.Text, text_color)
            palette.setColor(QPalette.ColorRole.ButtonText, text_color)
            palette.setColor(QPalette.ColorRole.Highlight, selection_color)
            palette.setColor(QPalette.ColorRole.HighlightedText, selection_text)
            widget.setPalette(palette)
        elif isinstance(widget, QCheckBox):
            # Ustaw font bezpośrednio dla CheckBox
            font = widget.font()
            font.setPointSize(9)
            font.setFamily("Segoe UI")
            widget.setFont(font)
            # Ustaw kolory bezpośrednio w palecie
            palette = widget.palette()
            palette.setColor(QPalette.ColorRole.WindowText, text_color)
            palette.setColor(QPalette.ColorRole.Base, base_color)
            widget.setPalette(palette)
        return widget
    
    def clear_table(self):
        """Czyści tabelę"""
        self.main_data_table.setRowCount(0)
        self.main_data_table.setColumnCount(0)
        self.current_columns_config = []
    
    def setup_column_editors(self):
        """Konfiguruje edytory komórek według typów kolumn"""
        if not hasattr(self, 'current_columns_config'):
            print("DEBUG: Brak konfiguracji kolumn")
            return
        
        print(f"DEBUG: Konfigurowanie edytorów dla {len(self.current_columns_config)} kolumn")
        
        for col_index, col_config in enumerate(self.current_columns_config):
            col_type = col_config.get('type', 'Tekstowa')
            print(f"DEBUG: Kolumna {col_index} ({col_config.get('name')}): {col_type}")
            
            try:
                # Ustaw delegat edytora dla całej kolumny
                if col_type == 'Data':
                    print(f"DEBUG: Ustawianie DateDelegate dla kolumny {col_index}")
                    self.main_data_table.setItemDelegateForColumn(col_index, DateDelegate(self))
                elif col_type == 'Lista':
                    # Znajdź przypisaną listę słownikową
                    print(f"DEBUG: Pobieranie opcji listy dla kolumny {col_index}")
                    list_options = self.get_list_options_for_column(col_config)
                    print(f"DEBUG: Opcje listy: {list_options}")
                    self.main_data_table.setItemDelegateForColumn(col_index, ComboBoxDelegate(list_options, self))
                elif col_type == 'Waluta':
                    print(f"DEBUG: Ustawianie CurrencyDelegate dla kolumny {col_index}")
                    self.main_data_table.setItemDelegateForColumn(col_index, CurrencyDelegate(self))
                elif col_type == 'CheckBox':
                    # CheckBox jest już obsługiwany w create_checkbox_cell
                    print(f"DEBUG: CheckBox dla kolumny {col_index} - obsługiwany przez create_checkbox_cell")
                    pass
                else:
                    print(f"DEBUG: Standardowy edytor dla kolumny {col_index}")
                    
            except Exception as e:
                print(f"DEBUG: Błąd przy ustawianiu edytora dla kolumny {col_index}: {e}")
                import traceback
                traceback.print_exc()
    
    def get_list_options_for_column(self, col_config):
        """Pobiera opcje dla kolumny typu Lista"""
        try:
            print(f"DEBUG: get_list_options_for_column wywoływana dla kolumny: {col_config.get('name', 'UNKNOWN')}")
            print(f"DEBUG: col_config: {col_config}")
            
            # Sprawdź czy kolumna ma przypisaną listę słownikową
            if 'dictionary_list_id' in col_config and col_config['dictionary_list_id']:
                list_id = col_config['dictionary_list_id']
                print(f"DEBUG: Znaleziono dictionary_list_id: {list_id}")
                
                # Pobierz opcje z bazy danych
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                from database.db_manager import Database
                
                db = Database()
                conn = db.get_connection()
                
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value FROM dictionary_list_items 
                    WHERE list_id = ? 
                    ORDER BY order_index, value
                """, (list_id,))
                
                options = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG: Znaleziono opcje: {options}")
                return options if options else ["Brak opcji"]
            else:
                print(f"DEBUG: Brak dictionary_list_id w konfiguracji kolumny")
            
            # Fallback - domyślne opcje
            print(f"DEBUG: Używanie domyślnych opcji")
            return ["Opcja 1", "Opcja 2", "Opcja 3"]
            
        except Exception as e:
            print(f"DEBUG: Błąd podczas pobierania opcji listy: {e}")
            import traceback
            traceback.print_exc()
            return ["Błąd ładowania"]
    
    def add_empty_row(self):
        """Dodaje pusty wiersz do edycji"""
        if not hasattr(self, 'current_columns_config') or not self.current_columns_config:
            return
            
        # Dodaj nowy wiersz
        current_rows = self.main_data_table.rowCount()
        self.main_data_table.setRowCount(current_rows + 1)
        
        row = current_rows  # Nowy wiersz
        base_color, alternate_color, warning_color, text_color = self._get_table_theme_colors()
        
        for col_index, col_config in enumerate(self.current_columns_config):
            col_type = col_config.get('type', 'Tekstowa')
            
            if col_type == 'CheckBox':
                self.create_checkbox_cell(self.main_data_table, row, col_index, False)
            else:
                item = QTableWidgetItem("")
                item.setBackground(base_color)
                self.main_data_table.setItem(row, col_index, item)
    
    def load_fallback_table_data(self, table_name):
        """Ładuje przykładowe dane gdy nie ma konfiguracji z bazy"""
        print(f"Przełączono na tabelę: {table_name}")
        
        # Symulacja różnych danych dla różnych tabel
        table_data = {
            "Projekty": [
                ["1", "Aplikacja Pro-Ka-Po", "2024-10-01", "W trakcie", False, "Wysoki"],
                ["2", "Strona internetowa", "2024-10-15", "Gotowe", True, "Średni"],
                ["3", "System CRM", "2024-10-20", "Nowy", False, "Wysoki"],
            ],
            "Zadania": [
                ["1", "Projektowanie UI", "2024-10-01", "Gotowe", True, "Wysoki"],
                ["2", "Implementacja backendu", "2024-10-02", "W trakcie", False, "Wysoki"],
                ["3", "Testy jednostkowe", "2024-10-03", "Nowy", False, "Średni"],
                ["4", "Dokumentacja", "2024-10-04", "Nowy", False, "Niski"],
            ],
            "Klienci": [
                ["1", "Firma ABC Sp. z o.o.", "2024-01-15", "Aktywny", True, "VIP"],
                ["2", "XYZ Corporation", "2024-02-20", "Aktywny", True, "Standard"],
                ["3", "StartupTech", "2024-03-10", "Potencjalny", False, "Standard"],
            ]
        }
        
        # Aktualizuj dane w tabeli
        data = table_data.get(table_name, [])
        self.refresh_table_data(data)
        
        # Aktualizuj informacje o tabeli
        if hasattr(self, 'table_info_label'):
            self.table_info_label.setText(f"Rekordów: {len(data)} | Kolumn: {self.main_data_table.columnCount()}")
    
    def refresh_table_data(self, data):
        """Odświeża dane w tabeli z optymalizacjami wydajności"""
        # Dla dużych zbiorów danych (>100 rekordów) używaj lazy loading
        if len(data) > 100:
            self.refresh_table_data_lazy(data)
            return
            
        # Wyłącz sygnały podczas masowego wypełniania danych
        self.main_data_table.blockSignals(True)
        
        try:
            # Wyczyść obecne dane
            self.main_data_table.setRowCount(len(data) + 1)  # +1 dla pustego wiersza
            
            # Batch creation of items - tworzymy wszystkie items naraz
            items_to_set = []
            base_color, alternate_color, warning_color, text_color = self._get_table_theme_colors()
            
            # Wypełnij danymi
            for row, row_data in enumerate(data):
                for col, value in enumerate(row_data):
                    if col == 4:  # CheckBox
                        self.create_checkbox_cell(self.main_data_table, row, col, value)
                    else:
                        item = QTableWidgetItem(str(value))
                        if col == 0:  # ID - tylko do odczytu
                            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                        items_to_set.append((row, col, item))
            
            # Ustaw wszystkie items naraz
            for row, col, item in items_to_set:
                self.main_data_table.setItem(row, col, item)
            
            # Pusty wiersz na końcu
            empty_row = len(data)
            for col in range(self.main_data_table.columnCount()):
                if col == 4:  # CheckBox
                    self.create_checkbox_cell(self.main_data_table, empty_row, col, False)
                elif col == 0:  # Auto-generowane ID
                    next_id = str(len(data) + 1)
                    item = QTableWidgetItem(next_id)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setBackground(alternate_color)
                    self.main_data_table.setItem(empty_row, col, item)
                else:
                    # Puste edytowalne pole z białym tłem
                    item = QTableWidgetItem("")
                    item.setBackground(base_color)
                    self.main_data_table.setItem(empty_row, col, item)
            
        finally:
            # Zawsze włącz z powrotem sygnały
            self.main_data_table.blockSignals(False)
        
        # Wykonaj operacje wymagające sygnałów na końcu
        self.main_data_table.resizeColumnsToContents()
        
        # Zastosuj styling tylko raz na końcu bez dodatkowego resize
        self.apply_table_styling(self.main_data_table, resize_columns=False)
    
    def refresh_table_data_lazy(self, data):
        """Lazy loading dla dużych zbiorów danych - ładuje tylko pierwszych 50 wierszy"""
        print(f"DEBUG: Używanie lazy loading dla {len(data)} rekordów")
        
        # Załaduj tylko pierwsze 50 rekordów
        visible_data = data[:50]
        self.all_data = data  # Zachowaj wszystkie dane
        
        # Wyłącz sygnały
        self.main_data_table.blockSignals(True)
        
        try:
            # Ustaw liczbę wierszy na wszystkie dane + pusty wiersz + wiersz "Załaduj więcej"
            self.main_data_table.setRowCount(len(visible_data) + 2)
            base_color, alternate_color, warning_color, text_color = self._get_table_theme_colors()
            
            # Wypełnij widocznymi danymi
            for row, row_data in enumerate(visible_data):
                for col, value in enumerate(row_data):
                    if col == 4:  # CheckBox
                        self.create_checkbox_cell(self.main_data_table, row, col, value)
                    else:
                        item = QTableWidgetItem(str(value))
                        if col == 0:  # ID - tylko do odczytu
                            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                        self.main_data_table.setItem(row, col, item)
            
            # Dodaj wiersz "Załaduj więcej..." jeśli są ukryte dane
            if len(data) > 50:
                load_more_row = len(visible_data)
                load_more_item = QTableWidgetItem(f"--- Załaduj więcej ({len(data) - 50} ukrytych rekordów) ---")
                load_more_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                load_more_item.setBackground(warning_color)
                self.main_data_table.setItem(load_more_row, 1, load_more_item)
            
            # Pusty wiersz na końcu
            empty_row = len(visible_data) + (1 if len(data) > 50 else 0)
            for col in range(self.main_data_table.columnCount()):
                if col == 4:  # CheckBox
                    self.create_checkbox_cell(self.main_data_table, empty_row, col, False)
                elif col == 0:  # Auto-generowane ID
                    next_id = str(len(data) + 1)
                    item = QTableWidgetItem(next_id)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setBackground(alternate_color)
                    self.main_data_table.setItem(empty_row, col, item)
                else:
                    # Puste edytowalne pole z białym tłem
                    item = QTableWidgetItem("")
                    item.setBackground(base_color)
                    self.main_data_table.setItem(empty_row, col, item)
                    
        finally:
            self.main_data_table.blockSignals(False)
        
        self.main_data_table.resizeColumnsToContents()
        self.apply_table_styling(self.main_data_table, resize_columns=False)
    
    def on_table_item_changed(self, item):
        """Obsługuje zmianę zawartości komórki"""
        row = item.row()
        col = item.column()
        
        # Jeśli to ostatni wiersz (pusty wiersz do dodawania)
        if row == self.main_data_table.rowCount() - 1:
            # Sprawdź czy wiersz został wypełniony
            if self.is_row_filled(row):
                print(f"Dodano nowy rekord w wierszu {row + 1}")
                # Dodaj kolejny pusty wiersz
                self.add_empty_row()
    
    def is_row_filled(self, row):
        """Sprawdza czy wiersz jest wypełniony (przynajmniej nazwa)"""
        name_item = self.main_data_table.item(row, 1)  # Kolumna "Nazwa"
        return name_item and name_item.text().strip() != ""
        
        # Usuń podświetlenie z poprzedniego wiersza
        prev_row = new_row - 1
        for col in range(1, self.main_data_table.columnCount()):
            if col != 4:  # Pomijamy CheckBox
                prev_item = self.main_data_table.item(prev_row, col)
                if prev_item:
                    prev_item.setBackground(self._get_table_theme_colors()[0])
    
    def on_data_checkbox_changed(self, row, state):
        """Obsługuje zmianę stanu CheckBox'a w tabeli danych"""
        is_checked = state == 2  # Qt.CheckState.Checked
        
        # Bezpieczne pobranie nazwy z tabeli
        name_item = self.main_data_table.item(row, 1)
        item_name = name_item.text() if name_item else f"Rekord {row + 1}"
        
        status_text = "zakończony" if is_checked else "niezakończony"
        print(f"'{item_name}' został oznaczony jako {status_text}")
        
        # TODO: Zapisz zmianę w bazie danych
    
    def create_pomodoro_view(self):
        """Tworzy widok Pomodoro"""
        try:
            # Utwórz instancję nowego widoku Pomodoro z ThemeManager
            self.pomodoro_view = PomodoroView(self.theme_manager)
            self.stacked_widget.addWidget(self.pomodoro_view)
            
        except Exception as e:
            print(f"Błąd tworzenia widoku Pomodoro: {e}")
            # Fallback - stwórz prosty widok
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)
            error_label = QLabel("Błąd ładowania widoku Pomodoro")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            self.stacked_widget.addWidget(fallback_widget)
    
    def create_alarms_view(self):
        """Tworzy widok alarmów"""
        try:
            from .alarms_view import AlarmsView
            
            # Utwórz instancję nowego widoku alarmów z ThemeManager
            self.alarms_view = AlarmsView(self.theme_manager)
            
            # Połącz sygnały
            self.alarms_view.alarm_triggered.connect(self.on_alarm_triggered)
            self.alarms_view.timer_finished.connect(self.on_timer_finished)
            
            self.stacked_widget.addWidget(self.alarms_view)
            
        except Exception as e:
            print(f"Błąd podczas tworzenia widoku alarmów: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback - prosty widok
            alarms_widget = QWidget()
            layout = QVBoxLayout(alarms_widget)
            
            title = QLabel("ALARMY")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            error_label = QLabel(f"Błąd ładowania widoku alarmów:\n{str(e)}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet(self.theme_manager.get_error_label_style())
            layout.addWidget(error_label)
            
            layout.addStretch()
            self.stacked_widget.addWidget(alarms_widget)

    def on_alarm_triggered(self, alarm_data):
        """Obsługuje uruchomienie alarmu"""
        print(f"ALARM TRIGGERED: {alarm_data['name']} - {alarm_data['time']}")
        # Tu można dodać dodatkowe akcje, np. miganie ikony w tray
    
    def on_timer_finished(self, timer_data):
        """Obsługuje zakończenie timera"""
        print(f"TIMER FINISHED: {timer_data['name']}")
        # Tu można dodać dodatkowe akcje
    
    def open_alarms_popup(self):
        """Kompatybilność - przekierowanie do widoku alarmów"""
        # Przełącz na widok alarmów
        if hasattr(self, 'alarms_view'):
            self.stacked_widget.setCurrentWidget(self.alarms_view)
            print("Przełączono na widok alarmów")
    
    def create_settings_view(self):
        """Tworzy widok ustawień z zakładkami"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        title = QLabel("USTAWIENIA")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tab Widget dla różnych kategorii ustawień
        self.settings_tabs = QTabWidget()
        layout.addWidget(self.settings_tabs)
        
        # Tworzenie zakładek
        self.create_general_settings_tab()
        self.create_task_columns_settings_tab()  # Nowa zakładka dla kolumn
        self.create_kanban_settings_tab()
        self.create_tables_settings_tab()
        self.create_help_tab()
        
        self.stacked_widget.addWidget(settings_widget)
    
    def create_general_settings_tab(self):
        """Tworzy zakładkę ustawień ogólnych"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Grupa ustawień aplikacji
        app_group = QGroupBox("Ustawienia aplikacji")
        app_layout = QGridLayout(app_group)
        
        # Motyw aplikacji
        app_layout.addWidget(QLabel("Motyw:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Jasny", "Ciemny", "Systemowy"])
        app_layout.addWidget(self.theme_combo, 0, 1)
        
        # Język aplikacji
        app_layout.addWidget(QLabel("Język:"), 1, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Polski", "English"])
        app_layout.addWidget(self.language_combo, 1, 1)
        
        # Autostart
        self.autostart_check = QCheckBox("Uruchom automatycznie z systemem")
        app_layout.addWidget(self.autostart_check, 2, 0, 1, 2)
        
        layout.addWidget(app_group)
        
        # Grupa powiadomień
        notif_group = QGroupBox("Powiadomienia")
        notif_layout = QGridLayout(notif_group)
        
        self.notifications_check = QCheckBox("Włącz powiadomienia")
        self.notifications_check.setChecked(True)
        notif_layout.addWidget(self.notifications_check, 0, 0, 1, 2)
        
        self.sound_check = QCheckBox("Dźwięk powiadomień")
        notif_layout.addWidget(self.sound_check, 1, 0, 1, 2)
        
        layout.addWidget(notif_group)
        layout.addStretch()
        
        # Połącz sygnały
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        self.settings_tabs.addTab(tab, "Ogólne")
    
    def on_theme_changed(self, theme_name):
        """Obsługuje zmianę motywu"""
        try:
            # Aktualizuj motyw w głównym ThemeManager
            self.theme_manager.set_theme(theme_name)
            
            # Zastosuj motyw do głównego okna
            self.apply_theme_to_main_window()
            
            # Aktualizuj motyw w widoku zadań jeśli istnieje
            if hasattr(self, 'tasks_view'):
                self.tasks_view.apply_theme()
            
            # Aktualizuj motyw w widoku notatek jeśli istnieje
            if hasattr(self, 'notes_view'):
                self.apply_theme_to_notes_view()
                
            # Aktualizuj motyw w widoku Pomodoro jeśli istnieje
            if hasattr(self, 'pomodoro_view'):
                self.apply_theme_to_pomodoro_view()
                
            # Aktualizuj motyw w widoku alarmów jeśli istnieje
            if hasattr(self, 'alarms_view'):
                self.apply_theme_to_alarms_view()
            
            # Aktualizuj motyw w widoku tabel
            self.apply_theme_to_tables_view()
            
            # Aktualizuj motyw w ustawieniach
            self.apply_theme_to_settings()
                
            print(f"Zmieniono motyw na: {theme_name}")
        except Exception as e:
            print(f"Błąd zmiany motywu: {e}")
    
    def apply_theme_to_notes_view(self):
        """Stosuje motyw do widoku notatek"""
        if hasattr(self, 'notes_view') and hasattr(self.notes_view, 'apply_theme'):
            self.notes_view.apply_theme()
            
    def apply_theme_to_pomodoro_view(self):
        """Stosuje motyw do widoku Pomodoro"""
        if hasattr(self, 'pomodoro_view') and hasattr(self.pomodoro_view, 'apply_theme'):
            self.pomodoro_view.apply_theme()
            
    def apply_theme_to_alarms_view(self):
        """Stosuje motyw do widoku alarmów"""
        if hasattr(self, 'alarms_view') and hasattr(self.alarms_view, 'apply_theme'):
            self.alarms_view.apply_theme()
    
    def apply_theme_to_tables_view(self):
        """Stosuje motyw do widoku tabel"""
        # Zaktualizuj style tabel w głównym oknie
        if hasattr(self, 'current_table'):
            self.current_table.setStyleSheet(self.theme_manager.get_table_style())
        if hasattr(self, 'table_tree'):
            self.table_tree.setStyleSheet(self.theme_manager.get_tree_style())
        
        # Zaktualizuj główną tabelę danych
        if hasattr(self, 'main_data_table'):
            self.main_data_table.setStyleSheet(self.theme_manager.get_table_style())
        
        # Zaktualizuj elementy panelu wyboru tabeli
        if hasattr(self, 'tables_combo'):
            self.tables_combo.setStyleSheet(self.theme_manager.get_combo_style())
        
        if hasattr(self, 'table_info_label'):
            # Usuń stare hardkodowane style i zastąp motywem
            self.table_info_label.setStyleSheet(self.theme_manager.get_label_style())
        
        # Znajdź i zaktualizuj wszystkie komponenty widoku tabel
        tables_widgets = []
        
        # Znajdź widżet "TABELE" w stacked widget
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            if widget and hasattr(widget, 'layout'):
                # Sprawdź czy to widok tabel poprzez szukanie charakterystycznych elementów
                for j in range(widget.layout().count()):
                    item = widget.layout().itemAt(j)
                    if item and item.widget():
                        child = item.widget()
                        if isinstance(child, QLabel) and child.text() == "TABELE":
                            tables_widgets.append(widget)
                            break
        
        # Zastosuj style do znalezionych widżetów tabel
        for widget in tables_widgets:
            if widget:
                widget.setStyleSheet(self.theme_manager.get_main_widget_style())
                
                # Znajdź i zaktualizuj wszystkie etykiety
                for label in widget.findChildren(QLabel):
                    if label.text() == "TABELE":
                        # Specjalny styl dla tytułu
                        label.setStyleSheet(self.theme_manager.get_title_label_style())
                    else:
                        label.setStyleSheet(self.theme_manager.get_label_style())
                
                # Znajdź i zaktualizuj wszystkie GroupBox
                for group_box in widget.findChildren(QGroupBox):
                    group_box.setStyleSheet(self.theme_manager.get_group_box_style())
                
                # Znajdź i zaktualizuj wszystkie przyciski
                for button in widget.findChildren(QPushButton):
                    button.setStyleSheet(self.theme_manager.get_button_style())
    
    def apply_theme_to_settings(self):
        """Stosuje motyw do widoku ustawień"""
        if hasattr(self, 'settings_tabs'):
            self.settings_tabs.setStyleSheet(self.theme_manager.get_tab_widget_style())
            
            # Aktualizuj wszystkie kontrolki w ustawieniach
            for i in range(self.settings_tabs.count()):
                tab = self.settings_tabs.widget(i)
                if tab:
                    tab.setStyleSheet(self.theme_manager.get_main_widget_style())
                    
                    # Aktualizuj GroupBox
                    for group_box in tab.findChildren(QGroupBox):
                        group_box.setStyleSheet(self.theme_manager.get_group_box_style())
                    
                    # Aktualizuj ComboBox
                    for combo in tab.findChildren(QComboBox):
                        combo.setStyleSheet(self.theme_manager.get_combo_style())
                    
                    # Aktualizuj CheckBox
                    for checkbox in tab.findChildren(QCheckBox):
                        checkbox.setStyleSheet(self.theme_manager.get_checkbox_style())
                    
                    # Aktualizuj SpinBox
                    for spinbox in tab.findChildren(QSpinBox):
                        spinbox.setStyleSheet(self.theme_manager.get_spin_box_style())
                    
                    # Aktualizuj tabele i drzewa
                    for table in tab.findChildren(QTableWidget):
                        table.setStyleSheet(self.theme_manager.get_table_style())

                    for tree in tab.findChildren(QTreeWidget):
                        tree.setStyleSheet(self.theme_manager.get_tree_style())

                    # Aktualizuj listy
                    for list_widget in tab.findChildren(QListWidget):
                        list_widget.setStyleSheet(self.theme_manager.get_list_style())

                    # Aktualizuj Labels
                    for label in tab.findChildren(QLabel):
                        label.setStyleSheet(self.theme_manager.get_label_style())
    
    def create_task_columns_settings_tab(self):
        """Tworzy zakładkę ustawień kolumn zadań"""
        tab = QWidget()
        
        # Główny layout ze scroll area
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area dla długiej zawartości
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # === SEKCJA ZARZĄDZANIA KOLUMNAMI I TAGAMI ===
        management_layout = QHBoxLayout()
        
        # ZARZĄDZANIE KOLUMNAMI (2/3 szerokości)
        columns_group = QGroupBox("Zarządzanie kolumnami")
        columns_layout = QVBoxLayout(columns_group)
        
        # Tabela kolumn z rozwijalnymi komboboxami
        self.columns_table = QTableWidget()
        self.columns_table.setColumnCount(5)
        self.columns_table.setHorizontalHeaderLabels(["Nazwa", "Typ", "Widoczna", "W dolnym pasku", "Wartość domyślna"])
        self.columns_table.setMinimumHeight(250)  # Zwiększona wysokość
        _, alternate_color, _, _ = self._get_table_theme_colors()
        
        # Ustawienia nagłówka
        header = self.columns_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.columns_table.setAlternatingRowColors(True)
        self.columns_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Ustaw większą wysokość wierszy dla widgetów w komórkach
        vertical_header = self.columns_table.verticalHeader()
        vertical_header.setDefaultSectionSize(45)  # Zwiększona wysokość wierszy dla ComboBox
        
        # Zastosuj stylizację tabeli z theme_manager
        self.columns_table.setStyleSheet(self.theme_manager.get_table_style())
        
        columns_layout.addWidget(self.columns_table)
        
        # Przyciski zarządzania kolumnami
        columns_buttons_layout = QHBoxLayout()
        
        add_column_btn = QPushButton("Dodaj kolumnę")
        add_column_btn.clicked.connect(self.add_custom_column)
        columns_buttons_layout.addWidget(add_column_btn)
        
        edit_column_btn = QPushButton("Edytuj kolumnę")
        edit_column_btn.clicked.connect(self.edit_custom_column)
        columns_buttons_layout.addWidget(edit_column_btn)
        
        delete_column_btn = QPushButton("Usuń kolumnę")
        delete_column_btn.clicked.connect(self.delete_custom_column)
        columns_buttons_layout.addWidget(delete_column_btn)
        
        columns_buttons_layout.addSpacing(20)  # Odstęp między grupami przycisków
        
        move_up_btn = QPushButton("⬆ Przesuń w górę")
        move_up_btn.clicked.connect(self.move_column_up)
        columns_buttons_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("⬇ Przesuń w dół")
        move_down_btn.clicked.connect(self.move_column_down)
        columns_buttons_layout.addWidget(move_down_btn)
        
        columns_buttons_layout.addStretch()
        columns_layout.addLayout(columns_buttons_layout)
        
        # ZARZĄDZANIE TAGAMI (1/3 szerokości)
        tags_group = QGroupBox("Zarządzanie tagami zadań")
        tags_layout = QVBoxLayout(tags_group)
        
        self.tags_list = QListWidget()
        self.tags_list.setMinimumHeight(250)  # Zwiększona wysokość
        tags_layout.addWidget(self.tags_list)
        
        tags_buttons_layout = QHBoxLayout()
        
        add_tag_btn = QPushButton("Dodaj tag")
        add_tag_btn.clicked.connect(self.add_task_tag)
        tags_buttons_layout.addWidget(add_tag_btn)
        
        edit_tag_btn = QPushButton("Edytuj tag")
        edit_tag_btn.clicked.connect(self.edit_task_tag)
        tags_buttons_layout.addWidget(edit_tag_btn)
        
        delete_tag_btn = QPushButton("Usuń tag")
        delete_tag_btn.clicked.connect(self.delete_task_tag)
        tags_buttons_layout.addWidget(delete_tag_btn)
        
        tags_layout.addLayout(tags_buttons_layout)
        
        # Dodaj do layoutu z proporcjami 2:1
        management_layout.addWidget(columns_group, 2)
        management_layout.addWidget(tags_group, 1)
        
        layout.addLayout(management_layout)
        
        # === SEKCJA ZARZĄDZANIA LISTAMI ZADAŃ ===
        task_lists_group = QGroupBox("Zarządzanie listami zadań")
        task_lists_layout = QVBoxLayout(task_lists_group)
        
        self.task_lists_widget = QListWidget()
        self.task_lists_widget.setMinimumHeight(180)
        
        # Zastosuj stylizację dla listy zadań
        self.task_lists_widget.setStyleSheet(self.theme_manager.get_list_style())
        
        task_lists_layout.addWidget(self.task_lists_widget)
        
        task_lists_buttons_layout = QHBoxLayout()
        
        add_task_list_btn = QPushButton("Dodaj listę")
        add_task_list_btn.clicked.connect(self.add_task_list)
        task_lists_buttons_layout.addWidget(add_task_list_btn)
        
        edit_task_list_btn = QPushButton("Edytuj listę")
        edit_task_list_btn.clicked.connect(self.edit_task_list)
        task_lists_buttons_layout.addWidget(edit_task_list_btn)
        
        edit_list_content_btn = QPushButton("Edytuj zawartość")
        edit_list_content_btn.clicked.connect(self.edit_task_list_content)
        task_lists_buttons_layout.addWidget(edit_list_content_btn)
        
        delete_task_list_btn = QPushButton("Usuń listę")
        delete_task_list_btn.clicked.connect(self.delete_task_list)
        task_lists_buttons_layout.addWidget(delete_task_list_btn)
        
        task_lists_buttons_layout.addStretch()
        task_lists_layout.addLayout(task_lists_buttons_layout)
        
        layout.addWidget(task_lists_group)
        
        # === SEKCJA USTAWIEŃ ZADAŃ ===
        settings_group = QGroupBox("Ustawienia zadań")
        settings_layout = QVBoxLayout(settings_group)
        
        # Archiwizacja ukończonych zadań
        archive_layout = QHBoxLayout()
        self.archive_completed_check = QCheckBox("Archiwizuj ukończone zadania po")
        archive_layout.addWidget(self.archive_completed_check)
        
        self.archive_time_spin = QSpinBox()
        self.archive_time_spin.setRange(1, 365)
        self.archive_time_spin.setValue(30)
        self.archive_time_spin.setSuffix(" dniach")
        archive_layout.addWidget(self.archive_time_spin)
        
        archive_layout.addStretch()
        settings_layout.addLayout(archive_layout)
        
        # Automatyczne przenoszenie ukończonych
        self.auto_move_completed_check = QCheckBox("Automatycznie przenoś ukończone pod nieukończone")
        settings_layout.addWidget(self.auto_move_completed_check)
        
        layout.addWidget(settings_group)
        
        # Dodaj elastyczność
        layout.addStretch()
        
        # Ustaw scroll widget
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Załaduj istniejące dane
        self.load_task_columns()
        self.load_task_tags()
        self.load_task_lists()
        
        self.settings_tabs.addTab(tab, "Konfiguracja zadań")
    
    def create_pomodoro_settings_tab(self):
        """Tworzy zakładkę ustawień Pomodoro"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Grupa czasów Pomodoro
        time_group = QGroupBox("Ustawienia czasów")
        time_layout = QGridLayout(time_group)
        
        # Czas pracy
        time_layout.addWidget(QLabel("Czas pracy:"), 0, 0)
        self.work_time_spin = QSpinBox()
        self.work_time_spin.setRange(1, 120)
        self.work_time_spin.setValue(25)
        self.work_time_spin.setSuffix(" min")
        time_layout.addWidget(self.work_time_spin, 0, 1)
        
        # Krótka przerwa
        time_layout.addWidget(QLabel("Krótka przerwa:"), 1, 0)
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 30)
        self.short_break_spin.setValue(5)
        self.short_break_spin.setSuffix(" min")
        time_layout.addWidget(self.short_break_spin, 1, 1)
        
        # Długa przerwa
        time_layout.addWidget(QLabel("Długa przerwa:"), 2, 0)
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(5, 60)
        self.long_break_spin.setValue(15)
        self.long_break_spin.setSuffix(" min")
        time_layout.addWidget(self.long_break_spin, 2, 1)
        
        # Liczba sesji do długiej przerwy
        time_layout.addWidget(QLabel("Sesje do długiej przerwy:"), 3, 0)
        self.sessions_to_long_break_spin = QSpinBox()
        self.sessions_to_long_break_spin.setRange(2, 10)
        self.sessions_to_long_break_spin.setValue(4)
        time_layout.addWidget(self.sessions_to_long_break_spin, 3, 1)
        
        layout.addWidget(time_group)
        
        # Grupa opcji
        options_group = QGroupBox("Opcje")
        options_layout = QVBoxLayout(options_group)
        
        self.auto_start_breaks_check = QCheckBox("Automatycznie rozpoczynaj przerwy")
        options_layout.addWidget(self.auto_start_breaks_check)
        
        self.auto_start_pomodoros_check = QCheckBox("Automatycznie rozpoczynaj następne Pomodoro")
        options_layout.addWidget(self.auto_start_pomodoros_check)
        
        layout.addWidget(options_group)
        layout.addStretch()
        
        self.settings_tabs.addTab(tab, "Pomodori")
    
    def create_kanban_settings_tab(self):
        """Tworzy zakładkę ustawień KanBan"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Grupa kolumn
        columns_group = QGroupBox("Konfiguracja kolumn")
        columns_layout = QGridLayout(columns_group)
        
        # Kolumny do wyświetlenia
        columns_layout.addWidget(QLabel("Wyświetlane kolumny:"), 0, 0, 1, 2)
        
        self.show_todo_check = QCheckBox("Do zrobienia")
        self.show_todo_check.setChecked(True)
        columns_layout.addWidget(self.show_todo_check, 1, 0)
        
        self.show_in_progress_check = QCheckBox("W trakcie")
        self.show_in_progress_check.setChecked(True)
        columns_layout.addWidget(self.show_in_progress_check, 1, 1)
        
        self.show_review_check = QCheckBox("Do sprawdzenia")
        columns_layout.addWidget(self.show_review_check, 2, 0)
        
        self.show_done_check = QCheckBox("Gotowe")
        self.show_done_check.setChecked(True)
        columns_layout.addWidget(self.show_done_check, 2, 1)
        
        layout.addWidget(columns_group)
        
        # Grupa limitów WIP
        wip_group = QGroupBox("Limity WIP (Work In Progress)")
        wip_layout = QGridLayout(wip_group)
        
        self.enable_wip_check = QCheckBox("Włącz limity WIP")
        wip_layout.addWidget(self.enable_wip_check, 0, 0, 1, 2)
        
        wip_layout.addWidget(QLabel("Limit 'W trakcie':"), 1, 0)
        self.wip_limit_spin = QSpinBox()
        self.wip_limit_spin.setRange(1, 20)
        self.wip_limit_spin.setValue(3)
        wip_layout.addWidget(self.wip_limit_spin, 1, 1)
        
        layout.addWidget(wip_group)
        layout.addStretch()
        
        self.settings_tabs.addTab(tab, "KanBan")
    
    def create_tables_settings_tab(self):
        """Tworzy zakładkę ustawień tabel z zarządzaniem tabelami i listami"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Główny layout poziomy dla dwóch sekcji
        main_horizontal_layout = QHBoxLayout()
        layout.addLayout(main_horizontal_layout)
        
        # === SEKCJA TABEL ===
        tables_section = self.create_tables_section()
        main_horizontal_layout.addWidget(tables_section)
        
        # === SEKCJA LIST SŁOWNIKOWYCH ===
        lists_section = self.create_lists_section()
        main_horizontal_layout.addWidget(lists_section)
        
        self.settings_tabs.addTab(tab, "Tabele")
    
    def create_tables_section(self):
        """Tworzy sekcję zarządzania tabelami"""
        tables_group = QGroupBox("Tabele (bez tabeli zadań)")
        tables_layout = QVBoxLayout(tables_group)
        
        # Drzewo tabel
        self.tables_tree = QTreeWidget()
        self.tables_tree.setHeaderLabels(["ID", "Nazwa tabeli", "Opis"])
        self.tables_tree.setRootIsDecorated(False)
        self.tables_tree.setAlternatingRowColors(True)
        
        # Ustawienia kolumn
        header = self.tables_tree.header()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Nazwa
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Opis
        
        # Załaduj prawdziwe tabele z bazy danych
        self.update_tables_tree()
        
        # Popraw wygląd drzewa tabel
        self.apply_tree_styling(self.tables_tree)
        
        tables_layout.addWidget(self.tables_tree)
        
        # Przyciski akcji dla tabel
        tables_buttons_layout = QHBoxLayout()
        
        self.add_table_btn = QPushButton("Dodaj nową")
        self.add_table_btn.clicked.connect(self.add_new_table)
        tables_buttons_layout.addWidget(self.add_table_btn)
        
        self.edit_table_btn = QPushButton("Edytuj")
        self.edit_table_btn.clicked.connect(self.edit_selected_table)
        self.edit_table_btn.setEnabled(False)
        tables_buttons_layout.addWidget(self.edit_table_btn)
        
        self.delete_table_btn = QPushButton("Usuń")
        self.delete_table_btn.clicked.connect(self.delete_selected_table)
        self.delete_table_btn.setEnabled(False)
        tables_buttons_layout.addWidget(self.delete_table_btn)
        
        tables_buttons_layout.addStretch()
        tables_layout.addLayout(tables_buttons_layout)
        
        # Podłącz sygnał zaznaczenia
        self.tables_tree.itemSelectionChanged.connect(self.on_table_selection_changed)
        
        return tables_group
    
    def create_lists_section(self):
        """Tworzy sekcję zarządzania listami słownikowymi"""
        lists_group = QGroupBox("Listy słownikowe")
        lists_layout = QVBoxLayout(lists_group)
        
        # Drzewo list
        self.lists_tree = QTreeWidget()
        self.lists_tree.setHeaderLabels(["ID", "Nazwa listy", "Opis"])
        self.lists_tree.setRootIsDecorated(False)
        self.lists_tree.setAlternatingRowColors(True)
        
        # Ustawienia kolumn
        header = self.lists_tree.header()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Nazwa
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Opis
        
        # Załaduj prawdziwe listy z bazy danych
        self.refresh_lists_list()
        
        # Popraw wygląd drzewa list
        self.apply_tree_styling(self.lists_tree)
        
        lists_layout.addWidget(self.lists_tree)
        
        # Przyciski akcji dla list
        lists_buttons_layout = QHBoxLayout()
        
        self.add_list_btn = QPushButton("Dodaj nową")
        self.add_list_btn.clicked.connect(self.add_new_list)
        lists_buttons_layout.addWidget(self.add_list_btn)
        
        self.edit_list_btn = QPushButton("Edytuj")
        self.edit_list_btn.clicked.connect(self.edit_selected_list)
        self.edit_list_btn.setEnabled(False)
        lists_buttons_layout.addWidget(self.edit_list_btn)
        
        self.delete_list_btn = QPushButton("Usuń")
        self.delete_list_btn.clicked.connect(self.delete_selected_list)
        self.delete_list_btn.setEnabled(False)
        lists_buttons_layout.addWidget(self.delete_list_btn)
        
        lists_buttons_layout.addStretch()
        lists_layout.addLayout(lists_buttons_layout)
        
        # Podłącz sygnał zaznaczenia
        self.lists_tree.itemSelectionChanged.connect(self.on_list_selection_changed)
        
        return lists_group
    
    def load_sample_lists(self):
        """Ładuje przykładowe listy słownikowe"""
        sample_lists = [
            ("1", "Statusy projektów", "Do zrobienia, W trakcie, Gotowe, Anulowane"),
            ("2", "Typy klientów", "Nowy, Stały, VIP, Nieaktywny"),
            ("3", "Priorytety", "Niski, Średni, Wysoki, Krytyczny"),
            ("4", "Działy firmy", "IT, Marketing, Sprzedaż, HR, Finanse"),
        ]
        
        for list_id, name, description in sample_lists:
            item = QTreeWidgetItem([list_id, name, description])
            self.lists_tree.addTopLevelItem(item)
    
    def on_table_selection_changed(self):
        """Obsługuje zmianę zaznaczenia w drzewie tabel"""
        has_selection = bool(self.tables_tree.selectedItems())
        self.edit_table_btn.setEnabled(has_selection)
        self.delete_table_btn.setEnabled(has_selection)
    
    def on_list_selection_changed(self):
        """Obsługuje zmianę zaznaczenia w drzewie list"""
        has_selection = bool(self.lists_tree.selectedItems())
        self.edit_list_btn.setEnabled(has_selection)
        self.delete_list_btn.setEnabled(has_selection)
    
    # === METODY AKCJI DLA TABEL ===
    def add_new_table(self):
        """Dodaje nową tabelę"""
        from .table_dialogs import TableDialog
        
        dialog = TableDialog(self, None, self.theme_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # TODO: Odśwież listę tabel
            print("Tabela została dodana")
            self.refresh_tables_list()
    
    def edit_selected_table(self):
        """Edytuje wybraną tabelę"""
        selected_items = self.tables_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            table_name = item.text(1)
            
            # Pobierz pełne dane tabeli z bazy danych
            try:
                # Znajdź tabelę w user_tables
                user_tables = self.db.get_user_tables()
                table_data = None
                
                for table in user_tables:
                    if table['name'] == table_name:
                        table_data = table
                        break
                
                if table_data:
                    print(f"DEBUG: Edycja tabeli {table_name} z {len(table_data.get('columns', []))} kolumnami")
                    
                    from .table_dialogs import TableDialog
                    
                    dialog = TableDialog(self, table_data, self.theme_manager)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        print("Tabela została zaktualizowana")
                        self.refresh_tables_list()
                        # Przeładuj aktualną tabelę jeśli to ta sama
                        current_table = self.tables_combo.currentText()
                        if current_table == table_name:
                            self.on_table_changed(table_name)
                else:
                    QMessageBox.warning(self, "Błąd", f"Nie znaleziono tabeli {table_name}")
                    
            except Exception as e:
                print(f"DEBUG: Błąd podczas edycji tabeli: {e}")
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Błąd", f"Błąd podczas ładowania danych tabeli: {e}")
    
    def delete_selected_table(self):
        """Usuwa wybraną tabelę"""
        selected_items = self.tables_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            table_name = item.text(1)
            
            print(f"DEBUG: Próba usunięcia tabeli: '{table_name}'")
            print(f"DEBUG: Zaznaczony element w drzewie: ID={item.text(0)}, Nazwa='{item.text(1)}'")
            
            from .table_dialogs import ConfirmDeleteDialog
            
            dialog = ConfirmDeleteDialog(self, table_name)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    # Znajdź ID tabeli
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from database.db_manager import Database
                    
                    db = Database()
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    
                    # Pobierz ID tabeli
                    cursor.execute('SELECT id FROM user_tables WHERE name = ?', (table_name,))
                    result = cursor.fetchone()
                    
                    print(f"DEBUG: Wyszukiwanie tabeli '{table_name}' w bazie: {result}")
                    
                    if result:
                        table_id = result[0]
                        print(f"DEBUG: Znaleziono tabelę ID={table_id}, usuwanie...")
                        # Usuń tabelę z bazy danych
                        db.delete_user_table(table_id)
                        
                        # Usuń z interfejsu
                        index = self.tables_tree.indexOfTopLevelItem(item)
                        if index >= 0:
                            self.tables_tree.takeTopLevelItem(index)
                            print(f"DEBUG: Usunięto tabelę '{table_name}' z interfejsu")
                            
                        # Odśwież listę tabel w combo box
                        self.load_user_tables()
                        print(f"DEBUG: Odświeżono listę tabel")
                    else:
                        print(f"BŁĄD: Nie znaleziono tabeli '{table_name}' w bazie danych")
                        # Usuń z interfejsu mimo że nie ma w bazie
                        index = self.tables_tree.indexOfTopLevelItem(item)
                        if index >= 0:
                            self.tables_tree.takeTopLevelItem(index)
                            print(f"DEBUG: Usunięto nieistniejącą tabelę '{table_name}' z interfejsu")
                        
                except Exception as e:
                    print(f"Błąd podczas usuwania tabeli: {e}")
                    import traceback
                    traceback.print_exc()
    
    # === METODY AKCJI DLA LIST ===
    def add_new_list(self):
        """Dodaje nową listę słownikową"""
        from .list_dialogs import ListDialog
        
        dialog = ListDialog(self, None, self.theme_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # TODO: Odśwież listę list
            print("Lista została dodana")
            self.refresh_lists_list()
    
    def edit_selected_list(self):
        """Edytuje wybraną listę słownikową"""
        selected_items = self.lists_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            list_id = int(item.text(0))
            
            # Pobierz pełne dane listy z bazy danych
            try:
                list_data = self.db.get_dictionary_list_by_id(list_id)
                
                if not list_data:
                    QMessageBox.warning(self, "Błąd", "Nie znaleziono danych listy w bazie danych")
                    return
                
                from .list_dialogs import ListDialog
                
                dialog = ListDialog(self, list_data, self.theme_manager, context="table")
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    # TODO: Odśwież listę list
                    print("Lista została zaktualizowana")
                    self.refresh_lists_list()
                    
            except Exception as e:
                print(f"Błąd podczas ładowania danych listy: {e}")
                QMessageBox.critical(self, "Błąd", f"Błąd podczas ładowania danych listy: {e}")
    
    def delete_selected_list(self):
        """Usuwa wybraną listę słownikową"""
        selected_items = self.lists_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            list_name = item.text(1)
            
            from .list_dialogs import ConfirmDeleteListDialog
            
            dialog = ConfirmDeleteListDialog(self, list_name, self.theme_manager)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    # Znajdź ID listy
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from database.db_manager import Database
                    
                    db = Database()
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    
                    # Pobierz ID listy
                    cursor.execute('SELECT id FROM dictionary_lists WHERE name = ?', (list_name,))
                    result = cursor.fetchone()
                    
                    if result:
                        list_id = result[0]
                        # Usuń listę z bazy danych
                        db.delete_dictionary_list(list_id)
                        
                        # Usuń z interfejsu
                        index = self.lists_tree.indexOfTopLevelItem(item)
                        if index >= 0:
                            self.lists_tree.takeTopLevelItem(index)
                            print(f"Usunięto listę: {list_name}")
                            
                        # Odśwież listę słowników
                        self.refresh_lists_list()
                    else:
                        print(f"Nie znaleziono listy: {list_name}")
                        
                except Exception as e:
                    print(f"Błąd podczas usuwania listy: {e}")
                    import traceback
                    traceback.print_exc()
    
    def refresh_tables_list(self):
        """Odświeża listę tabel"""
        print("DEBUG: Odświeżanie listy tabel...")
        self.load_user_tables()  # Załaduj ponownie tabele z bazy danych
        
        # Odśwież również drzewo tabel jeśli istnieje
        if hasattr(self, 'tables_tree'):
            self.update_tables_tree()
    
    def update_tables_tree(self):
        """Aktualizuje drzewo tabel"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            # Debug: sprawdź bezpośrednio w bazie danych
            db = Database()
            print(f"DEBUG: Używana ścieżka bazy danych: {db.db_path}")
            
            # Sprawdź bezpośrednio z bazy
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM user_tables ORDER BY name")
                direct_tables = cursor.fetchall()
                print(f"DEBUG: Bezpośrednie zapytanie do bazy: {direct_tables}")
            
            user_tables = db.get_user_tables()
            
            print(f"DEBUG: update_tables_tree - załadowano {len(user_tables)} tabel z bazy:")
            for table in user_tables:
                print(f"DEBUG:   - ID: {table['id']}, Nazwa: '{table['name']}'")
            
            # Wyczyść obecne elementy
            old_items_count = self.tables_tree.topLevelItemCount()
            print(f"DEBUG: Usuwanie {old_items_count} starych elementów z drzewa")
            self.tables_tree.clear()
            
            # Dodaj tabele użytkownika
            for table in user_tables:
                item = QTreeWidgetItem([
                    str(table['id']), 
                    table['name'], 
                    table.get('description', ''),
                    table.get('created_at', '')
                ])
                self.tables_tree.addTopLevelItem(item)
                print(f"DEBUG: Dodano do drzewa: ID={table['id']}, Nazwa='{table['name']}'")
                
            print(f"DEBUG: Drzewo tabel zaktualizowane - {self.tables_tree.topLevelItemCount()} elementów")
        except Exception as e:
            print(f"DEBUG: Błąd podczas aktualizacji drzewa tabel: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_lists_list(self):
        """Odświeża listę list słownikowych"""
        print("DEBUG: Odświeżanie listy list słownikowych...")
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            db = Database()
            lists = db.get_dictionary_lists()
            print(f"DEBUG: Załadowano {len(lists)} list słownikowych")
            
            # Wyczyść obecne elementy w drzewie list
            if hasattr(self, 'lists_tree'):
                self.lists_tree.clear()
                
                # Dodaj listy do drzewa
                for list_data in lists:
                    item = QTreeWidgetItem([
                        str(list_data['id']),
                        list_data['name'],
                        list_data.get('description', ''),
                        list_data.get('type', 'Inne'),
                        str(len(list_data.get('items', [])))
                    ])
                    self.lists_tree.addTopLevelItem(item)
                
                print(f"DEBUG: Dodano {len(lists)} list do drzewa")
            else:
                print("DEBUG: lists_tree nie istnieje")
                
        except Exception as e:
            print(f"DEBUG: Błąd podczas ładowania list: {e}")
            import traceback
            traceback.print_exc()
    
    def create_help_tab(self):
        """Tworzy zakładkę pomocy"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Informacje o aplikacji
        info_group = QGroupBox("O aplikacji")
        info_layout = QVBoxLayout(info_group)
        
        app_info = QLabel("""
        <h3>Pro-Ka-Po V2</h3>
        <p><b>Wersja:</b> 2.0.0</p>
        <p><b>Autor:</b> Twój Team</p>
        <p><b>Opis:</b> Aplikacja do organizacji zadań z funkcjami KanBan i Pomodoro</p>
        """)
        app_info.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_layout.addWidget(app_info)
        
        layout.addWidget(info_group)
        
        # Skróty klawiszowe
        shortcuts_group = QGroupBox("Skróty klawiszowe")
        shortcuts_layout = QVBoxLayout(shortcuts_group)
        
        shortcuts_text = QLabel("""
        <b>Ctrl + N</b> - Dodaj nowe zadanie<br>
        <b>Ctrl + S</b> - Zapisz ustawienia<br>
        <b>Ctrl + 1</b> - Przełącz na widok Zadania<br>
        <b>Ctrl + 2</b> - Przełącz na widok KanBan<br>
        <b>Ctrl + 3</b> - Przełącz na widok Tabele<br>
        <b>Ctrl + Q</b> - Zamknij aplikację<br>
        <b>F1</b> - Pomoc<br>
        """)
        shortcuts_layout.addWidget(shortcuts_text)
        
        layout.addWidget(shortcuts_group)
        
        # Przyciski akcji
        actions_group = QGroupBox("Akcje")
        actions_layout = QHBoxLayout(actions_group)
        
        save_settings_btn = QPushButton("Zapisz ustawienia")
        save_settings_btn.clicked.connect(self.save_settings)
        actions_layout.addWidget(save_settings_btn)
        
        reset_settings_btn = QPushButton("Przywróć domyślne")
        reset_settings_btn.clicked.connect(self.reset_settings)
        actions_layout.addWidget(reset_settings_btn)
        
        actions_layout.addStretch()
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        self.settings_tabs.addTab(tab, "Pomoc")
    
    def save_settings(self):
        """Zapisuje ustawienia aplikacji"""
        # TODO: Implementacja zapisywania ustawień do pliku konfiguracyjnego
        print("Ustawienia zostały zapisane!")
    
    def reset_settings(self):
        """Przywraca domyślne ustawienia"""
        # TODO: Implementacja przywracania domyślnych ustawień
        print("Przywrócono domyślne ustawienia!")
    
    def switch_view(self, view_id):
        """Przełącza widok na podstawie wybranego przycisku"""
        # Aktualizuj aktywny widok
        self.current_active_view = view_id
        
        # Aktualizuj style przycisków
        self.update_navigation_styles()
        
        # Przełącz widok
        view_mapping = {
            "tasks": 0,
            "kanban": 1,
            "tables": 2,
            "notes": 3,
            "pomodoro": 4,
            "alarms": 5,
            "settings": 6
        }
        
        if view_id in view_mapping:
            self.stacked_widget.setCurrentIndex(view_mapping[view_id])
            if view_id == "tasks":
                self.refresh_tasks_list()
    
    def show_tasks_view(self):
        """Pokazuje widok zadań"""
        self.switch_view("tasks")
    
    def load_categories(self):
        """Ładuje kategorie do combo box"""
        categories = self.db.get_categories()
        self.category_combo.clear()
        for category in categories:
            self.category_combo.addItem(category[1])  # category[1] to nazwa
    
    def add_new_task(self):
        """Dodaje nowe zadanie"""
        task_text = self.task_input.toPlainText().strip()
        if not task_text:
            return
        
        category = self.category_combo.currentText()
        priority_map = {"Niski": "low", "Średni": "medium", "Wysoki": "high", "Krytyczny": "critical"}
        priority = priority_map.get(self.priority_combo.currentText(), "medium")
        due_date = self.datetime_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        
        # Dodaj zadanie do bazy danych
        self.db.add_task(
            title=task_text,
            category=category,
            priority=priority,
            due_date=due_date
        )
        
        # Wyczyść pole tekstowe
        self.task_input.clear()
        
        # Odśwież listę zadań jeśli jesteśmy w widoku zadań
        if self.stacked_widget.currentIndex() == 0:
            self.refresh_tasks_list()
    
    def refresh_tasks_list(self):
        """Odświeża listę zadań - nowa implementacja dla zaawansowanego widoku"""
        try:
            if hasattr(self, 'tasks_view') and self.tasks_view:
                self.tasks_view.load_tasks()
        except Exception as e:
            print(f"Błąd odświeżania listy zadań: {e}")
    
    def on_task_created(self, task_data):
        """Obsługuje utworzenie nowego zadania"""
        try:
            # TODO: Dodaj do bazy danych
            print(f"Utworzono nowe zadanie: {task_data['task']}")
        except Exception as e:
            print(f"Błąd podczas zapisywania zadania: {e}")
    
    def on_task_updated(self, task_id, task_data):
        """Obsługuje aktualizację zadania"""
        try:
            # TODO: Aktualizuj w bazie danych
            print(f"Zaktualizowano zadanie {task_id}")
        except Exception as e:
            print(f"Błąd podczas aktualizacji zadania: {e}")
    
    def on_task_deleted(self, task_id):
        """Obsługuje usunięcie zadania"""
        try:
            # TODO: Usuń z bazy danych
            print(f"Usunięto zadanie {task_id}")
        except Exception as e:
            print(f"Błąd podczas usuwania zadania: {e}")
    
    def setup_note_buttons_functionality(self):
        """Ustawia funkcjonalność przycisków notatek w widoku zadań"""
        if not hasattr(self, 'tasks_view') or not self.tasks_view:
            return
        
        try:
            # Zastąp metodę open_task_note w tasks_view
            def custom_open_task_note(task_id):
                self.handle_note_button_click(task_id)
            
            # Przypisz nową metodę
            self.tasks_view.open_task_note = custom_open_task_note
            
            print("Podłączono funkcjonalność przycisków notatek")
        except Exception as e:
            print(f"Błąd podczas ustawiania funkcjonalności przycisków notatek: {e}")
    
    def handle_note_button_click(self, task_id):
        """Obsługuje kliknięcie przycisku notatki dla zadania"""
        try:
            from database.db_manager import Database
            
            db = Database()
            
            # Pobierz dane zadania
            task = db.get_task(task_id)
            if not task:
                print(f"Nie znaleziono zadania o ID: {task_id}")
                return
            
            task_title = task.get('title', f'Zadanie {task_id}')
            note_id = task.get('note_id')
            
            if note_id:
                # Notatka już istnieje - otwórz ją
                self.switch_view("notes")
                if hasattr(self, 'notes_view') and self.notes_view:
                    # Poczekaj na przełączenie widoku i wybierz notatkę
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(100, lambda: self.notes_view.select_note_in_tree(note_id))
            else:
                # Utwórz nową notatkę
                from datetime import datetime
                note_title = f"Notatka - {task_title}"
                note_content = f"Notatka do zadania: {task_title}\n\nData utworzenia: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                # Dodaj notatkę do bazy
                new_note_id = db.add_note(note_title, note_content)
                
                if new_note_id:
                    # Połącz zadanie z notatką
                    db.update_task(task_id, note_id=new_note_id)
                    
                    # Przełącz na widok notatek i otwórz nową notatkę
                    self.switch_view("notes")
                    if hasattr(self, 'notes_view') and self.notes_view:
                        # Odśwież drzewo notatek i wybierz nową notatkę
                        from PyQt6.QtCore import QTimer
                        def delayed_actions():
                            self.notes_view.load_notes_from_database()
                            self.notes_view.select_note_in_tree(new_note_id)
                        QTimer.singleShot(100, delayed_actions)
                    
                    # Odśwież widok zadań aby zaktualizować ikony przycisków
                    if hasattr(self, 'tasks_view') and self.tasks_view:
                        self.tasks_view.load_tasks()
                    
                    print(f"Utworzono notatkę {new_note_id} dla zadania {task_id}")
                else:
                    print("Błąd podczas tworzenia notatki")
                    
        except Exception as e:
            print(f"Błąd podczas obsługi przycisku notatki: {e}")
    
    def refresh_tasks_tags(self):
        """Odświeża tagi w widoku zadań po zmianach w ustawieniach"""
        try:
            if hasattr(self, 'tasks_view') and self.tasks_view:
                self.tasks_view.update_tags_from_settings()
                self.tasks_view.refresh_tasks()  # Odśwież zadania z nowymi kolorami tagów
                print("Odświeżono tagi w widoku zadań")
        except Exception as e:
            print(f"Błąd odświeżania tagów w widoku zadań: {e}")
    
    def setup_test_data(self):
        """Tworzy testowe dane dla demonstracji funkcjonalności"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Sprawdź czy istnieje tabela testowa z kolumnami Date i Lista
            cursor.execute("""
                SELECT COUNT(*) FROM user_tables 
                WHERE name = 'Test_Delegaty'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Utwórz tabelę testową
                cursor.execute("""
                    INSERT INTO user_tables (name, description) 
                    VALUES ('Test_Delegaty', 'Tabela testowa dla delegatów kolumn')
                """)
                
                table_id = cursor.lastrowid
                
                # Dodaj kolumny różnych typów
                test_columns = [
                    ("ID", "Numeryczna", ""),
                    ("Nazwa", "Tekstowa", ""),
                    ("Data", "Data", ""),
                    ("Status", "Lista", "status_options"),
                    ("Aktywny", "CheckBox", ""),
                    ("Priorytet", "Lista", "priority_options")
                ]
                
                for col_name, col_type, dict_list in test_columns:
                    cursor.execute("""
                        INSERT INTO user_table_columns 
                        (table_id, name, type, dictionary_list, column_order) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (table_id, col_name, col_type, dict_list, len(test_columns)))
                
                # Dodaj listy słownikowe
                test_lists = [
                    ("status_options", "Opcje statusu", ["Nowy", "W trakcie", "Gotowe", "Anulowany"]),
                    ("priority_options", "Opcje priorytetu", ["Niski", "Średni", "Wysoki", "Krytyczny"])
                ]
                
                list_id_mapping = {}
                
                for list_name, description, options in test_lists:
                    # Sprawdź czy lista już istnieje
                    cursor.execute("""
                        SELECT id FROM dictionary_lists WHERE name = ?
                    """, (list_name,))
                    
                    existing = cursor.fetchone()
                    if existing:
                        list_id = existing[0]
                    else:
                        # Dodaj listę słownikową
                        cursor.execute("""
                            INSERT INTO dictionary_lists (name, description, type) 
                            VALUES (?, ?, 'static')
                        """, (list_name, description))
                        list_id = cursor.lastrowid
                    
                    list_id_mapping[list_name] = list_id
                    
                    # Usuń stare elementy listy
                    cursor.execute("""
                        DELETE FROM dictionary_list_items WHERE list_id = ?
                    """, (list_id,))
                    
                    # Dodaj elementy listy
                    for index, option in enumerate(options):
                        cursor.execute("""
                            INSERT INTO dictionary_list_items (list_id, value, order_index) 
                            VALUES (?, ?, ?)
                        """, (list_id, option, index))
                
                # Zaktualizuj kolumny z ID list słownikowych
                cursor.execute("""
                    UPDATE user_table_columns 
                    SET dictionary_list_id = ? 
                    WHERE table_id = ? AND dictionary_list = 'status_options'
                """, (list_id_mapping.get('status_options'), table_id))
                
                cursor.execute("""
                    UPDATE user_table_columns 
                    SET dictionary_list_id = ? 
                    WHERE table_id = ? AND dictionary_list = 'priority_options'
                """, (list_id_mapping.get('priority_options'), table_id))
                
                conn.commit()
                print("DEBUG: Utworzono testową tabelę z delegatami")
                
        except Exception as e:
            print(f"Błąd podczas tworzenia testowych danych: {e}")
    
    def open_new_table_dialog(self):
        """Otwiera dialog tworzenia nowej tabeli"""
        from .table_dialogs import TableDialog
        
        dialog = TableDialog(self, None, self.theme_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Odśwież listę tabel
            self.load_user_tables()
            print("Nowa tabela została utworzona i dodana do listy")

    # === METODY ZARZĄDZANIA SZEROKOŚCIAMI KOLUMN ===
    def restore_column_widths(self):
        """Przywraca zapisane szerokości kolumn dla aktualnej tabeli"""
        if not hasattr(self, 'current_table_id') or not self.current_table_id:
            return
            
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            db = Database()
            saved_widths = db.get_column_widths(self.current_table_id)
            
            # Zastosuj zapisane szerokości
            for column_index, width in saved_widths.items():
                if column_index < self.main_data_table.columnCount():
                    self.main_data_table.setColumnWidth(column_index, width)
                    print(f"DEBUG: Przywrócono szerokość kolumny {column_index}: {width}px")
            
        except Exception as e:
            print(f"DEBUG: Błąd podczas przywracania szerokości kolumn: {e}")

    def save_current_column_widths(self):
        """Zapisuje aktualne szerokości kolumn"""
        if not hasattr(self, 'current_table_id') or not self.current_table_id:
            return
            
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            # Pobierz aktualne szerokości kolumn
            column_widths = []
            for i in range(self.main_data_table.columnCount()):
                width = self.main_data_table.columnWidth(i)
                column_widths.append(width)
            
            db = Database()
            db.save_column_widths(self.current_table_id, column_widths)
            
        except Exception as e:
            print(f"DEBUG: Błąd podczas zapisywania szerokości kolumn: {e}")

    def setup_column_width_tracking(self):
        """Konfiguruje śledzenie zmian szerokości kolumn"""
        header = self.main_data_table.horizontalHeader()
        if header:
            # Połącz sygnał zmiany szerokości kolumny z zapisywaniem
            header.sectionResized.connect(self.on_column_resized)

    def on_column_resized(self, logical_index, old_size, new_size):
        """Obsługuje zmianę szerokości kolumny"""
        print(f"DEBUG: Kolumna {logical_index} zmieniona z {old_size}px na {new_size}px")
        # Zapisz szerokości po małym opóźnieniu (żeby nie zapisywać przy każdej małej zmianie)
        if hasattr(self, '_width_save_timer'):
            self._width_save_timer.stop()
        
        from PyQt6.QtCore import QTimer
        self._width_save_timer = QTimer()
        self._width_save_timer.timeout.connect(self.save_current_column_widths)
        self._width_save_timer.setSingleShot(True)
        self._width_save_timer.start(1000)  # Zapisz po 1 sekundzie
    
    # === OBSŁUGA SYGNAŁÓW NOTATEK ===
    def on_note_created(self, note_data):
        """Obsługuje utworzenie nowej notatki"""
        print(f"Utworzono notatkę: {note_data.get('title', 'Bez tytułu')}")
        # Tu można dodać integrację z bazą danych
    
    def on_note_updated(self, note_data):
        """Obsługuje aktualizację notatki"""
        print(f"Zaktualizowano notatkę: {note_data.get('title', 'Bez tytułu')}")
        # Tu można dodać zapis do bazy danych
    
    def on_note_deleted(self, note_id):
        """Obsługuje usunięcie notatki"""
        print(f"Usunięto notatkę o ID: {note_id}")
        # Tu można dodać usunięcie z bazy danych

    # === ZARZĄDZANIE KOLUMNAMI ZADAŃ ===
    
    def ensure_standard_task_columns(self):
        """Zapewnia że standardowe kolumny zadań istnieją w bazie danych"""
        try:
            # Standardowe kolumny z kolejnością
            standard_columns = [
                {"name": "ID", "type": "Liczbowa", "visible": True, "in_panel": False, "editable": False, "default_value": "", "column_order": 1},
                {"name": "Data dodania", "type": "Data", "visible": True, "in_panel": False, "editable": False, "default_value": "", "column_order": 2},
                {"name": "Status", "type": "CheckBox", "visible": True, "in_panel": False, "editable": True, "default_value": "", "column_order": 3},
                {"name": "Zadanie", "type": "Tekstowa", "visible": True, "in_panel": False, "editable": False, "default_value": "", "column_order": 4},
                {"name": "Notatka", "type": "Tekstowa", "visible": True, "in_panel": False, "editable": True, "default_value": "", "column_order": 5},
                {"name": "TAG", "type": "Lista", "visible": True, "in_panel": True, "editable": True, "default_value": "", "column_order": 6},
                {"name": "Data realizacji", "type": "Data", "visible": False, "in_panel": False, "editable": False, "default_value": "", "column_order": 7},
                {"name": "KanBan", "type": "CheckBox", "visible": True, "in_panel": True, "editable": True, "default_value": "", "column_order": 8},
                {"name": "Archiwum", "type": "CheckBox", "visible": False, "in_panel": False, "editable": False, "default_value": "", "column_order": 9}
            ]
            
            # Pobierz istniejące kolumny
            existing_columns = self.db_manager.get_task_columns()
            existing_names = [col['name'] for col in existing_columns]
            
            # Dodaj brakujące standardowe kolumny
            for std_col in standard_columns:
                if std_col['name'] not in existing_names:
                    print(f"Dodaję brakującą standardową kolumnę: {std_col['name']}")
                    self.db_manager.add_task_column(
                        name=std_col['name'],
                        col_type=std_col['type'],
                        visible=std_col['visible'],
                        in_panel=std_col['in_panel'],
                        default_value=std_col['default_value']
                    )
            
            print("Sprawdzono i uzupełniono standardowe kolumny zadań")
            
        except Exception as e:
            print(f"Błąd przy zapewnianiu standardowych kolumn: {e}")
            import traceback
            traceback.print_exc()
    
    def load_task_columns(self):
        """Ładuje istniejące kolumny zadań"""
        try:
            _, alternate_color, _, _ = self._get_table_theme_colors()
            # Kolor dla zablokowanych pól (czerwony dla obu motywów)
            locked_color = QColor("#ffcccc")  # Jasny czerwony dla trybu jasnego
            if self.theme_manager.current_theme == 'dark':
                locked_color = QColor("#5c2020")  # Ciemny czerwony dla trybu ciemnego
            
            # Standardowe kolumny z ustawieniami blokowania
            standard_column_settings = {
                "ID": {"locked_visible": False, "locked_panel": False},
                "Data dodania": {"locked_visible": False, "locked_panel": False}, 
                "Status": {"locked_visible": True, "locked_panel": True},
                "Zadanie": {"locked_visible": True, "locked_panel": True},
                "Notatka": {"locked_visible": False, "locked_panel": False},
                "TAG": {"locked_visible": False, "locked_panel": False},
                "Data realizacji": {"locked_visible": False, "locked_panel": True},
                "KanBan": {"locked_visible": True, "locked_panel": False},
                "Archiwum": {"locked_visible": True, "locked_panel": True}
            }
            
            # Załaduj wszystkie kolumny z bazy danych (standard + niestandardowe)
            try:
                if not hasattr(self, 'db_manager'):
                    print("BŁĄD: db_manager nie istnieje!")
                    all_columns = []
                else:
                    columns_data = self.db_manager.get_task_columns()
                    all_columns = []
                    for col in columns_data:
                        # Sprawdź czy to kolumna standardowa
                        is_standard = col['name'] in standard_column_settings
                        lock_settings = standard_column_settings.get(col['name'], {})
                        
                        all_columns.append({
                            "id": col['id'],
                            "name": col['name'],
                            "type": col['type'],
                            "visible": col['visible'],
                            "in_panel": col['in_panel'],
                            "editable": not is_standard,
                            "default_value": col['default_value'],
                            "dictionary_list_id": col.get('dictionary_list_id'),
                            "locked_visible": lock_settings.get("locked_visible", False),
                            "locked_panel": lock_settings.get("locked_panel", False)
                        })
            except Exception as e:
                print(f"Błąd ładowania kolumn z bazy: {e}")
                import traceback
                traceback.print_exc()
                all_columns = []
            
            # Wypełnij tabelę kolumn
            self.columns_table.setRowCount(len(all_columns))
            
            for row, col in enumerate(all_columns):
                # Nazwa kolumny
                name_item = QTableWidgetItem(col["name"])
                if not col.get("editable", True):
                    name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                # Zapisz ID kolumny jako dane użytkownika (dla wszystkich kolumn)
                if col.get("id"):
                    name_item.setData(Qt.ItemDataRole.UserRole, col["id"])
                self.columns_table.setItem(row, 0, name_item)
                
                # Typ kolumny (tylko do odczytu - wyświetlanie)
                type_item = QTableWidgetItem(col["type"])
                type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.columns_table.setItem(row, 1, type_item)
                
                # Widoczność (ComboBox lub CheckBox dla KanBan)
                if col["name"] == "KanBan":
                    # KanBan używa CheckBox zamiast ComboBox
                    visible_check = QCheckBox()
                    visible_check.setChecked(col["visible"])
                    visible_check.setEnabled(False)  # Zablokowany - zawsze widoczny
                    # Zastosuj czerwone tło dla zablokowanego pola
                    visible_check_palette = visible_check.palette()
                    visible_check_palette.setColor(QPalette.ColorRole.Window, locked_color)
                    visible_check.setPalette(visible_check_palette)
                    visible_check.setAutoFillBackground(True)
                    self.configure_table_widget(visible_check)
                    self.columns_table.setCellWidget(row, 2, visible_check)
                else:
                    visible_combo = QComboBox()
                    visible_combo.addItems(["Tak", "Nie"])
                    visible_combo.setCurrentText("Tak" if col["visible"] else "Nie")
                    # Połącz sygnał zmiany z zapisywaniem
                    visible_combo.currentTextChanged.connect(lambda text, row=row: self.on_column_visibility_changed(row, text))
                    # Zablokuj widoczność dla określonych kolumn
                    if col.get("locked_visible", False):
                        visible_combo.setEnabled(False)
                        # Zastosuj czerwone tło dla zablokowanego pola
                        visible_combo_palette = visible_combo.palette()
                        visible_combo_palette.setColor(QPalette.ColorRole.Base, locked_color)
                        visible_combo_palette.setColor(QPalette.ColorRole.Button, locked_color)
                        visible_combo.setPalette(visible_combo_palette)
                    # Zastosuj stylizację dla widgetów w komórkach
                    self.configure_table_widget(visible_combo)
                    self.columns_table.setCellWidget(row, 2, visible_combo)
                
                # W dolnym pasku (ComboBox)
                panel_combo = QComboBox()
                panel_combo.addItems(["Tak", "Nie"])
                panel_combo.setCurrentText("Tak" if col["in_panel"] else "Nie")
                # Połącz sygnały zmiany
                panel_combo.currentTextChanged.connect(lambda text, row=row: self.on_column_panel_changed(row, text))
                panel_combo.currentTextChanged.connect(self.update_bottom_panel_visibility)
                # Zablokuj panel dla określonych kolumn
                if col.get("locked_panel", False):
                    panel_combo.setEnabled(False)
                    # Zastosuj czerwone tło dla zablokowanego pola
                    panel_combo_palette = panel_combo.palette()
                    panel_combo_palette.setColor(QPalette.ColorRole.Base, locked_color)
                    panel_combo_palette.setColor(QPalette.ColorRole.Button, locked_color)
                    panel_combo.setPalette(panel_combo_palette)
                # Zastosuj stylizację dla widgetów w komórkach
                self.configure_table_widget(panel_combo)
                self.columns_table.setCellWidget(row, 3, panel_combo)
                
                # Wartość domyślna
                default_item = QTableWidgetItem(col.get("default_value", ""))
                # Niedostępne dla niektórych typów
                if col["type"] in ["Data", "Alarm", "Czas trwania", "CheckBox"] or not col.get("editable", True):
                    default_item.setFlags(default_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    default_item.setBackground(alternate_color)
                self.columns_table.setItem(row, 4, default_item)
            
        except Exception as e:
            print(f"Błąd ładowania kolumn: {e}")
    
    def load_task_tags(self):
        """Ładuje kategorie jako tagi zadań z kolorami"""
        try:
            from database.db_manager import Database
            db = Database()
            categories = db.get_categories()
            
            # Wyczyść istniejące tagi
            self.tags_list.clear()
            
            # Dodaj kategorie z bazy danych jako tagi
            for category in categories:
                # category to tuple: (id, name, color, created_at)
                tag_data = {
                    "id": str(category[0]),
                    "name": category[1], 
                    "color": category[2]
                }
                self.add_tag_to_list(tag_data["name"], tag_data["color"], tag_data)
            
            print(f"Załadowano {len(categories)} kategorii jako tagi")
            
        except Exception as e:
            print(f"Błąd ładowania kategorii jako tagów: {e}")
            import traceback
            traceback.print_exc()
    
    def add_tag_to_list(self, name, color, tag_data=None):
        """Dodaje tag do listy z kolorowym stylem"""
        from PyQt6.QtWidgets import QListWidgetItem
        
        item = QListWidgetItem(name)
        
        # Oblicz kolor tekstu na podstawie jasności tła
        color_obj = QColor(color)
        brightness = (color_obj.red() * 299 + 
                     color_obj.green() * 587 + 
                     color_obj.blue() * 114) / 1000
        text_color = "#000000" if brightness > 128 else "#ffffff"
        
        # Ustaw dane tagu (z ID jeśli dostępne)
        if tag_data:
            item.setData(Qt.ItemDataRole.UserRole, tag_data)
        else:
            item.setData(Qt.ItemDataRole.UserRole, {"name": name, "color": color})
        
        # Dodaj do listy
        self.tags_list.addItem(item)
        
        # Zastosuj styl po dodaniu
        self.apply_tag_style(item, color, text_color)
    
    def apply_tag_style(self, item, bg_color, text_color):
        """Stosuje kolorowy styl do elementu tagu"""
        try:
            # Niestety QListWidgetItem nie obsługuje pełnych stylów CSS
            # Użyjemy background color i foreground color
            color_obj = QColor(bg_color)
            text_color_obj = QColor(text_color)
            
            item.setBackground(color_obj)
            item.setForeground(text_color_obj)
            
        except Exception as e:
            print(f"Błąd stosowania stylu tagu: {e}")
    
    def load_task_lists(self):
        """Ładuje listy zadań"""
        try:
            # Załaduj z bazy danych
            dictionary_lists = self.db_manager.get_dictionary_lists(context="table")
            
            self.task_lists_widget.clear()
            for dict_list in dictionary_lists:
                self.task_lists_widget.addItem(dict_list['name'])
                
        except Exception as e:
            print(f"Błąd ładowania list zadań: {e}")
    
    def add_task_tag(self):
        """Dodaje nową kategorię jako tag zadania z kolorem"""
        try:
            from .tag_dialog import TagDialog
            dialog = TagDialog(self, theme_manager=self.theme_manager)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                tag_data = dialog.get_tag_data()
                
                # Zapisz do bazy danych jako kategorię
                from database.db_manager import Database
                db = Database()
                
                # Sprawdź czy mamy metodę add_category w db_manager
                try:
                    # Dodaj jako kategorię
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO categories (name, color) VALUES (?, ?)
                    ''', (tag_data["name"], tag_data["color"]))
                    conn.commit()
                    category_id = cursor.lastrowid
                    conn.close()
                except Exception as e:
                    print(f"Błąd dodawania kategorii: {e}")
                    category_id = None
                
                if category_id:
                    # Dodaj tag do listy z ID
                    tag_data["id"] = str(category_id)  # Konwertuj na string
                    self.add_tag_to_list(tag_data["name"], tag_data["color"], tag_data)
                    print(f"Dodano kategorię jako tag: {tag_data['name']} z kolorem {tag_data['color']}")
                    
                    # Odśwież tagi w widoku zadań
                    self.refresh_tasks_tags()
                else:
                    QMessageBox.warning(self, "Błąd", "Nie udało się dodać kategorii do bazy danych")
                
        except Exception as e:
            print(f"Błąd dodawania kategorii jako tag: {e}")
            QMessageBox.critical(self, "Błąd", f"Błąd dodawania tagu: {e}")
    
    def edit_task_tag(self):
        """Edytuje wybraną kategorię jako tag z kolorem"""
        try:
            current_item = self.tags_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uwaga", "Wybierz tag do edycji")
                return
            
            # Pobierz dane tagu
            tag_data = current_item.data(Qt.ItemDataRole.UserRole)
            if not tag_data:
                # Dla starych tagów bez danych kolorów
                tag_data = {"name": current_item.text(), "color": "#3498db"}
            
            from .tag_dialog import TagDialog
            dialog = TagDialog(self, tag_data=tag_data, theme_manager=self.theme_manager)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_tag_data()
                
                # Zaktualizuj w bazie danych jeśli tag ma ID (kategoria)
                from database.db_manager import Database
                db = Database()
                
                if "id" in tag_data and tag_data["id"]:
                    try:
                        # Aktualizuj kategorię w bazie danych
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE categories SET name = ?, color = ? WHERE id = ?
                        ''', (updated_data["name"], updated_data["color"], int(tag_data["id"])))
                        conn.commit()
                        conn.close()
                        updated_data["id"] = tag_data["id"]  # Zachowaj ID
                    except Exception as e:
                        print(f"Błąd aktualizacji kategorii: {e}")
                
                # Zaktualizuj element na liście
                current_item.setText(updated_data["name"])
                current_item.setData(Qt.ItemDataRole.UserRole, updated_data)
                
                # Oblicz kolor tekstu
                color_obj = QColor(updated_data["color"])
                brightness = (color_obj.red() * 299 + 
                             color_obj.green() * 587 + 
                             color_obj.blue() * 114) / 1000
                text_color = "#000000" if brightness > 128 else "#ffffff"
                
                # Zastosuj nowy styl
                self.apply_tag_style(current_item, updated_data["color"], text_color)
                
                print(f"Zaktualizowano kategorię jako tag: {updated_data['name']} z kolorem {updated_data['color']}")
                
                # Odśwież tagi w widoku zadań
                self.refresh_tasks_tags()
                
        except Exception as e:
            print(f"Błąd edycji kategorii jako tag: {e}")
            QMessageBox.critical(self, "Błąd", f"Błąd edycji tagu: {e}")
    
    def delete_task_tag(self):
        """Usuwa wybraną kategorię jako tag"""
        try:
            current_item = self.tags_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uwaga", "Wybierz tag do usunięcia")
                return
            
            tag_name = current_item.text()
            reply = QMessageBox.question(
                self, 
                "Potwierdź usunięcie",
                f"Czy na pewno chcesz usunąć tag '{tag_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Usuń z bazy danych jeśli tag ma ID (kategoria)
                tag_data = current_item.data(Qt.ItemDataRole.UserRole)
                if tag_data and "id" in tag_data and tag_data["id"]:
                    from database.db_manager import Database
                    db = Database()
                    try:
                        # Usuń kategorię z bazy danych
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM categories WHERE id = ?', (int(tag_data["id"]),))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"Błąd usuwania kategorii: {e}")
                
                # Usuń z listy
                self.tags_list.takeItem(self.tags_list.row(current_item))
                print(f"Usunięto kategorię jako tag: {tag_name}")
                
                # Odśwież tagi w widoku zadań
                self.refresh_tasks_tags()
                
        except Exception as e:
            print(f"Błąd usuwania kategorii jako tag: {e}")
            QMessageBox.critical(self, "Błąd", f"Błąd usuwania tagu: {e}")
    
    def add_task_list(self):
        """Dodaje nową listę zadań"""
        try:
            from .list_dialogs import ListDialog
            dialog = ListDialog(self, theme_manager=self.theme_manager, context="task")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                list_data = dialog.get_list_data()
                
                # Dodaj do interfejsu
                self.task_lists_widget.addItem(list_data['name'])
                
                # TODO: Zapisz do bazy danych z kontekstem "task"
                print(f"Dodano listę zadań: {list_data['name']} (kontekst: {list_data['context']})")
                print(f"Elementy: {list_data['items']}")
                
        except Exception as e:
            print(f"Błąd dodawania listy zadań: {e}")
    
    def edit_task_list(self):
        """Edytuje wybraną listę zadań"""
        try:
            current_item = self.task_lists_widget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uwaga", "Wybierz listę do edycji")
                return
            
            list_name = current_item.text()
            
            # Pobierz dane listy z bazy danych po nazwie
            list_data = self.db.get_dictionary_list_by_name(list_name, context="task")
            
            if not list_data:
                QMessageBox.warning(self, "Błąd", f"Nie znaleziono danych listy '{list_name}' w bazie danych")
                return
            
            from .list_dialogs import ListDialog
            dialog = ListDialog(self, list_data=list_data, theme_manager=self.theme_manager, context="task")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_list_data()
                
                # Aktualizuj interfejs
                current_item.setText(updated_data['name'])
                
                # TODO: Zaktualizuj w bazie danych z kontekstem "task"
                print(f"Zaktualizowano listę zadań: {list_name} -> {updated_data['name']} (kontekst: {updated_data['context']})")
                print(f"Elementy: {updated_data['items']}")
                
        except Exception as e:
            print(f"Błąd edycji listy zadań: {e}")
            QMessageBox.critical(self, "Błąd", f"Błąd podczas edytowania listy zadań: {e}")
    
    def edit_task_list_content(self):
        """Edytuje zawartość wybranej listy zadań"""
        try:
            current_item = self.task_lists_widget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uwaga", "Wybierz listę do edycji zawartości")
                return
            
            list_name = current_item.text()
            
            # Otwórz dialog edycji zawartości listy
            from .task_list_content_dialog import TaskListContentDialog
            dialog = TaskListContentDialog(self, list_name, self.theme_manager)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                content = dialog.get_list_content()
                # TODO: Zapisz zawartość listy do bazy danych
                print(f"Zaktualizowano zawartość listy '{list_name}': {content}")
                
        except Exception as e:
            print(f"Błąd edycji zawartości listy: {e}")
    
    def delete_task_list(self):
        """Usuwa wybraną listę"""
        try:
            current_item = self.task_lists_widget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uwaga", "Wybierz listę do usunięcia")
                return
            
            list_name = current_item.text()
            reply = QMessageBox.question(
                self, 
                "Potwierdź usunięcie",
                f"Czy na pewno chcesz usunąć listę '{list_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.task_lists_widget.takeItem(self.task_lists_widget.row(current_item))
                # TODO: Usuń z bazy danych
                print(f"Usunięto listę: {list_name}")
                
        except Exception as e:
            print(f"Błąd usuwania listy: {e}")
    
    def update_dictionary_lists(self):
        """Aktualizuje listę dostępnych list słownikowych"""
        try:
            # Ta metoda jest już nieużywana w nowym UI
            pass
            
        except Exception as e:
            print(f"Błąd aktualizacji list: {e}")
    
    def on_column_type_changed(self, column_type):
        """Obsługuje zmianę typu kolumny"""
        # Ta metoda jest już nieużywana w nowym UI
        pass
    
    def add_custom_column(self):
        """Dodaje nową kolumnę niestandardową"""
        try:
            # Otwórz dialog dodawania kolumny
            from .column_dialog import ColumnDialog
            dialog = ColumnDialog(self, theme_manager=self.theme_manager, db_manager=self.db_manager)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                column_data = dialog.get_column_data()
                
                # Zapisz kolumnę do bazy danych
                try:
                    dictionary_list_id = None
                    # Jeśli typ to Lista, sprawdź czy istnieje lista słownikowa
                    if column_data['type'] == 'Lista' and column_data.get('dictionary_list'):
                        # Pobierz ID listy słownikowej po nazwie
                        lists = self.db_manager.get_dictionary_lists()
                        for lst in lists:
                            if lst['name'] == column_data['dictionary_list']:
                                dictionary_list_id = lst['id']
                                break
                    
                    self.db_manager.add_task_column(
                        name=column_data['name'],
                        col_type=column_data['type'],
                        visible=column_data.get('visible', True),
                        in_panel=column_data.get('in_panel', False),
                        default_value=column_data.get('default_value', ''),
                        dictionary_list_id=dictionary_list_id
                    )
                    
                    # Odśwież widok kolumn w ustawieniach
                    self.load_task_columns()
                    
                    # Odśwież widok zadań
                    if hasattr(self, 'tasks_view') and self.tasks_view:
                        self.tasks_view.refresh_columns()
                    
                    QMessageBox.information(self, "Sukces", f"Dodano kolumnę: {column_data['name']}")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać kolumny: {e}")
                    print(f"Błąd zapisywania kolumny: {e}")
                
        except Exception as e:
            print(f"Błąd dodawania kolumny: {e}")
    
    def edit_custom_column(self):
        """Edytuje wybraną kolumnę"""
        try:
            current_row = self.columns_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Uwaga", "Wybierz kolumnę do edycji")
                return
            
            name_item = self.columns_table.item(current_row, 0)
            if not name_item:
                return
            
            # Sprawdź czy kolumna jest edytowalna
            if name_item.flags() & Qt.ItemFlag.ItemIsEditable == 0:
                QMessageBox.warning(self, "Uwaga", "Ta kolumna nie może być edytowana")
                return
            
            # Otwórz dialog edycji
            from .column_dialog import ColumnDialog
            
            # Pobierz dane kolumny z tabeli
            type_item = self.columns_table.item(current_row, 1)
            visible_widget = self.columns_table.cellWidget(current_row, 2)
            panel_widget = self.columns_table.cellWidget(current_row, 3)
            default_item = self.columns_table.item(current_row, 4)
            
            col_data = {
                "name": name_item.text(),
                "type": type_item.text() if type_item else "Tekstowa",
                "visible": True,
                "in_panel": False,
                "default_value": default_item.text() if default_item else ""
            }
            
            # Pobierz wartość widoczności
            if isinstance(visible_widget, QComboBox):
                col_data["visible"] = visible_widget.currentText() == "Tak"
            elif isinstance(visible_widget, QCheckBox):
                col_data["visible"] = visible_widget.isChecked()
            
            # Pobierz wartość dolnego paska
            if isinstance(panel_widget, QComboBox):
                col_data["in_panel"] = panel_widget.currentText() == "Tak"
            elif isinstance(panel_widget, QCheckBox):
                col_data["in_panel"] = panel_widget.isChecked()
            
            dialog = ColumnDialog(self, column_data=col_data, theme_manager=self.theme_manager, db_manager=self.db_manager)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_column_data()
                
                # Zaktualizuj kolumnę w bazie danych
                try:
                    # Pobierz ID kolumny z danych użytkownika
                    column_id = name_item.data(Qt.ItemDataRole.UserRole)
                    if column_id:
                        dictionary_list_id = None
                        # Jeśli typ to Lista, sprawdź czy istnieje lista słownikowa
                        if updated_data['type'] == 'Lista' and updated_data.get('dictionary_list'):
                            lists = self.db_manager.get_dictionary_lists()
                            for lst in lists:
                                if lst['name'] == updated_data['dictionary_list']:
                                    dictionary_list_id = lst['id']
                                    break
                        
                        self.db_manager.update_task_column(
                            column_id=column_id,
                            name=updated_data['name'],
                            col_type=updated_data['type'],
                            visible=updated_data.get('visible', True),
                            in_panel=updated_data.get('in_panel', False),
                            default_value=updated_data.get('default_value', ''),
                            dictionary_list_id=dictionary_list_id
                        )
                        
                        # Odśwież widok kolumn w ustawieniach
                        self.load_task_columns()
                        
                        # Odśwież widok zadań
                        if hasattr(self, 'tasks_view') and self.tasks_view:
                            self.tasks_view.refresh_columns()
                        
                        QMessageBox.information(self, "Sukces", f"Zaktualizowano kolumnę: {updated_data['name']}")
                    else:
                        QMessageBox.warning(self, "Błąd", "Nie można edytować kolumny systemowej")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Błąd", f"Nie udało się zaktualizować kolumny: {e}")
                    print(f"Błąd aktualizacji kolumny: {e}")
                
        except Exception as e:
            print(f"Błąd edycji kolumny: {e}")
    
    def delete_custom_column(self):
        """Usuwa wybraną kolumnę"""
        try:
            current_row = self.columns_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Uwaga", "Wybierz kolumnę do usunięcia")
                return
            
            name_item = self.columns_table.item(current_row, 0)
            if not name_item:
                return
            
            # Sprawdź czy kolumna jest edytowalna
            if name_item.flags() & Qt.ItemFlag.ItemIsEditable == 0:
                QMessageBox.warning(self, "Uwaga", "Ta kolumna nie może być usunięta")
                return
            
            column_name = name_item.text()
            
            # Potwierdź usunięcie
            reply = QMessageBox.question(
                self, 
                "Potwierdź usunięcie",
                f"Czy na pewno chcesz usunąć kolumnę '{column_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Usuń kolumnę z bazy danych
                try:
                    # Pobierz ID kolumny z danych użytkownika
                    column_id = name_item.data(Qt.ItemDataRole.UserRole)
                    if column_id:
                        if self.db_manager.delete_task_column(column_id):
                            # Odśwież widok kolumn w ustawieniach
                            self.load_task_columns()
                            
                            # Odśwież widok zadań
                            if hasattr(self, 'tasks_view') and self.tasks_view:
                                self.tasks_view.refresh_columns()
                            
                            QMessageBox.information(self, "Sukces", f"Usunięto kolumnę: {column_name}")
                        else:
                            QMessageBox.warning(self, "Błąd", "Nie udało się usunąć kolumny")
                    else:
                        QMessageBox.warning(self, "Błąd", "Nie można usunąć kolumny systemowej")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć kolumny: {e}")
                    print(f"Błąd usuwania kolumny: {e}")
                
        except Exception as e:
            print(f"Błąd usuwania kolumny: {e}")
    
    def save_column_changes(self):
        """Zapisuje zmiany w konfiguracji kolumny"""
        try:
            # Ta metoda jest już nieużywana w nowym UI - zmiany są automatyczne
            QMessageBox.information(self, "Informacja", "Zmiany są zapisywane automatycznie")
            
        except Exception as e:
            print(f"Błąd zapisywania zmian: {e}")
    
    def reset_column_form(self):
        """Resetuje formularz konfiguracji kolumny"""
        # Ta metoda jest już nieużywana w nowym UI
        pass
    
    def move_column_up(self):
        """Przesuwa wybraną kolumnę w górę"""
        try:
            current_row = self.columns_table.currentRow()
            if current_row <= 0:
                QMessageBox.warning(self, "Uwaga", "Nie można przesunąć tej kolumny w górę")
                return
            
            # Pobierz ID kolumn
            current_item = self.columns_table.item(current_row, 0)
            prev_item = self.columns_table.item(current_row - 1, 0)
            
            if not current_item or not prev_item:
                return
            
            current_id = current_item.data(Qt.ItemDataRole.UserRole)
            prev_id = prev_item.data(Qt.ItemDataRole.UserRole)
            
            # Sprawdź czy obie kolumny mają ID (mogą być przesuwane)
            if not current_id or not prev_id:
                QMessageBox.warning(self, "Uwaga", "Nie można przesunąć kolumn bez ID")
                return
            
            # Zamień kolejność w bazie danych
            self.swap_column_order(current_id, prev_id)
            # Odśwież tabelę
            self.load_task_columns()
            # Zaznacz przesunięty wiersz
            self.columns_table.setCurrentCell(current_row - 1, 0)
            # Odśwież widok zadań
            if hasattr(self, 'tasks_view') and self.tasks_view:
                self.tasks_view.refresh_columns()
                    
        except Exception as e:
            print(f"Błąd przesuwania kolumny w górę: {e}")
            import traceback
            traceback.print_exc()
            import traceback
            traceback.print_exc()
    
    def move_column_down(self):
        """Przesuwa wybraną kolumnę w dół"""
        try:
            current_row = self.columns_table.currentRow()
            if current_row < 0 or current_row >= self.columns_table.rowCount() - 1:
                QMessageBox.warning(self, "Uwaga", "Nie można przesunąć tej kolumny w dół")
                return
            
            # Pobierz ID kolumn
            current_item = self.columns_table.item(current_row, 0)
            next_item = self.columns_table.item(current_row + 1, 0)
            
            if not current_item or not next_item:
                return
            
            current_id = current_item.data(Qt.ItemDataRole.UserRole)
            next_id = next_item.data(Qt.ItemDataRole.UserRole)
            
            # Sprawdź czy obie kolumny mają ID (mogą być przesuwane)
            if not current_id or not next_id:
                QMessageBox.warning(self, "Uwaga", "Nie można przesunąć kolumn bez ID")
                return
            
            # Zamień kolejność w bazie danych
            self.swap_column_order(current_id, next_id)
            # Odśwież tabelę
            self.load_task_columns()
            # Zaznacz przesunięty wiersz
            self.columns_table.setCurrentCell(current_row + 1, 0)
            # Odśwież widok zadań
            if hasattr(self, 'tasks_view') and self.tasks_view:
                self.tasks_view.refresh_columns()
                    
        except Exception as e:
            print(f"Błąd przesuwania kolumny w dół: {e}")
            import traceback
            traceback.print_exc()
            traceback.print_exc()
    
    def swap_column_order(self, id1, id2):
        """Zamienia kolejność dwóch kolumn w bazie danych"""
        try:
            # Pobierz informacje o kolumnach
            all_columns = self.db_manager.get_task_columns()
            col1 = next((c for c in all_columns if c['id'] == id1), None)
            col2 = next((c for c in all_columns if c['id'] == id2), None)
            
            if col1 and col2:
                # Zamień wartości column_order
                order1 = col1['column_order']
                order2 = col2['column_order']
                
                self.db_manager.update_task_column(id1, column_order=order2)
                self.db_manager.update_task_column(id2, column_order=order1)
                
        except Exception as e:
            print(f"Błąd zamiany kolejności kolumn: {e}")
            import traceback
            traceback.print_exc()
    
    def on_column_visibility_changed(self, row, text):
        """Obsługuje zmianę widoczności kolumny"""
        try:
            name_item = self.columns_table.item(row, 0)
            if name_item:
                column_id = name_item.data(Qt.ItemDataRole.UserRole)
                if column_id:  # Dla wszystkich kolumn z ID (standardowe + niestandardowe)
                    visible = (text == "Tak")
                    self.db_manager.update_task_column(column_id, visible=visible)
                    print(f"DEBUG: Zaktualizowano widoczność kolumny ID={column_id} na {visible}")
                    # Odśwież widok zadań
                    if hasattr(self, 'tasks_view') and self.tasks_view:
                        self.tasks_view.refresh_columns()
                else:
                    print(f"DEBUG: Brak ID dla kolumny w wierszu {row}")
        except Exception as e:
            print(f"Błąd zmiany widoczności: {e}")
            import traceback
            traceback.print_exc()
    
    def on_column_panel_changed(self, row, text):
        """Obsługuje zmianę ustawienia dolnego panelu kolumny"""
        try:
            name_item = self.columns_table.item(row, 0)
            if name_item:
                column_id = name_item.data(Qt.ItemDataRole.UserRole)
                if column_id:  # Tylko dla kolumn niestandardowych
                    in_panel = (text == "Tak")
                    self.db_manager.update_task_column(column_id, in_panel=in_panel)
        except Exception as e:
            print(f"Błąd zmiany ustawienia panelu: {e}")
    
    def update_bottom_panel_visibility(self):
        """Aktualizuje widoczność elementów w dolnym pasku na podstawie ustawień"""
        try:
            # Mapowanie nazw kolumn na elementy UI
            column_elements = {
                'Kategoria': [self.category_label, self.category_combo],
                'Priorytet': [self.priority_label, self.priority_combo],
                'Termin': [self.datetime_label, self.datetime_edit]
            }
            
            # Znajdź kolumny oznaczone do dolnego paska
            visible_columns = []
            if hasattr(self, 'columns_table'):
                for row in range(self.columns_table.rowCount()):
                    name_item = self.columns_table.item(row, 0)
                    panel_widget = self.columns_table.cellWidget(row, 3)
                    if name_item and panel_widget:
                        column_name = name_item.text()
                        # Sprawdź czy to ComboBox czy CheckBox
                        is_visible = False
                        if isinstance(panel_widget, QComboBox):
                            is_visible = panel_widget.currentText() == "Tak"
                        elif isinstance(panel_widget, QCheckBox):
                            is_visible = panel_widget.isChecked()
                        
                        if is_visible and column_name in column_elements:
                            visible_columns.append(column_name)
            else:
                # Domyślnie pokaż wszystkie kolumny
                visible_columns = ['Kategoria', 'Priorytet', 'Termin']
            
            # Aktualizuj widoczność elementów
            separator_count = 0
            for column_name, elements in column_elements.items():
                is_visible = column_name in visible_columns
                for element in elements:
                    element.setVisible(is_visible)
                
                # Pokaż separator tylko między widocznymi elementami
                if is_visible and separator_count < 2:
                    if separator_count == 0 and hasattr(self, 'separator1'):
                        self.separator1.setVisible(len(visible_columns) > 1)
                    elif separator_count == 1 and hasattr(self, 'separator2'):
                        self.separator2.setVisible(len(visible_columns) > 2)
                    separator_count += 1
            
            # Ukryj separatory jeśli nie są potrzebne
            if hasattr(self, 'separator1'):
                self.separator1.setVisible(len(visible_columns) > 1)
            if hasattr(self, 'separator2'):
                self.separator2.setVisible(len(visible_columns) > 2)
                
        except Exception as e:
            print(f"Błąd aktualizacji widoczności dolnego paska: {e}")

def main():
    app = QApplication(sys.argv)
    
    # Ustaw styl aplikacji
    app.setStyle('Fusion')
    
    window = TaskManagerApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()