"""
Dialogi do zarządzania tabelami w aplikacji Pro-Ka-Po V2
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel, 
                             QGroupBox, QCheckBox, QComboBox, QSpinBox,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QTreeWidget, QTreeWidgetItem, QHeaderView,
                             QColorDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class TableDialog(QDialog):
    """Dialog do dodawania/edycji tabel"""
    
    def __init__(self, parent=None, table_data=None, theme_manager=None):
        super().__init__(parent)
        self.table_data = table_data
        self.theme_manager = theme_manager
        self.is_edit_mode = table_data is not None
        
        self.setWindowTitle("Edytuj tabelę" if self.is_edit_mode else "Dodaj nową tabelę")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_table_data()
    
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Podstawowe informacje o tabeli
        self.create_basic_info_section(layout)
        
        # Konfiguracja kolumn
        self.create_columns_section(layout)
        
        # Ustawienia tabeli
        self.create_settings_section(layout)
        
        # Przyciski akcji
        self.create_buttons_section(layout)
    
    def create_basic_info_section(self, parent_layout):
        """Tworzy sekcję podstawowych informacji"""
        basic_group = QGroupBox("Podstawowe informacje")
        form_layout = QFormLayout(basic_group)
        
        # Nazwa tabeli
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Wprowadź nazwę tabeli...")
        form_layout.addRow("Nazwa tabeli:", self.name_edit)
        
        # Opis tabeli
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Opis tabeli (opcjonalnie)...")
        form_layout.addRow("Opis:", self.description_edit)
        
        parent_layout.addWidget(basic_group)
    
    def create_columns_section(self, parent_layout):
        """Tworzy sekcję konfiguracji kolumn"""
        columns_group = QGroupBox("Konfiguracja kolumn")
        columns_layout = QVBoxLayout(columns_group)
        
        # Informacja
        info_label = QLabel("Skonfiguruj kolumny, które będą wyświetlane w tabeli:")
        if self.theme_manager:
            info_label.setStyleSheet(self.theme_manager.get_info_label_style())
        else:
            info_label.setStyleSheet("color: #666; font-style: italic;")
        columns_layout.addWidget(info_label)
        
        # Drzewo kolumn z konfiguracją
        self.columns_tree = QTreeWidget()
        self.columns_tree.setHeaderLabels(["Nazwa kolumny", "Typ", "Wymagana", "Widoczna"])
        self.columns_tree.setRootIsDecorated(False)
        self.columns_tree.setAlternatingRowColors(True)
        self.columns_tree.setMaximumHeight(200)
        
        # Ustawienia kolumn
        header = self.columns_tree.header()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)      # Nazwa
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Typ
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Wymagana
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Widoczna
        
        # Dodaj domyślne kolumny
        self.load_default_columns()
        
        columns_layout.addWidget(self.columns_tree)
        
        # Sekcja dodawania nowej kolumny
        add_column_group = QGroupBox("Dodaj nową kolumnę")
        add_layout = QHBoxLayout(add_column_group)
        
        # Nazwa kolumny
        add_layout.addWidget(QLabel("Nazwa:"))
        self.new_column_name = QLineEdit()
        self.new_column_name.setPlaceholderText("Nazwa kolumny...")
        add_layout.addWidget(self.new_column_name)
        
        # Typ kolumny
        add_layout.addWidget(QLabel("Typ:"))
        self.new_column_type = QComboBox()
        self.new_column_type.addItems([
            "Tekstowa", "Data", "Godzina", "Czas", "Alarm", 
            "Waluta", "Lista", "Hiperłącze", "Operacje matematyczne", "CheckBox"
        ])
        add_layout.addWidget(self.new_column_type)
        
        # Lista słownikowa (dla typu Lista)
        self.dictionary_label = QLabel("Lista:")
        add_layout.addWidget(self.dictionary_label)
        self.dictionary_combo = QComboBox()
        
        # Załaduj prawdziwe listy słownikowe z bazy danych
        self.load_dictionary_lists()
        
        add_layout.addWidget(self.dictionary_combo)
        
        # Przycisk konfiguracji formuły (dla typu Operacje matematyczne)
        self.formula_config_btn = QPushButton("⚙ Konfiguruj formułę")
        self.formula_config_btn.clicked.connect(self.open_formula_config)
        self.formula_config_btn.setVisible(False)  # Początkowo ukryty
        add_layout.addWidget(self.formula_config_btn)
        
        # Wymagana
        self.new_column_required = QCheckBox("Wymagana")
        add_layout.addWidget(self.new_column_required)
        
        # Kolor kolumny
        add_layout.addWidget(QLabel("Kolor:"))
        self.color_btn = QPushButton("  ")
        self.color_btn.setMaximumWidth(40)
        self.color_btn.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc;")
        self.selected_color = "#ffffff"  # Domyślny kolor biały
        self.color_btn.clicked.connect(self.choose_color)
        add_layout.addWidget(self.color_btn)
        
        # Podłącz sygnał zmiany typu kolumny
        self.new_column_type.currentTextChanged.connect(self.on_column_type_changed)
        
        # Przycisk dodaj
        self.add_column_btn = QPushButton("Dodaj kolumnę")
        self.add_column_btn.clicked.connect(self.add_new_column)
        add_layout.addWidget(self.add_column_btn)
        
        columns_layout.addWidget(add_column_group)
        
        # Przyciski zarządzania kolumnami
        columns_buttons_layout = QHBoxLayout()
        
        self.edit_column_btn = QPushButton("Edytuj kolumnę")
        self.edit_column_btn.clicked.connect(self.edit_selected_column)
        self.edit_column_btn.setEnabled(False)
        columns_buttons_layout.addWidget(self.edit_column_btn)
        
        self.remove_column_btn = QPushButton("Usuń kolumnę")
        self.remove_column_btn.clicked.connect(self.remove_selected_column)
        self.remove_column_btn.setEnabled(False)
        columns_buttons_layout.addWidget(self.remove_column_btn)
        
        columns_buttons_layout.addStretch()
        columns_layout.addLayout(columns_buttons_layout)
        
        # Podłącz sygnały
        self.columns_tree.itemSelectionChanged.connect(self.on_column_selection_changed)
        self.new_column_type.currentTextChanged.connect(self.on_column_type_changed)
        
        # Ukryj listę słownikową na początku
        self.toggle_dictionary_widgets(False)
        
        parent_layout.addWidget(columns_group)
    
    def create_settings_section(self, parent_layout):
        """Tworzy sekcję ustawień tabeli"""
        settings_group = QGroupBox("Ustawienia tabeli")
        settings_layout = QVBoxLayout(settings_group)
        
        # Opcje wyświetlania
        display_layout = QHBoxLayout()
        
        # Liczba wierszy na stronę
        display_layout.addWidget(QLabel("Wierszy na stronę:"))
        self.rows_per_page_spin = QSpinBox()
        self.rows_per_page_spin.setRange(10, 1000)
        self.rows_per_page_spin.setValue(50)
        display_layout.addWidget(self.rows_per_page_spin)
        
        display_layout.addStretch()
        settings_layout.addLayout(display_layout)
        
        # Checkboxy z opcjami
        options_layout = QVBoxLayout()
        
        self.sortable_check = QCheckBox("Umożliw sortowanie kolumn")
        self.sortable_check.setChecked(True)
        options_layout.addWidget(self.sortable_check)
        
        self.filterable_check = QCheckBox("Umożliw filtrowanie danych")
        self.filterable_check.setChecked(True)
        options_layout.addWidget(self.filterable_check)
        
        self.exportable_check = QCheckBox("Umożliw eksport danych")
        self.exportable_check.setChecked(True)
        options_layout.addWidget(self.exportable_check)
        
        self.editable_check = QCheckBox("Umożliw edycję w miejscu")
        options_layout.addWidget(self.editable_check)
        
        settings_layout.addLayout(options_layout)
        parent_layout.addWidget(settings_group)
    
    def create_buttons_section(self, parent_layout):
        """Tworzy sekcję przycisków akcji"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Przycisk anuluj
        self.cancel_btn = QPushButton("Anuluj")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        # Przycisk zapisz
        save_text = "Zaktualizuj" if self.is_edit_mode else "Utwórz tabelę"
        self.save_btn = QPushButton(save_text)
        self.save_btn.clicked.connect(self.save_table)
        self.save_btn.setDefault(True)
        buttons_layout.addWidget(self.save_btn)
        
        parent_layout.addLayout(buttons_layout)
    
    def load_default_columns(self):
        """Ładuje domyślne kolumny"""
        default_columns = [
            ("ID", "Operacje matematyczne", True, True, "#e3f2fd", None),  # Dodajemy dictionary_list_id=None
        ]
        
        for col_name, col_type, is_required, is_visible, color, dictionary_list_id in default_columns:
            self.add_column_to_tree(col_name, col_type, is_required, is_visible, color, dictionary_list_id)
    
    def add_column_to_tree(self, name, col_type, is_required, is_visible, color="#ffffff", dictionary_list_id=None):
        """Dodaje kolumnę do drzewa"""
        item = QTreeWidgetItem([name, col_type, "", ""])
        
        # Checkboxy dla wymagana i widoczna
        required_check = QCheckBox()
        required_check.setChecked(is_required)
        self.columns_tree.setItemWidget(item, 2, required_check)
        
        visible_check = QCheckBox()
        visible_check.setChecked(is_visible)
        self.columns_tree.setItemWidget(item, 3, visible_check)
        
        # Przechowaj typ kolumny, kolor i dictionary_list_id
        item.setData(0, Qt.ItemDataRole.UserRole, col_type)
        item.setData(1, Qt.ItemDataRole.UserRole, color)  # Przechowaj kolor
        item.setData(2, Qt.ItemDataRole.UserRole, dictionary_list_id)  # Przechowaj dictionary_list_id
        
        # Ustaw kolor tła dla pierwszej kolumny (nazwa)
        item.setBackground(0, QColor(color))
        
        self.columns_tree.addTopLevelItem(item)
    
    def add_new_column(self):
        """Dodaje nową kolumnę"""
        name = self.new_column_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Błąd", "Nazwa kolumny nie może być pusta!")
            return
        
        col_type = self.new_column_type.currentText()
        is_required = self.new_column_required.isChecked()
        
        # Sprawdź czy typ Alarm ma kolumnę Godzina
        if col_type == "Alarm":
            if not self.has_time_column():
                QMessageBox.warning(self, "Błąd", 
                    "Kolumna typu 'Alarm' wymaga obecności kolumny typu 'Godzina' w tabeli!")
                return
        
        # Pobierz ID wybranej listy słownikowej dla kolumn typu Lista
        dictionary_list_id = None
        if col_type == "Lista":
            current_data = self.dictionary_combo.currentData()
            current_text = self.dictionary_combo.currentText()
            print(f"DEBUG: Kolumna Lista - currentText: '{current_text}', currentData: {current_data}")
            if current_data is not None:
                dictionary_list_id = current_data
                print(f"DEBUG: Ustawiono dictionary_list_id: {dictionary_list_id}")
            else:
                print("DEBUG: Brak wybranej listy słownikowej")
        
        self.add_column_to_tree(name, col_type, is_required, True, self.selected_color, dictionary_list_id)
        
        # Wyczyść pola
        self.new_column_name.clear()
        self.new_column_required.setChecked(False)
        # Reset koloru do białego
        self.selected_color = "#ffffff"
        self.color_btn.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc;")
    
    def has_time_column(self):
        """Sprawdza czy tabela ma kolumnę typu Godzina"""
        for i in range(self.columns_tree.topLevelItemCount()):
            item = self.columns_tree.topLevelItem(i)
            if item and item.data(0, Qt.ItemDataRole.UserRole) == "Godzina":
                return True
        return False
    
    def edit_selected_column(self):
        """Edytuje wybraną kolumnę"""
        selected_items = self.columns_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            # TODO: Implementacja edycji kolumny
            print(f"Edycja kolumny: {item.text(0)}")
    
    def remove_selected_column(self):
        """Usuwa wybraną kolumnę"""
        selected_items = self.columns_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            index = self.columns_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.columns_tree.takeTopLevelItem(index)
    
    def on_column_selection_changed(self):
        """Obsługuje zmianę zaznaczenia kolumny"""
        has_selection = bool(self.columns_tree.selectedItems())
        self.edit_column_btn.setEnabled(has_selection)
        self.remove_column_btn.setEnabled(has_selection)
    
    def toggle_dictionary_widgets(self, show):
        """Pokazuje/ukrywa pola listy słownikowej"""
        self.dictionary_label.setVisible(show)
        self.dictionary_combo.setVisible(show)
    
    def load_table_data(self):
        """Ładuje dane tabeli do edycji"""
        if self.table_data:
            try:
                print(f"DEBUG: Ładowanie danych tabeli do edycji: {self.table_data.get('name')}")
                
                # Załaduj podstawowe informacje
                self.name_edit.setText(self.table_data.get('name', ''))
                self.description_edit.setPlainText(self.table_data.get('description', ''))
                
                # Załaduj kolumny
                columns = self.table_data.get('columns', [])
                print(f"DEBUG: Ładowanie {len(columns)} kolumn")
                
                self.columns_tree.clear()
                for column in columns:
                    item = QTreeWidgetItem()
                    
                    # Ustaw dane dla kolumn
                    item.setText(0, column.get('name', 'Bez nazwy'))
                    item.setText(1, column.get('type', 'Tekstowa'))
                    item.setText(2, "Tak" if column.get('is_required') else "Nie")
                    item.setText(3, "Tak" if column.get('is_visible', True) else "Nie")
                    
                    # Zapisz pełne dane kolumny
                    item.setData(0, Qt.ItemDataRole.UserRole, column)
                    
                    self.columns_tree.addTopLevelItem(item)
                
                print(f"DEBUG: Załadowano {self.columns_tree.topLevelItemCount()} kolumn do drzewa")
                
                # Załaduj ustawienia tabeli (jeśli są dostępne)
                # Na razie używamy domyślnych wartości
                
            except Exception as e:
                print(f"DEBUG: Błąd podczas ładowania danych tabeli: {e}")
                import traceback
                traceback.print_exc()
    
    def load_dictionary_lists(self):
        """Ładuje prawdziwe listy słownikowe z bazy danych"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            db = Database()
            lists = db.get_dictionary_lists()
            
            # Wyczyść obecne elementy
            self.dictionary_combo.clear()
            
            # Dodaj prawdziwe listy
            for list_data in lists:
                self.dictionary_combo.addItem(
                    f"{list_data['name']} ({len(list_data['items'])} elementów)",
                    list_data['id']
                )
            
            # Dodaj opcję "Brak" na końcu
            self.dictionary_combo.addItem("-- Brak --", None)
            
            # Ustaw pierwszy element jako domyślny (jeśli są listy)
            if lists:
                self.dictionary_combo.setCurrentIndex(0)
                
            print(f"DEBUG: Załadowano {len(lists)} list słownikowych do combo")
            
        except Exception as e:
            print(f"DEBUG: Błąd podczas ładowania list słownikowych: {e}")
            # Fallback - dodaj przynajmniej opcję "Brak"
            self.dictionary_combo.clear()
            self.dictionary_combo.addItem("-- Brak --", None)
    
    def save_table(self):
        """Zapisuje tabelę"""
        print("DEBUG: Rozpoczęcie zapisywania tabeli...")
        
        # Walidacja
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Błąd", "Nazwa tabeli nie może być pusta!")
            return
        
        print("DEBUG: Walidacja przeszła pomyślnie...")
        
        # Zbieranie danych
        table_config = {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'rows_per_page': self.rows_per_page_spin.value(),
            'sortable': self.sortable_check.isChecked(),
            'filterable': self.filterable_check.isChecked(),
            'exportable': self.exportable_check.isChecked(),
            'editable': self.editable_check.isChecked(),
            'columns': []
        }
        
        print(f"DEBUG: Zbieranie konfiguracji dla tabeli: {table_config['name']}")
        
        # Zbieranie konfiguracji kolumn
        for i in range(self.columns_tree.topLevelItemCount()):
            item = self.columns_tree.topLevelItem(i)
            if item:
                column_name = item.text(0)
                column_type = item.data(0, Qt.ItemDataRole.UserRole)
                
                required_widget = self.columns_tree.itemWidget(item, 2)
                visible_widget = self.columns_tree.itemWidget(item, 3)
                
                # Rzutowanie na QCheckBox
                from PyQt6.QtWidgets import QCheckBox
                is_required = required_widget.isChecked() if isinstance(required_widget, QCheckBox) else False
                is_visible = visible_widget.isChecked() if isinstance(visible_widget, QCheckBox) else False
                
                # Specjalne ustawienia dla kolumny ID z operacjami matematycznymi
                settings = ""
                if column_name == "ID" and column_type == "Operacje matematyczne":
                    settings = "AUTOINCREMENT"  # Ustawienie autoinkrementowania
                
                # Pobierz kolor kolumny i dictionary_list_id
                column_color = item.data(1, Qt.ItemDataRole.UserRole) or "#ffffff"
                dictionary_list_id = item.data(2, Qt.ItemDataRole.UserRole)
                
                print(f"DEBUG: Kolumna '{column_name}' typu '{column_type}', dictionary_list_id: {dictionary_list_id}")
                
                table_config['columns'].append({
                    'name': column_name,
                    'type': column_type,
                    'required': is_required,
                    'visible': is_visible,
                    'settings': settings,
                    'color': column_color,
                    'dictionary_list_id': dictionary_list_id
                })
        
        print(f"DEBUG: Zebrano {len(table_config['columns'])} kolumn")
        
        # Zapisz konfigurację tabeli do bazy danych
        try:
            print("DEBUG: Próba zapisu do bazy danych...")
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            db = Database()
            print("DEBUG: Utworzono instancję Database")
            
            if self.is_edit_mode and self.table_data:
                # Tryb edycji - aktualizuj istniejącą tabelę
                table_id = self.table_data.get('id')
                if table_id:
                    print(f"DEBUG: Aktualizacja tabeli ID: {table_id}")
                    db.update_user_table(table_id, table_config)
                    QMessageBox.information(self, "Sukces", 
                        f"Tabela '{table_config['name']}' została zaktualizowana pomyślnie!")
                else:
                    QMessageBox.warning(self, "Błąd", "Nie można znaleźć ID tabeli do edycji!")
                    return
            else:
                # Tryb dodawania - utwórz nową tabelę
                table_id = db.create_user_table(table_config)
                print(f"DEBUG: Zapisano nową tabelę do bazy danych z ID: {table_id}")
                QMessageBox.information(self, "Sukces", 
                    f"Tabela '{table_config['name']}' została utworzona pomyślnie!")
            
            print("DEBUG: Zamykanie dialogu...")
            self.accept()
            
        except Exception as e:
            print(f"DEBUG: Błąd podczas zapisu: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Błąd", 
                f"Nie udało się utworzyć tabeli: {str(e)}")
            return
        
        self.accept()
    
    def choose_color(self):
        """Otwiera dialog wyboru koloru"""
        color = QColorDialog.getColor(QColor(self.selected_color), self, "Wybierz kolor kolumny")
        if color.isValid():
            self.selected_color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #ccc;")
    
    def on_column_type_changed(self, column_type):
        """Obsługuje zmianę typu kolumny"""
        # Pokaż/ukryj odpowiednie kontrolki w zależności od typu
        
        # Lista słownikowa
        is_list_type = column_type == "Lista"
        self.dictionary_label.setVisible(is_list_type)
        self.dictionary_combo.setVisible(is_list_type)
        
        # Konfiguracja formuły
        is_math_type = column_type == "Operacje matematyczne"
        self.formula_config_btn.setVisible(is_math_type)
    
    def open_formula_config(self):
        """Otwiera dialog konfiguracji formuły matematycznej"""
        from .math_column_dialog import MathColumnDialog
        
        # Sprawdź czy już mamy konfigurację dla tej kolumny
        current_config = getattr(self, '_current_formula_config', None)
        
        dialog = MathColumnDialog(self, current_config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Zapisz konfigurację
            self._current_formula_config = dialog.get_configuration()
            
            # Zaktualizuj nazwę kolumny jeśli została zmieniona
            config = self._current_formula_config
            if config and config.get('name'):
                self.new_column_name.setText(config['name'])
            
            print(f"Skonfigurowano formułę: {config}")

class ConfirmDeleteDialog(QDialog):
    """Dialog potwierdzenia usunięcia tabeli"""
    
    def __init__(self, parent=None, table_name=""):
        super().__init__(parent)
        self.setWindowTitle("Potwierdź usunięcie")
        self.setModal(True)
        self.setMinimumSize(400, 150)
        
        layout = QVBoxLayout(self)
        
        # Wiadomość
        message = QLabel(f"Czy na pewno chcesz usunąć tabelę '{table_name}'?\\n\\n"
                        "Ta operacja nie może być cofnięta.")
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Przyciski
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        delete_btn = QPushButton("Usuń")
        delete_btn.clicked.connect(self.accept)
        delete_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)