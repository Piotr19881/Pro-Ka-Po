from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QCheckBox,
                             QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class KanbanView(QWidget):
    """Widok Kanban z trzema kolumnami: Do wykonania, Realizowane, Zakończone"""
    
    task_status_changed = pyqtSignal(int, bool)  # task_id, completed
    task_moved = pyqtSignal(int, str)  # task_id, new_status
    note_requested = pyqtSignal(int)  # task_id
    
    def __init__(self, db_manager, theme_manager):
        super().__init__()
        self.db_manager = db_manager
        self.theme_manager = theme_manager
        self.tasks = []
        
        # Stany zwinięcia/rozwinięcia tabel
        self.todo_collapsed = False
        self.done_collapsed = False
        
        # Referencje do elementów UI dla refresh_theme
        self.column_headers = {}
        self.collapse_buttons = {}
        
        self.init_ui()
    
    def get_column_colors(self):
        """Zwraca kolory dla kolumn w zależności od aktywnego motywu"""
        colors = self.theme_manager.get_current_colors()
        
        if self.theme_manager.current_theme == 'dark':
            return {
                'todo': colors['border_color'],      # zielony Matrix
                'in_progress': colors['warning_color'],  # żółty
                'done': colors['success_color']      # jasnozielony
            }
        else:
            return {
                'todo': '#e74c3c',      # czerwony
                'in_progress': '#f39c12',  # pomarańczowy
                'done': '#27ae60'       # zielony
            }
        
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        colors = self.theme_manager.get_current_colors()
        column_colors = self.get_column_colors()
        
        # Ustaw styl tła dla głównego widgetu
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['main_bg']};
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Nagłówek
        header = QLabel("Tablica Kanban")
        header.setStyleSheet(self.theme_manager.get_label_style(bold=True))
        header.setFont(QFont(colors['font_family'].replace("'", ""), 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Layout dla trzech kolumn
        self.columns_layout = QHBoxLayout()
        self.columns_layout.setSpacing(10)
        
        # Kolumna 1: Do wykonania
        self.todo_frame, todo_header, todo_btn = self.create_column_frame("Do wykonania", column_colors['todo'], collapsible=True, column_type="todo")
        self.column_headers['todo'] = todo_header
        if todo_btn:
            self.collapse_buttons['todo'] = todo_btn
        self.todo_table = self.create_todo_table()
        self.todo_frame.layout().addWidget(self.todo_table)
        self.columns_layout.addWidget(self.todo_frame, 1)
        
        # Kolumna 2: Realizowane
        self.in_progress_frame, in_progress_header, _ = self.create_column_frame("Realizowane", column_colors['in_progress'], collapsible=False)
        self.column_headers['in_progress'] = in_progress_header
        self.in_progress_table = self.create_in_progress_table()
        self.in_progress_frame.layout().addWidget(self.in_progress_table)
        self.columns_layout.addWidget(self.in_progress_frame, 1)
        
        # Kolumna 3: Zakończone
        self.done_frame, done_header, done_btn = self.create_column_frame("Zakończone", column_colors['done'], collapsible=True, column_type="done")
        self.column_headers['done'] = done_header
        if done_btn:
            self.collapse_buttons['done'] = done_btn
        self.done_table = self.create_done_table()
        self.done_frame.layout().addWidget(self.done_table)
        self.columns_layout.addWidget(self.done_frame, 1)
        
        main_layout.addLayout(self.columns_layout)
        
    def create_column_frame(self, title, color, collapsible=False, column_type=None):
        """Tworzy ramkę dla kolumny z nagłówkiem i opcjonalnym przyciskiem zwijania"""
        colors = self.theme_manager.get_current_colors()
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['widget_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 5px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Layout dla nagłówka z przyciskiem
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        # Nagłówek kolumny
        header = QLabel(title)
        header.setFont(QFont(colors['font_family'].replace("'", ""), 12, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Kolor tekstu dla nagłówka - biały dla ciemnych tła, biały też dla jasnych (dla lepszej czytelności)
        text_color = colors['widget_bg'] if self.theme_manager.current_theme == 'light' else colors['main_bg']
        
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: {text_color};
                padding: 8px;
                border-radius: 4px;
                border: 1px solid {color};
            }}
        """)
        header_layout.addWidget(header)
        
        # Przycisk zwijania (będzie None jeśli nie collapsible)
        collapse_btn = None
        
        # Dodaj przycisk zwijania/rozwijania jeśli wymagane
        if collapsible and column_type:
            collapse_btn = QPushButton("▼")
            collapse_btn.setFixedSize(30, 30)
            
            hover_color = self.darken_color(color)
            collapse_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {text_color};
                    border: 1px solid {color};
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                    border: 1px solid {hover_color};
                }}
            """)
            
            # Podłącz do odpowiedniej funkcji w zależności od typu kolumny
            if column_type == "todo":
                collapse_btn.clicked.connect(lambda: self.toggle_todo_column(collapse_btn))
            elif column_type == "done":
                collapse_btn.clicked.connect(lambda: self.toggle_done_column(collapse_btn))
            
            header_layout.addWidget(collapse_btn)
        
        # Dodaj layout nagłówka do głównego layoutu
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)
        
        return frame, header, collapse_btn
    
    def darken_color(self, hex_color):
        """Przyciemnia kolor hex o 20%"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def toggle_todo_column(self, button):
        """Zwija/rozwija kolumnę Do wykonania"""
        self.todo_collapsed = not self.todo_collapsed
        self.todo_table.setVisible(not self.todo_collapsed)
        button.setText("▶" if self.todo_collapsed else "▼")
        self.update_column_stretches()
    
    def toggle_done_column(self, button):
        """Zwija/rozwija kolumnę Zakończone"""
        self.done_collapsed = not self.done_collapsed
        self.done_table.setVisible(not self.done_collapsed)
        button.setText("▶" if self.done_collapsed else "▼")
        self.update_column_stretches()
    
    def update_column_stretches(self):
        """Aktualizuje proporcje kolumn w zależności od tego, które są zwinięte"""
        # Ustal stretch factor dla każdej kolumny
        todo_stretch = 0 if self.todo_collapsed else 1
        done_stretch = 0 if self.done_collapsed else 1
        
        # Kolumna "Realizowane" zajmuje więcej miejsca gdy inne są zwinięte
        in_progress_stretch = 1
        if self.todo_collapsed or self.done_collapsed:
            in_progress_stretch = 2
        if self.todo_collapsed and self.done_collapsed:
            in_progress_stretch = 3
        
        # Ustaw nowe stretch factors
        self.columns_layout.setStretch(0, todo_stretch)
        self.columns_layout.setStretch(1, in_progress_stretch)
        self.columns_layout.setStretch(2, done_stretch)
        
    def create_todo_table(self):
        """Tworzy tabelę dla zadań do wykonania (2 kolumny: zadanie, przycisk)"""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Zadanie", "→"])
        
        # Konfiguracja nagłówka
        header = table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        
        table.setColumnWidth(1, 50)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        
        # Stylizacja
        table.setAlternatingRowColors(True)
        table.setStyleSheet(self.theme_manager.get_table_style())
        
        return table
        
    def create_in_progress_table(self):
        """Tworzy tabelę dla zadań w realizacji (3 kolumny: status, zadanie, notatka)"""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["✓", "Zadanie", "📝"])
        
        # Konfiguracja nagłówka
        header = table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        
        table.setColumnWidth(0, 50)
        table.setColumnWidth(2, 50)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        
        # Stylizacja
        table.setAlternatingRowColors(True)
        table.setStyleSheet(self.theme_manager.get_table_style())
        
        return table
        
    def create_done_table(self):
        """Tworzy tabelę dla zadań zakończonych (1 kolumna: przekreślone zadanie)"""
        table = QTableWidget()
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Zadanie"])
        
        # Konfiguracja nagłówka
        header = table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        
        # Stylizacja
        table.setAlternatingRowColors(True)
        table.setStyleSheet(self.theme_manager.get_table_style())
        
        return table
        
    def load_tasks(self):
        """Ładuje zadania z flagą kanban=1 z bazy danych"""
        try:
            # Pobierz wszystkie zadania
            all_tasks = self.db_manager.get_tasks()
            
            # Filtruj zadania które mają kanban=1
            self.tasks = []
            for task in all_tasks:
                # Sprawdź czy zadanie ma kolumnę kanban (index 10 po dodaniu)
                # Struktura: (id, title, description, status, priority, category, due_date, note_id, created_at, updated_at, kanban)
                kanban_flag = task[10] if len(task) > 10 else 0
                
                if kanban_flag == 1:
                    task_dict = {
                        'id': task[0],
                        'title': task[1],
                        'description': task[2] or '',
                        'status': task[3],  # 'todo', 'in_progress', 'completed'
                        'note_id': task[7] if len(task) > 7 else None
                    }
                    self.tasks.append(task_dict)
            
            # Wypełnij tabele
            self.populate_tables()
            
        except Exception as e:
            print(f"Błąd ładowania zadań Kanban: {e}")
            import traceback
            traceback.print_exc()
            
    def populate_tables(self):
        """Wypełnia tabele zadaniami według statusu"""
        # Wyczyść tabele
        self.todo_table.setRowCount(0)
        self.in_progress_table.setRowCount(0)
        self.done_table.setRowCount(0)
        
        for task in self.tasks:
            status = task['status']
            
            if status == 'todo':
                self.add_task_to_todo(task)
            elif status == 'in_progress':
                self.add_task_to_in_progress(task)
            elif status == 'completed':
                self.add_task_to_done(task)
                
    def add_task_to_todo(self, task):
        """Dodaje zadanie do kolumny 'Do wykonania'"""
        row = self.todo_table.rowCount()
        self.todo_table.insertRow(row)
        
        # Kolumna 1: Zadanie
        task_item = QTableWidgetItem(task['title'])
        task_item.setData(Qt.ItemDataRole.UserRole, task['id'])
        self.todo_table.setItem(row, 0, task_item)
        
        # Kolumna 2: Przycisk strzałki
        move_btn = QPushButton("→")
        move_btn.setMaximumWidth(40)
        move_btn.setStyleSheet(self.theme_manager.get_button_style('default'))
        move_btn.clicked.connect(lambda checked, t_id=task['id']: self.move_to_in_progress(t_id))
        self.todo_table.setCellWidget(row, 1, move_btn)
        
    def add_task_to_in_progress(self, task):
        """Dodaje zadanie do kolumny 'Realizowane'"""
        row = self.in_progress_table.rowCount()
        self.in_progress_table.insertRow(row)
        
        # Kolumna 1: Checkbox statusu
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_checkbox = QCheckBox()
        status_checkbox.setChecked(False)
        status_checkbox.setStyleSheet(self.theme_manager.get_checkbox_style())
        status_checkbox.stateChanged.connect(lambda state, t_id=task['id']: self.mark_as_completed(t_id, state))
        status_layout.addWidget(status_checkbox)
        
        self.in_progress_table.setCellWidget(row, 0, status_widget)
        
        # Kolumna 2: Zadanie
        task_item = QTableWidgetItem(task['title'])
        task_item.setData(Qt.ItemDataRole.UserRole, task['id'])
        self.in_progress_table.setItem(row, 1, task_item)
        
        # Kolumna 3: Przycisk notatki
        note_btn = QPushButton("📝")
        note_btn.setMaximumWidth(40)
        note_btn.setStyleSheet(self.theme_manager.get_button_style('default'))
        note_btn.clicked.connect(lambda checked, t_id=task['id']: self.open_note(t_id))
        self.in_progress_table.setCellWidget(row, 2, note_btn)
        
    def add_task_to_done(self, task):
        """Dodaje zadanie do kolumny 'Zakończone'"""
        colors = self.theme_manager.get_current_colors()
        row = self.done_table.rowCount()
        self.done_table.insertRow(row)
        
        # Przekreślona treść zadania
        task_item = QTableWidgetItem(task['title'])
        task_item.setData(Qt.ItemDataRole.UserRole, task['id'])
        
        # Stylizacja przekreślonego tekstu
        font = task_item.font()
        font.setStrikeOut(True)
        task_item.setFont(font)
        
        # Użyj koloru tekstu drugorzędnego z motywu
        task_item.setForeground(QColor(colors['text_secondary']))
        
        self.done_table.setItem(row, 0, task_item)
        
    def move_to_in_progress(self, task_id):
        """Przenosi zadanie do kolumny 'Realizowane'"""
        try:
            # Aktualizuj status w bazie danych
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', ('in_progress', task_id))
                conn.commit()
            
            # Wyemituj sygnał
            self.task_moved.emit(task_id, 'in_progress')
            
            # Przeładuj zadania
            self.load_tasks()
            
        except Exception as e:
            print(f"Błąd przenoszenia zadania: {e}")
            
    def mark_as_completed(self, task_id, state):
        """Oznacza zadanie jako zakończone"""
        try:
            completed = (state == Qt.CheckState.Checked.value)
            
            # Aktualizuj status w bazie danych
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                new_status = 'completed' if completed else 'in_progress'
                cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
                conn.commit()
            
            # Wyemituj sygnał
            self.task_status_changed.emit(task_id, completed)
            
            # Przeładuj zadania
            self.load_tasks()
            
        except Exception as e:
            print(f"Błąd oznaczania zadania jako zakończone: {e}")
            
    def open_note(self, task_id):
        """Otwiera notatkę dla zadania"""
        self.note_requested.emit(task_id)
        
    def refresh(self):
        """Odświeża widok"""
        self.load_tasks()
    
    def refresh_theme(self):
        """Odświeża widok po zmianie motywu"""
        colors = self.theme_manager.get_current_colors()
        column_colors = self.get_column_colors()
        
        # Zaktualizuj tło głównego widgetu
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['main_bg']};
            }}
        """)
        
        # Zaktualizuj style ramek kolumn
        self.todo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['widget_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 5px;
            }}
        """)
        
        self.in_progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['widget_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 5px;
            }}
        """)
        
        self.done_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['widget_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 5px;
            }}
        """)
        
        # Zaktualizuj kolory nagłówków
        text_color = colors['widget_bg'] if self.theme_manager.current_theme == 'light' else colors['main_bg']
        
        # Nagłówek "Do wykonania"
        if 'todo' in self.column_headers:
            self.column_headers['todo'].setStyleSheet(f"""
                QLabel {{
                    background-color: {column_colors['todo']};
                    color: {text_color};
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid {column_colors['todo']};
                }}
            """)
        
        # Nagłówek "Realizowane"
        if 'in_progress' in self.column_headers:
            self.column_headers['in_progress'].setStyleSheet(f"""
                QLabel {{
                    background-color: {column_colors['in_progress']};
                    color: {text_color};
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid {column_colors['in_progress']};
                }}
            """)
        
        # Nagłówek "Zakończone"
        if 'done' in self.column_headers:
            self.column_headers['done'].setStyleSheet(f"""
                QLabel {{
                    background-color: {column_colors['done']};
                    color: {text_color};
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid {column_colors['done']};
                }}
            """)
        
        # Zaktualizuj przyciski zwijania
        for btn_type in ['todo', 'done']:
            if btn_type in self.collapse_buttons:
                color = column_colors[btn_type]
                hover_color = self.darken_color(color)
                self.collapse_buttons[btn_type].setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: {text_color};
                        border: 1px solid {color};
                        border-radius: 4px;
                        font-size: 14px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {hover_color};
                        border: 1px solid {hover_color};
                    }}
                """)
        
        # Zaktualizuj style tabel
        self.todo_table.setStyleSheet(self.theme_manager.get_table_style())
        self.in_progress_table.setStyleSheet(self.theme_manager.get_table_style())
        self.done_table.setStyleSheet(self.theme_manager.get_table_style())
        
        # Przeładuj zadania, aby zastosować nowe kolory w komórkach
        self.load_tasks()

