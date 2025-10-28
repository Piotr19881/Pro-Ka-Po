"""
Dialog szybkiego dodawania zadań
Minimalistyczny interfejs wzorowany na dolnym pasku zadań
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QLabel, QFrame, QWidget, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
import sys
import os

# Dodaj ścieżkę do modułu database
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class QuickTaskDialog(QDialog):
    """Dialog szybkiego dodawania zadań - kopia dolnego paska zadań"""
    
    task_added = pyqtSignal(dict)  # Sygnał emitowany po dodaniu zadania
    
    def __init__(self, parent=None, theme_manager=None, db_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.db_manager = db_manager
        self.task_columns = []  # Lista kolumn zadań
        self.panel_widgets = {}  # Mapa widget'ów panelu
        self.panel_labels = []  # Lista etykiet panelu do stylowania
        
        self.init_ui()
        self.load_columns_config()
        self.setup_shortcuts()
        
        # Zastosuj motyw na końcu, gdy wszystkie widgety są już utworzone
        if self.theme_manager:
            self.apply_theme()
        
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        self.setWindowTitle(self.tr("Szybkie dodawanie zadania"))
        self.setMinimumWidth(800)
        self.setMaximumHeight(150)
        
        # Główny layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
 
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # Pole zadania (główne pole tekstowe)
        task_layout = QHBoxLayout()
        task_layout.setSpacing(5)
        
        task_label = QLabel(self.tr("Zadanie:"))
        task_label.setMinimumWidth(80)
        task_layout.addWidget(task_label)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText(self.tr("Wpisz treść zadania..."))
        self.task_input.returnPressed.connect(self.add_task)
        task_layout.addWidget(self.task_input, 1)
        
        main_layout.addLayout(task_layout)
        
        # Panel dodatkowych pól (będzie wypełniony dynamicznie)
        self.panel_layout = QHBoxLayout()
        self.panel_layout.setSpacing(10)
        self.panel_frame = QWidget()
        self.panel_frame.setLayout(self.panel_layout)
        main_layout.addWidget(self.panel_frame)
        
        # Przyciski akcji
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.add_button = QPushButton(self.tr("Dodaj zadanie"))
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setMinimumWidth(120)
        buttons_layout.addWidget(self.add_button)
        
        cancel_button = QPushButton(self.tr("Anuluj"))
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumWidth(120)
        buttons_layout.addWidget(cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_shortcuts(self):
        """Konfiguruje skróty klawiszowe"""
        # Ctrl+Enter - dodaj zadanie
        add_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        add_shortcut.activated.connect(self.add_task)
        
        # Escape - zamknij dialog
        close_shortcut = QShortcut(QKeySequence("Escape"), self)
        close_shortcut.activated.connect(self.reject)
    
    def load_columns_config(self):
        """Ładuje konfigurację kolumn z bazy danych"""
        if not self.db_manager:
            print("DEBUG: Brak db_manager, pomijam ładowanie kolumn")
            return
        
        try:
            # Pobierz kolumny zadań
            self.task_columns = self.db_manager.get_task_columns()
            print(f"DEBUG: Załadowano {len(self.task_columns)} kolumn")
            
            # Utwórz widgety dla kolumn z in_panel=True
            self.create_panel_widgets()
            
        except Exception as e:
            print(f"ERROR: Błąd ładowania konfiguracji kolumn: {e}")
            import traceback
            traceback.print_exc()
    
    def create_panel_widgets(self):
        """Tworzy widgety dla kolumn z flagą in_panel"""
        # Wyczyść obecne widgety
        while self.panel_layout.count():
            item = self.panel_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.panel_widgets.clear()
        
        # Przefiltruj kolumny - tylko te z in_panel=True i nie KanBan
        panel_columns = [
            col for col in self.task_columns 
            if col.get('in_panel', False) and col['name'] != 'KanBan'
        ]
        
        print(f"DEBUG: Tworzenie widgetów dla {len(panel_columns)} kolumn panelu")
        
        for col in panel_columns:
            col_name = col['name']
            col_type = col['type']
            
            # Kontener dla kolumny
            col_widget = QWidget()
            col_layout = QHBoxLayout(col_widget)
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(5)
            
            # Etykieta
            label = QLabel(f"{col_name}:")
            label.setMinimumWidth(60)
            col_layout.addWidget(label)
            self.panel_labels.append(label)  # Dodaj do listy dla późniejszego stylowania
            
            # Widget w zależności od typu
            if col_type == 'Lista':
                widget = self.create_list_widget(col)
                col_layout.addWidget(widget, 1)
                self.panel_widgets[col_name] = widget
            elif col_type == 'CheckBox':
                widget = QCheckBox()
                col_layout.addWidget(widget)
                self.panel_widgets[col_name] = widget
            elif col_type == 'Data':
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
                col_layout.addWidget(widget, 1)
                self.panel_widgets[col_name] = widget
            else:  # Tekstowa lub inne
                widget = QLineEdit()
                # Note: col_name pochodzi z bazy danych, nie tłumaczymy dynamicznych nazw kolumn
                widget.setPlaceholderText(self.tr("Wpisz") + f" {col_name.lower()}...")
                col_layout.addWidget(widget, 1)
                self.panel_widgets[col_name] = widget
            
            # Dodaj do panelu
            self.panel_layout.addWidget(col_widget)
        
        # Dodaj stretch na końcu
        self.panel_layout.addStretch()
    
    def create_list_widget(self, col_config):
        """Tworzy ComboBox dla kolumny typu Lista"""
        combo = QComboBox()
        
        # Pobierz opcje z listy słownikowej
        if 'dictionary_list_id' in col_config and col_config['dictionary_list_id']:
            try:
                list_id = col_config['dictionary_list_id']
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT value FROM dictionary_list_items 
                    WHERE list_id = ? 
                    ORDER BY order_index
                """, (list_id,))
                
                options = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                if options:
                    combo.addItems(options)
                else:
                    combo.addItem(self.tr("Brak opcji"))
            except Exception as e:
                print(f"ERROR: Błąd ładowania opcji listy: {e}")
                combo.addItem(self.tr("Błąd ładowania"))
        else:
            combo.addItem(self.tr("Brak konfiguracji"))
        
        return combo
    
    def add_task(self):
        """Dodaje zadanie do bazy danych"""
        # Pobierz treść zadania
        task_title = self.task_input.text().strip()
        
        if not task_title:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.tr("Błąd"), self.tr("Wpisz treść zadania!"))
            self.task_input.setFocus()
            return
        
        try:
            # Przygotuj dane zadania
            task_data = {
                'title': task_title,
                'description': '',
                'status': False
            }
            
            # Zbierz wartości z widgetów panelu
            for col_name, widget in self.panel_widgets.items():
                if isinstance(widget, QComboBox):
                    task_data[col_name] = widget.currentText()
                elif isinstance(widget, QCheckBox):
                    task_data[col_name] = widget.isChecked()
                elif isinstance(widget, QDateEdit):
                    task_data[col_name] = widget.date().toString("yyyy-MM-dd")
                elif isinstance(widget, QLineEdit):
                    task_data[col_name] = widget.text()
            
            # Dodaj zadanie do bazy danych
            if self.db_manager:
                # Przygotuj dane dla db_manager
                category = task_data.get('TAG', '')
                
                task_id = self.db_manager.add_task(
                    title=task_title,
                    description='',
                    category=category
                )
                
                if task_id:
                    print(f"DEBUG: Dodano zadanie ID={task_id}")
                    
                    # Zaktualizuj dodatkowe kolumny
                    self.update_task_columns(task_id, task_data)
                    
                    # Emituj sygnał
                    self.task_added.emit(task_data)
                    
                    # Wyczyść formularz
                    self.clear_form()
                    
                    # Pokaż komunikat sukcesu
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, self.tr("Sukces"), self.tr("Zadanie zostało dodane!"))
                    
                    # Zamknij dialog
                    self.accept()
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.critical(self, self.tr("Błąd"), self.tr("Nie udało się dodać zadania do bazy danych!"))
            
        except Exception as e:
            print(f"ERROR: Błąd dodawania zadania: {e}")
            import traceback
            traceback.print_exc()
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, self.tr("Błąd"), self.tr("Wystąpił błąd podczas dodawania zadania:") + f"\n{e}")
    
    def update_task_columns(self, task_id, task_data):
        """Aktualizuje wartości w niestandardowych kolumnach zadania"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Pobierz bieżące dane zadania
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            task_row = cursor.fetchone()
            
            if not task_row:
                conn.close()
                return
            
            # Pobierz nazwy kolumn
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Przygotuj UPDATE
            update_parts = []
            update_values = []
            
            for col_name, value in task_data.items():
                # Pomiń standardowe pola
                if col_name in ['title', 'description', 'status']:
                    continue
                
                # Sprawdź czy kolumna istnieje w tabeli tasks
                safe_col_name = col_name.lower().replace(' ', '_')
                if safe_col_name in columns:
                    update_parts.append(f"{safe_col_name} = ?")
                    
                    # Konwersja wartości
                    if isinstance(value, bool):
                        update_values.append(1 if value else 0)
                    else:
                        update_values.append(value)
            
            if update_parts:
                update_values.append(task_id)
                sql = f"UPDATE tasks SET {', '.join(update_parts)} WHERE id = ?"
                cursor.execute(sql, update_values)
                conn.commit()
                print(f"DEBUG: Zaktualizowano {len(update_parts)} kolumn dla zadania ID={task_id}")
            
            conn.close()
            
        except Exception as e:
            print(f"ERROR: Błąd aktualizacji kolumn zadania: {e}")
            import traceback
            traceback.print_exc()
    
    def clear_form(self):
        """Czyści formularz"""
        self.task_input.clear()
        
        for widget in self.panel_widgets.values():
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate.currentDate())
            elif isinstance(widget, QLineEdit):
                widget.clear()
        
        # Ustaw fokus na pole zadania
        self.task_input.setFocus()
    
    def apply_theme(self):
        """Stosuje motyw do dialogu"""
        if not self.theme_manager:
            return
        
        try:
            # Główne okno
            colors = self.theme_manager.get_current_colors()
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {colors['widget_bg']};
                    color: {colors['text_color']};
                }}
                QFrame {{
                    background-color: {colors['border_color']};
                }}
            """)
            
            # Wszystkie etykiety - znajdź je wszystkie w dialogu
            all_labels = self.findChildren(QLabel)
            for label in all_labels:
                label.setStyleSheet(self.theme_manager.get_label_style())
            
            # Pola tekstowe
            self.task_input.setStyleSheet(self.theme_manager.get_line_edit_style())
            
            # Style dla widgetów panelu
            for widget in self.panel_widgets.values():
                if isinstance(widget, QLineEdit):
                    widget.setStyleSheet(self.theme_manager.get_line_edit_style())
                elif isinstance(widget, QComboBox):
                    widget.setStyleSheet(self.theme_manager.get_combo_style())
                elif isinstance(widget, QCheckBox):
                    widget.setStyleSheet(self.theme_manager.get_checkbox_style())
                elif isinstance(widget, QDateEdit):
                    widget.setStyleSheet(self.theme_manager.get_date_edit_style())
            
            # Przyciski
            self.add_button.setStyleSheet(self.theme_manager.get_button_style())
            
            # Przycisk Anuluj - znajdź go w layoutcie
            buttons_layout = self.layout().itemAt(self.layout().count() - 1).layout()
            if buttons_layout:
                for i in range(buttons_layout.count()):
                    item = buttons_layout.itemAt(i)
                    if item and item.widget() and isinstance(item.widget(), QPushButton):
                        widget = item.widget()
                        if widget.text() == self.tr("Anuluj"):
                            widget.setStyleSheet(self.theme_manager.get_button_style())
            
        except Exception as e:
            print(f"ERROR: Błąd stosowania motywu: {e}")
