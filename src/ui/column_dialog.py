"""
Dialog do zarządzania kolumnami zadań
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, 
    QPushButton, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt


class ColumnDialog(QDialog):
    """Dialog do dodawania/edycji kolumn zadań"""
    
    def __init__(self, parent=None, column_data=None, theme_manager=None, db_manager=None):
        super().__init__(parent)
        self.column_data = column_data
        self.theme_manager = theme_manager
        self.db_manager = db_manager
        self.is_edit_mode = column_data is not None
        
        self.setup_ui()
        self.setup_connections()
        
        if self.is_edit_mode:
            self.load_column_data()
    
    def setup_ui(self):
        """Konfiguruje interfejs użytkownika"""
        self.setWindowTitle("Edycja kolumny" if self.is_edit_mode else "Nowa kolumna")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        
        # Główny layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Formularz
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Nazwa kolumny
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Wprowadź nazwę kolumny")
        form_layout.addRow("Nazwa kolumny:", self.name_edit)
        
        # Typ kolumny
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Tekstowa",
            "Lista", 
            "Waluta",
            "Alarm",
            "Liczbowa",
            "Czas trwania",
            "Data",
            "CheckBox"
        ])
        form_layout.addRow("Typ kolumny:", self.type_combo)
        
        # Lista słownikowa (tylko dla typu Lista)
        self.list_combo = QComboBox()
        self.list_combo.addItem("-- Wybierz listę --")
        
        # Załaduj listy słownikowe z bazy danych
        if self.db_manager:
            try:
                dictionary_lists = self.db_manager.get_dictionary_lists()
                for dict_list in dictionary_lists:
                    self.list_combo.addItem(dict_list['name'])
            except Exception as e:
                print(f"Błąd ładowania list słownikowych: {e}")
        
        self.list_combo.setVisible(False)
        form_layout.addRow("Lista słownikowa:", self.list_combo)
        
        # Opcje wyświetlania
        options_layout = QVBoxLayout()
        
        self.visible_check = QCheckBox("Widoczna w tabeli")
        self.visible_check.setChecked(True)
        options_layout.addWidget(self.visible_check)
        
        self.in_panel_check = QCheckBox("Dostępna w dolnym pasku")
        options_layout.addWidget(self.in_panel_check)
        
        form_layout.addRow("Opcje:", options_layout)
        
        layout.addLayout(form_layout)
        
        # Spacer
        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        
        # Przyciski
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Anuluj")
        self.save_button = QPushButton("Zapisz" if self.is_edit_mode else "Dodaj")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        
        # Zastosuj style
        if self.theme_manager:
            self.apply_theme()
    
    def apply_theme(self):
        """Stosuje motyw do dialogu"""
        try:
            # Style głównego dialogu
            self.setStyleSheet(self.theme_manager.get_dialog_style())
            
            # Style kontrolek
            self.name_edit.setStyleSheet(self.theme_manager.get_line_edit_style())
            self.type_combo.setStyleSheet(self.theme_manager.get_combo_style())
            self.list_combo.setStyleSheet(self.theme_manager.get_combo_style())
            self.visible_check.setStyleSheet(self.theme_manager.get_checkbox_style())
            self.in_panel_check.setStyleSheet(self.theme_manager.get_checkbox_style())
            
            # Style przycisków
            self.cancel_button.setStyleSheet(self.theme_manager.get_button_style())
            self.save_button.setStyleSheet(self.theme_manager.get_button_style())
            
        except Exception as e:
            print(f"Błąd stosowania motywu: {e}")
    
    def setup_connections(self):
        """Konfiguruje połączenia sygnałów"""
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.validate_and_accept)
    
    def on_type_changed(self, column_type):
        """Obsługuje zmianę typu kolumny"""
        # Pokaż/ukryj listę słownikową
        is_list_type = column_type == "Lista"
        self.list_combo.setVisible(is_list_type)
    
    def load_column_data(self):
        """Ładuje dane kolumny do edycji"""
        if not self.column_data:
            return
        
        try:
            self.name_edit.setText(self.column_data.get("name", ""))
            
            # Znajdź i ustaw typ
            type_text = self.column_data.get("type", "Tekstowa")
            index = self.type_combo.findText(type_text)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            
            # Ustaw opcje
            self.visible_check.setChecked(self.column_data.get("visible", True))
            self.in_panel_check.setChecked(self.column_data.get("in_panel", False))
            
            # Lista słownikowa
            if "list_name" in self.column_data:
                list_name = self.column_data["list_name"]
                index = self.list_combo.findText(list_name)
                if index >= 0:
                    self.list_combo.setCurrentIndex(index)
            
        except Exception as e:
            print(f"Błąd ładowania danych kolumny: {e}")
    
    def validate_and_accept(self):
        """Waliduje dane i zamyka dialog"""
        try:
            # Sprawdź nazwę
            name = self.name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Błąd", "Nazwa kolumny nie może być pusta")
                self.name_edit.setFocus()
                return
            
            # Sprawdź listę słownikową dla typu Lista
            if self.type_combo.currentText() == "Lista":
                if self.list_combo.currentIndex() <= 0:
                    QMessageBox.warning(self, "Błąd", "Wybierz listę słownikową dla typu 'Lista'")
                    self.list_combo.setFocus()
                    return
            
            # Sprawdź limit kolumn w panelu
            if self.in_panel_check.isChecked():
                # TODO: Sprawdź ile kolumn już jest w panelu
                pass
            
            self.accept()
            
        except Exception as e:
            print(f"Błąd walidacji: {e}")
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas walidacji: {e}")
    
    def get_column_data(self):
        """Zwraca dane kolumny"""
        data = {
            "name": self.name_edit.text().strip(),
            "type": self.type_combo.currentText(),
            "visible": self.visible_check.isChecked(),
            "in_panel": self.in_panel_check.isChecked(),
            "editable": True  # Kolumny niestandardowe są zawsze edytowalne
        }
        
        # Dodaj listę słownikową jeśli typ to Lista
        if data["type"] == "Lista" and self.list_combo.currentIndex() > 0:
            data["dictionary_list"] = self.list_combo.currentText()
        
        return data