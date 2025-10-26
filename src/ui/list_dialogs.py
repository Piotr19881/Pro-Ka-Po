"""
Dialogi do zarządzania listami słownikowymi w aplikacji Pro-Ka-Po V2
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel, 
                             QGroupBox, QCheckBox, QComboBox, QListWidget,
                             QListWidgetItem, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt

class ListDialog(QDialog):
    """Dialog do dodawania/edycji list słownikowych"""
    
    def __init__(self, parent=None, list_data=None, theme_manager=None, context="table"):
        super().__init__(parent)
        self.list_data = list_data
        self.theme_manager = theme_manager
        self.context = context  # "table" dla list tabel, "task" dla list zadań
        self.is_edit_mode = list_data is not None
        
        # Dostosuj tytuł do kontekstu
        if self.context == "task":
            title = "Edytuj listę zadań" if self.is_edit_mode else "Dodaj nową listę zadań"
        else:
            title = "Edytuj listę" if self.is_edit_mode else "Dodaj nową listę"
            
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 600)
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_list_data()
    
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Podstawowe informacje o liście
        self.create_basic_info_section(layout)
        
        # Elementy listy
        self.create_items_section(layout)
        
        # Ustawienia listy
        self.create_settings_section(layout)
        
        # Przyciski akcji
        self.create_buttons_section(layout)
    
    def create_basic_info_section(self, parent_layout):
        """Tworzy sekcję podstawowych informacji"""
        basic_group = QGroupBox("Podstawowe informacje")
        form_layout = QFormLayout(basic_group)
        
        # Nazwa listy
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Wprowadź nazwę listy...")
        form_layout.addRow("Nazwa listy:", self.name_edit)
        
        # Opis listy
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("Opis listy (opcjonalnie)...")
        form_layout.addRow("Opis:", self.description_edit)
        
        # Typ listy
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Statusy", "Priorytety", "Kategorie", "Działy", 
            "Typy", "Role", "Lokalizacje", "Inne"
        ])
        form_layout.addRow("Typ listy:", self.type_combo)
        
        parent_layout.addWidget(basic_group)
    
    def create_items_section(self, parent_layout):
        """Tworzy sekcję elementów listy"""
        items_group = QGroupBox("Elementy listy")
        items_layout = QVBoxLayout(items_group)
        
        # Informacja
        info_label = QLabel("Dodaj elementy, które będą dostępne w tej liście:")
        if self.theme_manager:
            info_label.setStyleSheet(self.theme_manager.get_info_label_style())
        else:
            info_label.setStyleSheet("color: #666; font-style: italic;")
        items_layout.addWidget(info_label)
        
        # Lista elementów
        self.items_list = QListWidget()
        self.items_list.setMinimumHeight(200)
        
        # Dodaj przykładowe elementy zależnie od typu
        self.add_sample_items()
        
        items_layout.addWidget(self.items_list)
        
        # Przyciski zarządzania elementami
        items_buttons_layout = QHBoxLayout()
        
        self.add_item_btn = QPushButton("Dodaj element")
        self.add_item_btn.clicked.connect(self.add_list_item)
        items_buttons_layout.addWidget(self.add_item_btn)
        
        self.edit_item_btn = QPushButton("Edytuj element")
        self.edit_item_btn.clicked.connect(self.edit_selected_item)
        items_buttons_layout.addWidget(self.edit_item_btn)
        
        self.remove_item_btn = QPushButton("Usuń element")
        self.remove_item_btn.clicked.connect(self.remove_selected_item)
        items_buttons_layout.addWidget(self.remove_item_btn)
        
        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.setMaximumWidth(30)
        self.move_up_btn.clicked.connect(self.move_item_up)
        items_buttons_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.setMaximumWidth(30)
        self.move_down_btn.clicked.connect(self.move_item_down)
        items_buttons_layout.addWidget(self.move_down_btn)
        
        items_buttons_layout.addStretch()
        items_layout.addLayout(items_buttons_layout)
        
        # Podłącz sygnały
        self.items_list.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        parent_layout.addWidget(items_group)
    
    def create_settings_section(self, parent_layout):
        """Tworzy sekcję ustawień listy"""
        settings_group = QGroupBox("Ustawienia listy")
        settings_layout = QVBoxLayout(settings_group)
        
        # Opcje listy
        self.allow_custom_check = QCheckBox("Pozwól użytkownikom dodawać własne elementy")
        settings_layout.addWidget(self.allow_custom_check)
        
        self.allow_multiple_check = QCheckBox("Pozwól na wybór wielu elementów")
        settings_layout.addWidget(self.allow_multiple_check)
        
        self.required_check = QCheckBox("Wymagaj wyboru z listy")
        self.required_check.setChecked(True)
        settings_layout.addWidget(self.required_check)
        
        self.case_sensitive_check = QCheckBox("Rozróżniaj wielkość liter")
        settings_layout.addWidget(self.case_sensitive_check)
        
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
        save_text = "Zaktualizuj" if self.is_edit_mode else "Utwórz listę"
        self.save_btn = QPushButton(save_text)
        self.save_btn.clicked.connect(self.save_list)
        self.save_btn.setDefault(True)
        buttons_layout.addWidget(self.save_btn)
        
        parent_layout.addLayout(buttons_layout)
    
    def add_sample_items(self):
        """Dodaje przykładowe elementy do listy"""
        if self.context == "task":
            # Przykładowe elementy dla kontekstu zadań
            sample_items = {
                "Statusy": ["Do zrobienia", "W trakcie", "Gotowe", "Anulowane", "Wstrzymane"],
                "Priorytety": ["Niski", "Normalny", "Wysoki", "Krytyczny"],
                "Kategorie": ["Praca", "Osobiste", "Projekt", "Spotkanie", "Nauka"],
                "Działy": ["Frontend", "Backend", "Design", "QA", "Marketing", "Sprzedaż"],
                "Typy": ["Bug", "Feature", "Improvement", "Task"],
                "Role": ["Developer", "Tester", "Designer", "Manager", "Client"],
                "Lokalizacje": ["Biuro", "Zdalnie", "Klient", "Sala konferencyjna"],
                "Inne": ["Zadanie 1", "Zadanie 2", "Zadanie 3"]
            }
        else:
            # Przykładowe elementy dla kontekstu tabel
            sample_items = {
                "Statusy": ["Aktywny", "Nieaktywny", "Oczekujący", "Zablokowany"],
                "Priorytety": ["Niski", "Średni", "Wysoki", "Krytyczny"],
                "Kategorie": ["Ogólne", "Pilne", "Projekty", "Administracja"],
                "Działy": ["IT", "Marketing", "Sprzedaż", "HR", "Finanse"],
                "Typy": ["Typ A", "Typ B", "Typ C"],
                "Role": ["Administrator", "Użytkownik", "Gość", "Moderator"],
                "Lokalizacje": ["Warszawa", "Kraków", "Gdańsk", "Wrocław"],
                "Inne": ["Element 1", "Element 2", "Element 3"]
            }
        
        current_type = self.type_combo.currentText()
        items = sample_items.get(current_type, ["Element 1", "Element 2"])
        
        for item_text in items:
            self.items_list.addItem(item_text)
    
    def on_type_changed(self, new_type):
        """Obsługuje zmianę typu listy"""
        # Wyczyść aktualną listę
        self.items_list.clear()
        # Dodaj nowe przykładowe elementy
        self.add_sample_items()
    
    def add_list_item(self):
        """Dodaje nowy element do listy"""
        item_text, ok = QInputDialog.getText(
            self, "Dodaj element", "Nazwa elementu:"
        )
        
        if ok and item_text.strip():
            self.items_list.addItem(item_text.strip())
    
    def edit_selected_item(self):
        """Edytuje zaznaczony element"""
        current_item = self.items_list.currentItem()
        if current_item:
            current_text = current_item.text()
            new_text, ok = QInputDialog.getText(
                self, "Edytuj element", "Nazwa elementu:", text=current_text
            )
            
            if ok and new_text.strip():
                current_item.setText(new_text.strip())
    
    def remove_selected_item(self):
        """Usuwa zaznaczony element"""
        current_item = self.items_list.currentItem()
        if current_item:
            row = self.items_list.row(current_item)
            self.items_list.takeItem(row)
    
    def move_item_up(self):
        """Przesuwa element w górę"""
        current_row = self.items_list.currentRow()
        if current_row > 0:
            item = self.items_list.takeItem(current_row)
            self.items_list.insertItem(current_row - 1, item)
            self.items_list.setCurrentRow(current_row - 1)
    
    def move_item_down(self):
        """Przesuwa element w dół"""
        current_row = self.items_list.currentRow()
        if current_row < self.items_list.count() - 1:
            item = self.items_list.takeItem(current_row)
            self.items_list.insertItem(current_row + 1, item)
            self.items_list.setCurrentRow(current_row + 1)
    
    def on_item_selection_changed(self):
        """Obsługuje zmianę zaznaczenia elementu"""
        has_selection = bool(self.items_list.selectedItems())
        current_row = self.items_list.currentRow()
        
        self.edit_item_btn.setEnabled(has_selection)
        self.remove_item_btn.setEnabled(has_selection)
        self.move_up_btn.setEnabled(has_selection and current_row > 0)
        self.move_down_btn.setEnabled(has_selection and current_row < self.items_list.count() - 1)
    
    def load_list_data(self):
        """Ładuje dane listy do edycji"""
        if not self.list_data:
            return
            
        # Załaduj podstawowe informacje
        if 'name' in self.list_data:
            self.name_edit.setText(self.list_data['name'])
        
        if 'description' in self.list_data:
            self.description_edit.setPlainText(self.list_data['description'])
        
        if 'type' in self.list_data:
            # Znajdź i ustaw odpowiedni typ w combo
            index = self.type_combo.findText(self.list_data['type'])
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        
        # Załaduj elementy listy
        if 'items' in self.list_data and isinstance(self.list_data['items'], list):
            self.items_list.clear()
            for item in self.list_data['items']:
                if isinstance(item, str):
                    self.items_list.addItem(item)
                elif isinstance(item, dict) and 'text' in item:
                    self.items_list.addItem(item['text'])
        
        # Załaduj ustawienia checkboxów
        if 'allow_custom' in self.list_data:
            self.allow_custom_check.setChecked(bool(self.list_data['allow_custom']))
        
        if 'allow_multiple' in self.list_data:
            self.allow_multiple_check.setChecked(bool(self.list_data['allow_multiple']))
        elif 'multiple_selection' in self.list_data:
            self.allow_multiple_check.setChecked(bool(self.list_data['multiple_selection']))
        
        if 'required' in self.list_data:
            self.required_check.setChecked(bool(self.list_data['required']))
        
        if 'case_sensitive' in self.list_data:
            self.case_sensitive_check.setChecked(bool(self.list_data['case_sensitive']))
    
    def save_list(self):
        """Zapisuje listę"""
        # Walidacja
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Błąd", "Nazwa listy nie może być pusta!")
            return
        
        if self.items_list.count() == 0:
            QMessageBox.warning(self, "Błąd", "Lista musi zawierać przynajmniej jeden element!")
            return
        
        # Zbieranie danych
        list_config = {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'type': self.type_combo.currentText(),
            'allow_custom': self.allow_custom_check.isChecked(),
            'multiple_selection': self.allow_multiple_check.isChecked(),  # Zmienione z allow_multiple
            'required': self.required_check.isChecked(),
            'case_sensitive': self.case_sensitive_check.isChecked(),
            'items': []
        }
        
        # Zbieranie elementów listy
        for i in range(self.items_list.count()):
            item = self.items_list.item(i)
            if item:
                list_config['items'].append(item.text())
        
        # Zapisz konfigurację listy do bazy danych
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database.db_manager import Database
            
            db = Database()
            
            if self.is_edit_mode and self.list_data:
                # Tryb edycji - TODO: dodać metodę update_dictionary_list
                QMessageBox.information(self, "Info", "Edycja list nie jest jeszcze zaimplementowana!")
                return
            else:
                # Tryb dodawania - utwórz nową listę
                list_id = db.create_dictionary_list(list_config)
                print(f"Zapisano listę do bazy danych z ID: {list_id}")
                QMessageBox.information(self, "Sukces", 
                    f"Lista '{list_config['name']}' została utworzona pomyślnie!")
            
        except Exception as e:
            print(f"Błąd podczas zapisywania listy: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Błąd", f"Błąd podczas zapisywania listy: {e}")
            return
        
        print(f"Zapisano listę: {list_config}")
        
        self.accept()
    
    def get_list_data(self):
        """Zwraca dane listy z dialogu"""
        items = []
        for i in range(self.items_list.count()):
            items.append(self.items_list.item(i).text())
        
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'type': self.type_combo.currentText(),
            'items': items,
            'allow_custom': self.allow_custom_check.isChecked(),
            'allow_multiple': self.allow_multiple_check.isChecked(),
            'required': self.required_check.isChecked(),
            'case_sensitive': self.case_sensitive_check.isChecked(),
            'context': self.context  # Dodajemy informację o kontekście
        }

class ConfirmDeleteListDialog(QDialog):
    """Dialog potwierdzenia usunięcia listy"""
    
    def __init__(self, parent=None, list_name="", theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowTitle("Potwierdź usunięcie")
        self.setModal(True)
        self.setMinimumSize(400, 150)
        
        layout = QVBoxLayout(self)
        
        # Wiadomość
        message = QLabel(f"Czy na pewno chcesz usunąć listę '{list_name}'?\\n\\n"
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
        if self.theme_manager:
            delete_btn.setStyleSheet(self.theme_manager.get_danger_button_style())
        else:
            delete_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)