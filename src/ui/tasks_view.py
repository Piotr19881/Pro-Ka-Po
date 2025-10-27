from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
                            QCheckBox, QLineEdit, QDateEdit, QComboBox, QHeaderView,
                            QMenu, QDialog, QDialogButtonBox, QFormLayout, QSpinBox,
                            QMessageBox, QApplication, QAbstractItemView, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QColor, QAction, QBrush
from .theme_manager import ThemeManager
from .column_delegate import ColumnDelegate
import datetime

class TasksView(QWidget):
    """Zaawansowany widok zarządzania zadaniami"""
    
    # Sygnały
    task_created = pyqtSignal(dict)
    task_updated = pyqtSignal(int, dict)  # task_id, task_data
    task_deleted = pyqtSignal(int)
    
    def __init__(self, db_manager, theme_manager=None):
        super().__init__()
        self.db_manager = db_manager
        self.theme_manager = theme_manager or ThemeManager()
        self.current_tasks = []
        self.custom_columns = []
        self.visible_columns = []  # Kolumny widoczne w tabeli
        self.tag_color_map = {}
        self.category_color_map = {}
        self._row_task_ids = []
        self._suspend_item_updates = False
        self.setup_ui()
        self.load_tasks()
        
        # Załaduj tagi z ustawień po utworzeniu wszystkich komponentów
        self.update_tags_from_settings()
    
    def refresh_columns(self):
        """Odświeża konfigurację kolumn z bazy danych i przebudowuje tabelę"""
        try:
            # Przeładuj kolumny
            self.setup_table_columns()
            self.configure_table_header()
            # Odśwież dane w tabeli
            self.populate_table()
        except Exception as e:
            print(f"Błąd odświeżania kolumn: {e}")
            import traceback
            traceback.print_exc()
        
    def apply_theme(self):
        """Stosuje aktualny motyw do widoku"""
        self.setStyleSheet(self.theme_manager.get_main_widget_style())
        
        # Aktualizuj style kontrolek
        if hasattr(self, 'status_filter'):
            self.status_filter.setStyleSheet(self.theme_manager.get_combo_style())
        if hasattr(self, 'tag_filter'):
            self.tag_filter.setStyleSheet(self.theme_manager.get_combo_style())
        if hasattr(self, 'search_input'):
            self.search_input.setStyleSheet(self.theme_manager.get_line_edit_style())
        if hasattr(self, 'tasks_table'):
            self.tasks_table.setStyleSheet(self.theme_manager.get_table_style())
        if hasattr(self, 'controls_widget'):
            self.controls_widget.setStyleSheet(self.theme_manager.get_controls_widget_style())
        if hasattr(self, 'table_container'):
            self.table_container.setStyleSheet(self.theme_manager.get_controls_widget_style())
            
        # Odśwież tabelę żeby zastosować nowe style
        if hasattr(self, 'current_tasks'):
            self.populate_table()
        
    def setup_ui(self):
        """Tworzy interfejs użytkownika"""
        # Podstawowy styl
        self.setStyleSheet(self.theme_manager.get_main_widget_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # === FILTRY I KONTROLKI ===
        self.create_controls_section(layout)
        
        # === TABELA ZADAŃ ===
        self.create_tasks_table(layout)
        
        # Ustaw proporcje: kontrolki zajmują minimalną przestrzeń, tabela resztę
        layout.setStretch(0, 0)  # Kontrolki - minimalna przestrzeń
        layout.setStretch(1, 1)  # Tabela - cała pozostała przestrzeń
        
        # Zastosuj pełny motyw po utworzeniu wszystkich elementów
        self.apply_theme()
        
    def create_controls_section(self, parent_layout):
        """Tworzy sekcję kontrolek i filtrów"""
        controls_widget = QWidget()
        controls_widget.setStyleSheet(self.theme_manager.get_controls_widget_style())
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(15, 10, 15, 10)

        # Filtry statusu
        status_label = QLabel("Status:")
        status_label.setStyleSheet(self.theme_manager.get_label_style(bold=True))
        controls_layout.addWidget(status_label)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Wszystkie", "Aktywne", "Zakończone", "Zarchiwizowane"])
        self.status_filter.setStyleSheet(self.theme_manager.get_combo_style())
        self.status_filter.currentTextChanged.connect(self.filter_tasks)
        controls_layout.addWidget(self.status_filter)

        controls_layout.addSpacing(20)

        # Filtr TAG
        tag_label = QLabel("TAG:")
        tag_label.setStyleSheet(self.theme_manager.get_label_style(bold=True))
        controls_layout.addWidget(tag_label)

        self.tag_filter = QComboBox()
        self.tag_filter.addItem("Wszystkie")
        self.tag_filter.setStyleSheet(self.theme_manager.get_combo_style())
        self.tag_filter.currentTextChanged.connect(self.filter_tasks)
        controls_layout.addWidget(self.tag_filter)

        controls_layout.addSpacing(20)

        # Wyszukiwanie
        search_label = QLabel("Szukaj:")
        search_label.setStyleSheet(self.theme_manager.get_label_style(bold=True))
        controls_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Wpisz tekst do wyszukania...")
        self.search_input.setStyleSheet(self.theme_manager.get_line_edit_style())
        self.search_input.textChanged.connect(self.filter_tasks)
        controls_layout.addWidget(self.search_input)

        controls_layout.addStretch()
        parent_layout.addWidget(controls_widget)
        self.controls_widget = controls_widget

    def create_tasks_table(self, parent_layout):
        """Tworzy tabelę zadań"""
        table_widget = QWidget()
        table_widget.setStyleSheet(self.theme_manager.get_controls_widget_style())
        table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(15, 15, 15, 15)

        # Tabela
        self.tasks_table = QTableWidget()
        self.setup_table_columns()

        # Stylizacja tabeli
        self.tasks_table.setStyleSheet(self.theme_manager.get_table_style())

        # Ustawienia tabeli
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tasks_table.verticalHeader().setVisible(False)
        
        # Ustaw triggery edycji - pojedyncze kliknięcie lub double click
        self.tasks_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked | 
            QAbstractItemView.EditTrigger.SelectedClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )

        # Ustaw politykę rozmiaru dla tabeli aby wypełniała dostępną przestrzeń
        self.tasks_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Menu kontekstowe
        self.tasks_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tasks_table.customContextMenuRequested.connect(self.show_context_menu)

        # Reaguj na zmiany w komórkach (np. wybór nowego tagu)
        self.tasks_table.itemChanged.connect(self.on_task_item_changed)

        table_layout.addWidget(self.tasks_table)
        parent_layout.addWidget(table_widget)
        self.table_container = table_widget
        
    def setup_table_columns(self):
        """Konfiguruje kolumny tabeli na podstawie ustawień z bazy danych"""
        try:
            # Pobierz WSZYSTKIE kolumny z bazy danych (standardowe + niestandardowe)
            all_columns_from_db = self.db_manager.get_task_columns()
            
            # Konwertuj na format używany przez tasks_view
            all_columns = []
            for col in all_columns_from_db:
                # Ustaw domyślne szerokości dla różnych typów kolumn
                if col["name"] == "ID":
                    width = 50
                    resize_mode = "Fixed"
                elif col["name"] == "Data dodania" or col["name"] == "Data realizacji":
                    width = 110
                    resize_mode = "Fixed"
                elif col["name"] == "Status" or col["name"] == "KanBan" or col["name"] == "Archiwum":
                    width = 60
                    resize_mode = "Fixed"
                elif col["name"] == "Zadanie":
                    width = 200
                    resize_mode = "Stretch"
                elif col["name"] == "Notatka":
                    width = 70
                    resize_mode = "Fixed"
                elif col["name"] == "TAG":
                    width = 80
                    resize_mode = "Interactive"
                else:
                    width = 100  # Domyślna szerokość dla kolumn niestandardowych
                    resize_mode = "Interactive"
                
                all_columns.append({
                    "name": col["name"],
                    "type": col["type"],
                    "visible": col["visible"],
                    "in_panel": col["in_panel"],
                    "width": width,
                    "resize_mode": resize_mode,
                    "dictionary_list_id": col.get("dictionary_list_id")
                })
            
            # Filtruj tylko widoczne kolumny
            self.visible_columns = [col for col in all_columns if col["visible"]]
            
            # Oddziel kolumny niestandardowe (nie są to kolumny standardowe)
            standard_column_names = ["ID", "Data dodania", "Status", "Zadanie", "Notatka", "TAG", "Data realizacji", "KanBan", "Archiwum"]
            self.custom_columns = [col for col in all_columns if col["name"] not in standard_column_names]
            
            print(f"DEBUG: Załadowano {len(all_columns)} kolumn z bazy, {len(self.visible_columns)} widocznych, {len(self.custom_columns)} niestandardowych")
            
            # Ustaw liczę kolumn i nagłówki
            column_names = [col["name"] for col in self.visible_columns]
            self.tasks_table.setColumnCount(len(column_names))
            self.tasks_table.setHorizontalHeaderLabels(column_names)
            
            # Utwórz i skonfiguruj delegata dla kolumn
            self.column_delegate = ColumnDelegate(
                parent=self.tasks_table,
                db_manager=self.db_manager,
                theme_manager=self.theme_manager
            )
            
            # Ustaw typy kolumn w delegacie
            for col in self.visible_columns:
                self.column_delegate.set_column_type(
                    col["name"], 
                    col["type"],
                    col.get("dictionary_list_id")
                )
            
            # Przypisz delegata do tabeli
            self.tasks_table.setItemDelegate(self.column_delegate)
            
        except Exception as e:
            print(f"Błąd konfiguracji kolumn: {e}")
            import traceback
            traceback.print_exc()
            # Fallback do kolumn standardowych
            self.visible_columns = [
                {"name": "ID", "type": "Liczbowa", "visible": True, "width": 50, "resize_mode": "Fixed"},
                {"name": "Data dodania", "type": "Data", "visible": True, "width": 110, "resize_mode": "Fixed"},
                {"name": "Status", "type": "CheckBox", "visible": True, "width": 60, "resize_mode": "Fixed"},
                {"name": "Zadanie", "type": "Tekstowa", "visible": True, "width": 200, "resize_mode": "Stretch"},
                {"name": "Notatka", "type": "Tekstowa", "visible": True, "width": 70, "resize_mode": "Fixed"},
                {"name": "TAG", "type": "Lista", "visible": True, "width": 80, "resize_mode": "Interactive"},
                {"name": "Data realizacji", "type": "Data", "visible": False, "width": 110, "resize_mode": "Fixed"},
                {"name": "KanBan", "type": "CheckBox", "visible": True, "width": 60, "resize_mode": "Fixed"},
                {"name": "Archiwum", "type": "CheckBox", "visible": False, "width": 60, "resize_mode": "Fixed"}
            ]
            column_names = [col["name"] for col in self.visible_columns if col["visible"]]
            self.tasks_table.setColumnCount(len(column_names))
            self.tasks_table.setHorizontalHeaderLabels(column_names)
        
    def configure_table_header(self):
        """Konfiguruje header tabeli z odpowiednimi szerokościami i trybami kolumn na podstawie ustawień"""
        try:
            header = self.tasks_table.horizontalHeader()
            if header is None:
                return
            
            header.setStretchLastSection(False)  # Nie rozciągaj ostatniej kolumny automatycznie
            
            # Konfiguruj każdą kolumnę zgodnie z ustawieniami
            for col_index, col_config in enumerate(self.visible_columns):
                # Ustaw szerokość
                width = col_config.get("width", 100)
                header.resizeSection(col_index, width)
                
                # Ustaw tryb rozmiaru
                resize_mode_str = col_config.get("resize_mode", "Interactive")
                if resize_mode_str == "Fixed":
                    resize_mode = QHeaderView.ResizeMode.Fixed
                elif resize_mode_str == "Stretch":
                    resize_mode = QHeaderView.ResizeMode.Stretch
                else:  # Interactive
                    resize_mode = QHeaderView.ResizeMode.Interactive
                
                header.setSectionResizeMode(col_index, resize_mode)
            
        except Exception as e:
            print(f"Błąd konfiguracji header: {e}")
            import traceback
            traceback.print_exc()
        
    def load_tasks(self):
        """Ładuje zadania z bazy danych"""
        try:
            # Pobierz zadania z bazy danych
            tasks = self.db_manager.get_tasks()
            
            # Pobierz kolory tagów z dedykowanej tabeli oraz kategorii
            tag_colors = {}
            try:
                tag_rows = self.db_manager.get_task_tags()
                for tag_row in tag_rows:
                    tag_name = tag_row[1]
                    tag_color = tag_row[2]
                    if tag_name and tag_color:
                        tag_colors[tag_name] = tag_color
            except Exception as e:
                print(f"Błąd pobierania tagów: {e}")

            categories = self.db_manager.get_categories()
            category_colors = {cat[1]: cat[2] for cat in categories if cat[1] and cat[2]}
            self.category_color_map = category_colors.copy()
            # Kolory z tagów mają priorytet nad kategoriami
            combined_colors = {**category_colors, **tag_colors}
            
            # Konwertuj zadania do odpowiedniego formatu z kolorami tagów
            self.current_tasks = []
            for task in tasks:
                task_dict = {
                    'id': task[0],
                    'date_added': task[7],  # created_at
                    'status': task[3] == 'completed',  # status
                    'task': task[1],  # title
                    'note_id': task[9],  # note_id
                    'tag': task[5],  # category (używane jako tag)
                    'date_completed': task[8] if task[3] == 'completed' else None,  # updated_at jeśli completed
                    'kanban_status': 'DONE' if task[3] == 'completed' else 'TODO',
                    'archived': task[11] == 1 if len(task) > 11 else False,  # flaga archived
                    'kanban': task[10] if len(task) > 10 else 0  # flaga kanban
                }
                
                # Parsuj description aby wyciągnąć wartości kolumn użytkownika
                description = task[2]  # description
                if description:
                    # Pobierz wszystkie kolumny użytkownika
                    all_columns = self.db_manager.get_task_columns()
                    standard_columns = {'ID', 'Data dodania', 'Status', 'Zadanie', 'Notatka', 
                                       'Data realizacji', 'KanBan', 'Archiwum', 'TAG'}
                    
                    # Wyciągnij wartości dla wszystkich kolumn użytkownika z description
                    for line in description.split('\n'):
                        if ':' in line:
                            # Sprawdź czy linia zaczyna się od nazwy kolumny użytkownika
                            for col in all_columns:
                                col_name = col['name']
                                if col_name not in standard_columns and line.startswith(f'{col_name}:'):
                                    value = line.replace(f'{col_name}:', '').strip()
                                    task_dict[col_name] = value
                                    break
                
                # Dodaj kolor kategorii jako kolor tagu
                tag_name = task_dict.get('tag')
                if tag_name:
                    color_hex = combined_colors.get(tag_name)
                    task_dict['tag_color'] = color_hex or '#3498db'
                else:
                    task_dict['tag_color'] = None
                
                self.current_tasks.append(task_dict)
            
            self.populate_table()
            # Skonfiguruj header po załadowaniu danych
            self.configure_table_header()
            # Zastosuj kolorowanie komórek po wszystkich konfiguracjach
            self.apply_cell_coloring()
        except Exception as e:
            print(f"Błąd ładowania zadań: {e}")
            import traceback
            traceback.print_exc()
            
    def get_sample_tasks(self):
        """Zwraca przykładowe zadania (tymczasowo)"""
        return [
            {
                'id': 1,
                'date_added': datetime.datetime.now(),
                'status': False,
                'task': 'Zakończ projekt aplikacji',
                'note_id': None,
                'tag': 'Programowanie',
                'date_completed': None,
                'kanban_status': 'TODO',
                'archived': False
            },
            {
                'id': 2,
                'date_added': datetime.datetime.now() - datetime.timedelta(days=1),
                'status': True,
                'task': 'Przygotuj prezentację',
                'note_id': None,
                'tag': 'Praca',
                'date_completed': datetime.datetime.now(),
                'kanban_status': 'DONE',
                'archived': False
            }
        ]
        
    def get_column_index(self, column_name):
        """Zwraca indeks kolumny po nazwie lub None jeśli kolumna nie jest widoczna"""
        for index, col in enumerate(self.visible_columns):
            if col["name"] == column_name:
                return index
        return None
    
    def populate_table(self):
        """Wypełnia tabelę zadaniami"""
        filtered_tasks = self.filter_tasks_data()
        self._row_task_ids = [task['id'] for task in filtered_tasks]

        self._suspend_item_updates = True
        try:
            self.tasks_table.setRowCount(len(filtered_tasks))

            for row, task in enumerate(filtered_tasks):
                # ID
                id_col = self.get_column_index("ID")
                if id_col is not None:
                    id_item = QTableWidgetItem(str(task['id']))
                    id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tasks_table.setItem(row, id_col, id_item)

                # Data dodania
                date_added_col = self.get_column_index("Data dodania")
                if date_added_col is not None:
                    date_value = task.get('date_added') or task.get('created_at')
                    if date_value:
                        if isinstance(date_value, str):
                            date_str = date_value
                        else:
                            date_str = date_value.strftime("%d.%m.%Y %H:%M")
                    else:
                        date_str = ""
                    date_item = QTableWidgetItem(date_str)
                    date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tasks_table.setItem(row, date_added_col, date_item)

                # Status (checkbox)
                status_col = self.get_column_index("Status")
                if status_col is not None:
                    status_widget = QCheckBox()
                    status_widget.setChecked(task['status'])

                    if task['status']:
                        status_color = "background-color: rgba(46, 204, 113, 0.3);"
                    else:
                        status_color = "background-color: rgba(231, 76, 60, 0.3);"

                    checkbox_style = self.theme_manager.get_checkbox_style() + status_color
                    status_widget.setStyleSheet(checkbox_style)
                    status_widget.stateChanged.connect(lambda state, task_id=task['id']: self.toggle_task_status(task_id, state))
                    self.tasks_table.setCellWidget(row, status_col, status_widget)

                # Zadanie
                task_col = self.get_column_index("Zadanie")
                if task_col is not None:
                    task_item = QTableWidgetItem(task['task'])
                    self.tasks_table.setItem(row, task_col, task_item)

                # Notatka
                note_col = self.get_column_index("Notatka")
                if note_col is not None:
                    note_btn = QPushButton("📝" if task['note_id'] else "➕")
                    note_btn.setStyleSheet(self.theme_manager.get_button_style())
                    note_btn.clicked.connect(lambda checked, task_id=task['id']: self.open_task_note(task_id))
                    self.tasks_table.setCellWidget(row, note_col, note_btn)

                # TAG
                tag_col = self.get_column_index("TAG")
                if tag_col is not None:
                    tag_value = task.get('tag') or ""
                    tag_item = QTableWidgetItem(tag_value)

                    tag_color_hex = task.get('tag_color') if tag_value else None
                    tag_item.setData(Qt.ItemDataRole.UserRole + 1, tag_color_hex)

                    if tag_color_hex:
                        base_color = QColor(tag_color_hex)
                        tag_brush = QBrush(base_color)
                        tag_item.setBackground(tag_brush)
                        tag_item.setData(Qt.ItemDataRole.BackgroundRole, tag_brush)

                        brightness = (base_color.red() * 299 + base_color.green() * 587 + base_color.blue() * 114) / 1000
                        text_color = QColor("#000000") if brightness > 160 else QColor("#ffffff")
                        tag_item.setForeground(text_color)
                    else:
                        default_text = self.theme_manager.get_current_colors().get('text_color', '#2c3e50')
                        tag_item.setForeground(QColor(default_text))
                        tag_item.setData(Qt.ItemDataRole.BackgroundRole, None)

                    self.tasks_table.setItem(row, tag_col, tag_item)

                # Data realizacji
                completion_col = self.get_column_index("Data realizacji")
                if completion_col is not None:
                    date_completed = task.get('date_completed')
                    if date_completed:
                        if isinstance(date_completed, str):
                            completion_date = date_completed
                        else:
                            completion_date = date_completed.strftime("%d.%m.%Y %H:%M")
                    else:
                        completion_date = ""
                    completion_item = QTableWidgetItem(completion_date)
                    completion_item.setFlags(completion_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tasks_table.setItem(row, completion_col, completion_item)

                # KanBan
                kanban_col = self.get_column_index("KanBan")
                if kanban_col is not None:
                    # Sprawdź czy zadanie jest już w KanBan
                    is_in_kanban = task.get('kanban', 0) == 1
                    kanban_btn = QPushButton("✓ 📊" if is_in_kanban else "📊")
                    kanban_btn.setStyleSheet(self.theme_manager.get_button_style())
                    kanban_btn.clicked.connect(lambda checked, task_id=task['id'], in_kanban=is_in_kanban: self.toggle_kanban(task_id, in_kanban))
                    self.tasks_table.setCellWidget(row, kanban_col, kanban_btn)

                # Archiwum (checkbox)
                archive_col = self.get_column_index("Archiwum")
                if archive_col is not None:
                    archive_widget = QCheckBox()
                    archive_widget.setChecked(task.get('archived', False))
                    archive_widget.setStyleSheet(self.theme_manager.get_checkbox_style())
                    archive_widget.stateChanged.connect(lambda state, task_id=task['id']: self.toggle_task_archive(task_id, state))
                    self.tasks_table.setCellWidget(row, archive_col, archive_widget)

                # Ustaw kolor tła dla całego wiersza
                self.set_row_background_color(row, task.get('tag_color'))

                # Kolumny niestandardowe
                for col in self.custom_columns:
                    col_index = self.get_column_index(col["name"])
                    if col_index is not None:
                        value = task.get(col["name"], "")

                        if col["type"] == "CheckBox":
                            checkbox_widget = QCheckBox()
                            checkbox_widget.setChecked(bool(value))
                            checkbox_widget.setStyleSheet(self.theme_manager.get_checkbox_style())
                            self.tasks_table.setCellWidget(row, col_index, checkbox_widget)
                        else:
                            item = QTableWidgetItem(str(value) if value else "")
                            self.tasks_table.setItem(row, col_index, item)
        finally:
            self._suspend_item_updates = False

        # Po wypełnieniu tabeli ponownie zastosuj kolorowanie komórek TAG
        self.apply_cell_coloring()

    def set_row_background_color(self, row, color_hex):
        """Ustawia (lub czyści) kolor tła wiersza na podstawie tagu"""
        try:
            status_col_index = self.get_column_index("Status")
            tag_col_index = self.get_column_index("TAG")

            if not color_hex:
                # Usuń niestandardowe kolory tła
                for col in range(self.tasks_table.columnCount()):
                    if col == status_col_index or col == tag_col_index:
                        continue

                    item = self.tasks_table.item(row, col)
                    if item:
                        item.setBackground(QBrush())
                        item.setData(Qt.ItemDataRole.BackgroundRole, None)
                    else:
                        widget = self.tasks_table.cellWidget(row, col)
                        if widget:
                            import re
                            current_style = widget.styleSheet()
                            current_style = re.sub(r'background-color:[^;]*;?', '', current_style)
                            widget.setStyleSheet(current_style)
                return

            color = QColor(color_hex)
            rgba_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, 0.15)"

            for col in range(self.tasks_table.columnCount()):
                if col == status_col_index or col == tag_col_index:
                    continue

                item = self.tasks_table.item(row, col)
                if item:
                    bg_color = QColor(color_hex)
                    bg_color.setAlpha(40)
                    item.setBackground(bg_color)
                    item.setData(Qt.ItemDataRole.BackgroundRole, bg_color)
                else:
                    widget = self.tasks_table.cellWidget(row, col)
                    if widget:
                        import re
                        current_style = widget.styleSheet()
                        current_style = re.sub(r'background-color:[^;]*;?', '', current_style)
                        widget.setStyleSheet(f"{current_style}; background-color: {rgba_color};")
        except Exception as e:
            print(f"Błąd ustawiania koloru tła wiersza {row}: {e}")
            import traceback
            traceback.print_exc()
    
    def get_color_for_tag(self, tag_name):
        """Zwraca kolor HEX przypisany do tagu lub fallback"""
        if not tag_name:
            return None

        color = self.tag_color_map.get(tag_name)
        if color:
            return color

        color = self.category_color_map.get(tag_name)
        if color:
            return color

        return "#3498db"

    def on_task_item_changed(self, item):
        """Reaguje na zmianę wartości komórki (np. zmiana TAGu)"""
        if self._suspend_item_updates:
            return

        row = item.row()
        col = item.column()

        if row >= len(self._row_task_ids):
            return

        if col >= len(self.visible_columns):
            return

        column_name = self.visible_columns[col]["name"]
        if column_name != "TAG":
            return

        task_id = self._row_task_ids[row]
        tag_value = (item.text() or "").strip()
        color_hex = self.get_color_for_tag(tag_value) if tag_value else None

        default_text = self.theme_manager.get_current_colors().get('text_color', '#2c3e50')

        self._suspend_item_updates = True
        try:
            if color_hex:
                color = QColor(color_hex)
                brush = QBrush(color)
                item.setData(Qt.ItemDataRole.BackgroundRole, brush)
                item.setBackground(brush)

                brightness = (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000
                text_color = QColor("#000000") if brightness > 160 else QColor("#ffffff")
                item.setForeground(text_color)
                self.set_row_background_color(row, color_hex)
            else:
                item.setData(Qt.ItemDataRole.BackgroundRole, None)
                item.setBackground(QBrush())
                item.setForeground(QColor(default_text))
                self.set_row_background_color(row, None)
        finally:
            self._suspend_item_updates = False

        # Zaktualizuj lokalne dane zadania
        for task in self.current_tasks:
            if task['id'] == task_id:
                task['tag'] = tag_value if tag_value else None
                task['tag_color'] = color_hex
                break

        # Zapisz zmianę w bazie danych
        try:
            self.db_manager.update_task(task_id, category=tag_value if tag_value else None)
        except Exception as e:
            print(f"Błąd aktualizacji tagu zadania {task_id}: {e}")

    def toggle_task_archive(self, task_id, state):
        """Przełącza status archiwizacji zadania"""
        try:
            archived = (state == Qt.CheckState.Checked.value)
            print(f"Zadanie {task_id} - Archiwum: {archived}")
            
            # Zapisz status archiwizacji w bazie danych
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE tasks SET archived = ? WHERE id = ?', (1 if archived else 0, task_id))
                conn.commit()
            
            # Aktualizuj lokalnie
            for task in self.current_tasks:
                if task['id'] == task_id:
                    task['archived'] = archived
                    break
            
            # Odśwież widok jeśli filtr nie pokazuje zarchiwizowanych
            status_filter = self.status_filter.currentText()
            if status_filter != "Zarchiwizowane" and archived:
                self.populate_table()
            
        except Exception as e:
            print(f"Błąd zmiany statusu archiwizacji: {e}")
            import traceback
            traceback.print_exc()
    
    def filter_tasks_data(self):
        """Filtruje zadania według ustawionych kryteriów"""
        filtered = self.current_tasks.copy()
        
        # Filtr statusu
        status_filter = self.status_filter.currentText()
        if status_filter == "Aktywne":
            # Aktywne = niezakończone i niezarchiwizowane
            filtered = [task for task in filtered if not task['status'] and not task.get('archived', False)]
        elif status_filter == "Zakończone":
            # Zakończone = zakończone ale niezarchiwizowane
            filtered = [task for task in filtered if task['status'] and not task.get('archived', False)]
        elif status_filter == "Zarchiwizowane":
            # Tylko zarchiwizowane
            filtered = [task for task in filtered if task.get('archived', False)]
        else:  # "Wszystkie"
            # Wszystkie bez zarchiwizowanych
            filtered = [task for task in filtered if not task.get('archived', False)]
            
        # Filtr TAG
        tag_filter = self.tag_filter.currentText()
        if tag_filter != "Wszystkie":
            filtered = [task for task in filtered if task['tag'] == tag_filter]
            
        # Filtr wyszukiwania
        search_text = self.search_input.text().lower()
        if search_text:
            filtered = [task for task in filtered if search_text in task['task'].lower()]
        
        # Automatyczne przenoszenie ukończonych pod nieukończone
        auto_move = self.db_manager.get_setting('task_auto_move_completed', 'false')
        if auto_move == 'true':
            # Sortuj: nieukończone (False) na górze, ukończone (True) na dole
            filtered.sort(key=lambda t: (t['status'], t['id']))
            
        return filtered
        
    def filter_tasks(self):
        """Odświeża tabelę z filtrami"""
        self.populate_table()
        
    def toggle_task_status(self, task_id, state):
        """Przełącza status zadania"""
        task = None
        for t in self.current_tasks:
            if t['id'] == task_id:
                task = t
                is_completed = (state == Qt.CheckState.Checked.value)
                task['status'] = is_completed
                
                # Ustaw datę realizacji
                if is_completed:
                    task['date_completed'] = datetime.datetime.now()
                    completion_date = task['date_completed'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    task['date_completed'] = None
                    completion_date = None
                
                # Zapisz zmiany do bazy danych
                try:
                    self.db_manager.update_task(task_id, status=is_completed, date_completed=completion_date)
                    print(f"DEBUG: Zaktualizowano status zadania {task_id}: {is_completed}, data realizacji: {completion_date}")
                except Exception as e:
                    print(f"Błąd aktualizacji zadania {task_id}: {e}")
                
                break
                
        if task:
            self.populate_table()
            self.load_existing_tags()
            self.task_updated.emit(task['id'], task)
        
    def load_existing_tags(self):
        """Ładuje istniejące tagi do filtra"""
        existing_tags = list(set([task['tag'] for task in self.current_tasks if task['tag']]))
        
        self.tag_filter.clear()
        self.tag_filter.addItem("Wszystkie")
        self.tag_filter.addItems(existing_tags)
        
    def open_task_note(self, task_id):
        """Otwiera notatkę dla zadania"""
        # TODO: Integracja z systemem notatek
        print(f"Otwieranie notatki dla zadania {task_id}")
        
    def toggle_kanban(self, task_id, currently_in_kanban):
        """Przełącza stan zadania w KanBan (dodaje lub usuwa)"""
        try:
            # Odwróć stan - jeśli jest w kanban, usuń; jeśli nie ma, dodaj
            new_kanban_value = 0 if currently_in_kanban else 1
            action = "usunięte z" if currently_in_kanban else "przeniesione do"
            
            print(f"Zadanie {task_id} {action} KanBan")
            
            # Aktualizuj flagę kanban w bazie danych
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE tasks SET kanban = ? WHERE id = ?', (new_kanban_value, task_id))
                conn.commit()
            
            # Odśwież widok zadań aby pokazać zmianę
            self.load_tasks()
            
            print(f"Zadanie {task_id} - flaga kanban ustawiona na {new_kanban_value}")
        except Exception as e:
            print(f"Błąd przełączania zadania w KanBan: {e}")
            import traceback
            traceback.print_exc()
        
    def show_context_menu(self, position):
        """Pokazuje menu kontekstowe dla tabeli"""
        if self.tasks_table.itemAt(position) is None:
            return
            
        menu = QMenu(self)
        colors = self.theme_manager.get_current_colors()
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {colors['widget_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 4px;
                color: {colors['text_color']};
            }}
            QMenu::item {{
                padding: 8px 16px;
                color: {colors['text_color']};
            }}
            QMenu::item:selected {{
                background-color: {colors['selection_bg']};
                color: {colors['selection_text']};
            }}
        """)
        
        edit_action = menu.addAction("✏️ Edytuj zadanie")
        delete_action = menu.addAction("🗑️ Usuń zadanie")
        menu.addSeparator()
        note_action = menu.addAction("📝 Otwórz notatkę")
        kanban_action = menu.addAction("📊 Przenieś do KanBan")
        archive_action = menu.addAction("📦 Archiwizuj")
        
        action = menu.exec(self.tasks_table.mapToGlobal(position))
        
        if action:
            print(f"DEBUG: Wybrana akcja z menu: {action.text()}")
        else:
            print("DEBUG: Brak wybranej akcji (anulowano)")
            return
        
        row = self.tasks_table.rowAt(position.y())
        print(f"DEBUG: Wiersz: {row}")
        
        if row >= 0 and row < len(self._row_task_ids):
            # Pobierz ID zadania z mapy wiersz -> ID
            task_id = self._row_task_ids[row]
            print(f"DEBUG: Zadanie ID z _row_task_ids: {task_id}")
            
            if action == edit_action:
                self.edit_task(task_id)
            elif action == delete_action:
                self.delete_task(task_id)
            elif action == note_action:
                self.open_task_note(task_id)
            elif action == kanban_action:
                # Pobierz aktualny stan kanban dla zadania
                current_kanban = False
                for task in self.current_tasks:
                    if task['id'] == task_id:
                        current_kanban = task.get('kanban', 0) == 1
                        break
                self.toggle_kanban(task_id, current_kanban)
            elif action == archive_action:
                print(f"DEBUG: ARCHIVE_ACTION wykryty!")
                # Pobierz aktualny stan archiwizacji dla zadania
                current_archived = False
                for task in self.current_tasks:
                    if task['id'] == task_id:
                        current_archived = task.get('archived', False)
                        break
                print(f"DEBUG: Archiwizacja zadania {task_id}, aktualny stan: {current_archived}")
                # Jeśli zadanie nie jest zarchiwizowane, zaarchiwizuj (Checked)
                # Jeśli jest zarchiwizowane, odarchiwizuj (Unchecked)
                new_state = Qt.CheckState.Checked.value if not current_archived else Qt.CheckState.Unchecked.value
                print(f"DEBUG: Nowy stan: {new_state}")
                self.toggle_task_archive(task_id, new_state)
                
    def edit_task(self, task_id):
        """Edytuje zadanie"""
        # TODO: Implementuj dialog edycji
        print(f"Edytowanie zadania {task_id}")
        
    def delete_task(self, task_id):
        """Usuwa zadanie"""
        reply = QMessageBox.question(
            self, 
            "Potwierdź usunięcie",
            "Czy na pewno chcesz usunąć to zadanie?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_tasks = [task for task in self.current_tasks if task['id'] != task_id]
            self.populate_table()
            self.load_existing_tags()
            self.task_deleted.emit(task_id)
            print(f"Usunięto zadanie {task_id}")
            
    def show_column_config(self):
        """Pokazuje dialog konfiguracji kolumn"""
        # TODO: Implementuj dialog konfiguracji kolumn
        print("Konfiguracja kolumn - TODO")# TEST
    
    def update_tags_from_settings(self):
        """Aktualizuje listę tagów z listy słownikowej 'Tagi zadań'"""
        try:
            tag_entries = []

            # Pobierz tagi z listy słownikowej
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                # Pobierz ID listy słownikowej dla kolumny TAG
                cursor.execute("SELECT dictionary_list_id FROM task_columns WHERE name='TAG'")
                result = cursor.fetchone()
                
                if result and result[0]:
                    tag_list_id = result[0]
                    
                    # Pobierz tagi z listy słownikowej
                    cursor.execute("""
                        SELECT id, value FROM dictionary_list_items 
                        WHERE list_id = ? 
                        ORDER BY order_index
                    """, (tag_list_id,))
                    
                    tags = cursor.fetchall()
                    
                    # Kolory domyślne (bo lista słownikowa nie ma kolorów)
                    default_colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71', '#9b59b6', '#1abc9c', '#34495e']
                    
                    for i, (tag_id, tag_name) in enumerate(tags):
                        if tag_name:
                            tag_entries.append({
                                "id": tag_id,
                                "name": tag_name,
                                "color": default_colors[i % len(default_colors)]
                            })
                    
                    print(f"DEBUG: Załadowano {len(tag_entries)} tagów z listy słownikowej ID={tag_list_id}")
                else:
                    print("UWAGA: Kolumna TAG nie ma przypisanej listy słownikowej")
                
                conn.close()
            except Exception as fetch_exc:
                print(f"Błąd pobierania tagów z listy słownikowej: {fetch_exc}")
                import traceback
                traceback.print_exc()

            # Zapisz mapę kolorów tagów do dalszego wykorzystania
            self.tag_color_map = {entry["name"]: entry["color"] for entry in tag_entries}

            # Zaktualizuj filtr tagów w UI
            current_selection = self.tag_filter.currentText()
            self.tag_filter.blockSignals(True)
            self.tag_filter.clear()
            self.tag_filter.addItem("Wszystkie")

            for entry in tag_entries:
                self.tag_filter.addItem(entry["name"])

            index = self.tag_filter.findText(current_selection)
            if index >= 0:
                self.tag_filter.setCurrentIndex(index)
            else:
                self.tag_filter.setCurrentIndex(0)

            self.tag_filter.blockSignals(False)

            # Utwórz/zaktualizuj listę słownikową dla kolumny TAG
            self.update_tag_dictionary_list(tag_entries)

        except Exception as e:
            print(f"Błąd aktualizacji tagów z ustawień: {e}")
            import traceback
            traceback.print_exc()

    def update_tag_dictionary_list(self, tag_entries):
        """Tworzy/aktualizuje listę słownikową dla tagów"""
        try:
            # Sprawdź czy lista słownikowa dla tagów już istnieje
            existing_list = self.db_manager.get_dictionary_list_by_name("Tagi zadań", "task")
            
            if existing_list:
                tag_list_id = existing_list['id']  # ID listy ze słownika
            else:
                # Utwórz nową listę słownikową
                list_config = {
                    "name": "Tagi zadań",
                    "description": "Lista tagów dostępnych dla zadań",
                    "context": "task"
                }
                tag_list_id = self.db_manager.create_dictionary_list(list_config)
            
            # Usuń stare elementy listy jeśli istnieją
            if tag_list_id:
                try:
                    existing_items = self.db_manager.get_dictionary_list_items(tag_list_id)
                    for item in existing_items:
                        self.db_manager.delete_dictionary_list_item(item[0])  # item[0] to ID
                except Exception as e:
                    pass  # Ignoruj błędy usuwania
                
                # Dodaj nowe elementy tagów do listy słownikowej
                for entry in tag_entries:
                    try:
                        self.db_manager.add_dictionary_list_item(
                            list_id=tag_list_id,
                            value=entry["name"],
                            description=f"Tag: {entry['name']}"
                        )
                    except Exception as e:
                        print(f"Błąd dodawania tagu {entry['name']}: {e}")
                
                # Zaktualizuj delegata kolumny TAG
                if hasattr(self, 'column_delegate'):
                    self.column_delegate.set_column_type("TAG", "Lista", tag_list_id)
                    
                    # Dodatkowo zaktualizuj kolumnę TAG w visible_columns
                    for col in self.visible_columns:
                        if col["name"] == "TAG":
                            col["dictionary_list_id"] = tag_list_id
                            break
                    
                    # Zaktualizuj kolumnę TAG w bazie danych
                    try:
                        # Znajdź ID kolumny TAG
                        all_columns = self.db_manager.get_task_columns()
                        tag_column = next((c for c in all_columns if c['name'] == 'TAG'), None)
                        if tag_column:
                            self.db_manager.update_task_column(
                                tag_column['id'], 
                                dictionary_list_id=tag_list_id
                            )
                            print(f"DEBUG: Zaktualizowano kolumnę TAG (ID={tag_column['id']}) z dictionary_list_id={tag_list_id}")
                    except Exception as e:
                        print(f"Błąd aktualizacji kolumny TAG w bazie: {e}")
                    
                print(f"Zaktualizowano listę słownikową tagów (ID: {tag_list_id}) z {len(tag_entries)} elementami")
                
        except Exception as e:
            print(f"Błąd aktualizacji listy słownikowej tagów: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_cell_coloring(self):
        """Stosuje kolorowanie komórek po wypełnieniu tabeli"""
        try:
            tag_col = self.get_column_index("TAG")
            if tag_col is None:
                return
            default_text = self.theme_manager.get_current_colors().get('text_color', '#2c3e50')

            self._suspend_item_updates = True
            try:
                for row in range(self.tasks_table.rowCount()):
                    tag_item = self.tasks_table.item(row, tag_col)
                    if not tag_item:
                        continue

                    tag_value = (tag_item.text() or "").strip()
                    tag_color_hex = tag_item.data(Qt.ItemDataRole.UserRole + 1)
                    if not tag_color_hex and tag_value:
                        tag_color_hex = self.get_color_for_tag(tag_value)
                        tag_item.setData(Qt.ItemDataRole.UserRole + 1, tag_color_hex)

                    if tag_value and tag_color_hex:
                        base_color = QColor(tag_color_hex)
                        tag_brush = QBrush(base_color)
                        tag_item.setBackground(tag_brush)
                        tag_item.setData(Qt.ItemDataRole.BackgroundRole, tag_brush)

                        brightness = (base_color.red() * 299 + base_color.green() * 587 + base_color.blue() * 114) / 1000
                        text_color = QColor("#000000") if brightness > 160 else QColor("#ffffff")
                        tag_item.setForeground(text_color)
                        self.set_row_background_color(row, tag_color_hex)
                    else:
                        tag_item.setData(Qt.ItemDataRole.BackgroundRole, None)
                        tag_item.setBackground(QBrush())
                        tag_item.setForeground(QColor(default_text))
                        self.set_row_background_color(row, None)
            finally:
                self._suspend_item_updates = False
                        
        except Exception as e:
            print(f"Błąd stosowania kolorowania komórek: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_tasks(self):
        """Odświeża listę zadań i kolory tagów"""
        try:
            self.load_tasks()
            self.update_tags_from_settings()
        except Exception as e:
            print(f"Błąd odświeżania zadań: {e}")
            import traceback
            traceback.print_exc()
