"""
Dialog do edycji zawartości list zadań
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QListWidget, QInputDialog, QMessageBox,
                             QListWidgetItem)
from PyQt6.QtCore import Qt

class TaskListContentDialog(QDialog):
    """Dialog do zarządzania zawartością listy zadań"""
    
    def __init__(self, parent=None, list_name="", theme_manager=None):
        super().__init__(parent)
        self.list_name = list_name
        self.theme_manager = theme_manager
        self.list_content = []
        
        self.setWindowTitle(f"Edycja zawartości listy: {list_name}")
        self.setModal(True)
        self.resize(400, 500)
        
        self.init_ui()
        self.load_list_content()
        
        # Zastosuj motyw
        if self.theme_manager:
            self.setStyleSheet(self.theme_manager.get_dialog_style())
    
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Nagłówek
        header_label = QLabel(f"Zawartość listy: {self.list_name}")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header_label)
        
        # Lista elementów
        self.content_list = QListWidget()
        self.content_list.setMinimumHeight(300)
        layout.addWidget(self.content_list)
        
        # Przyciski zarządzania zawartością
        content_buttons_layout = QHBoxLayout()
        
        add_item_btn = QPushButton("Dodaj element")
        add_item_btn.clicked.connect(self.add_list_item)
        content_buttons_layout.addWidget(add_item_btn)
        
        edit_item_btn = QPushButton("Edytuj element")
        edit_item_btn.clicked.connect(self.edit_list_item)
        content_buttons_layout.addWidget(edit_item_btn)
        
        delete_item_btn = QPushButton("Usuń element")
        delete_item_btn.clicked.connect(self.delete_list_item)
        content_buttons_layout.addWidget(delete_item_btn)
        
        content_buttons_layout.addStretch()
        layout.addLayout(content_buttons_layout)
        
        # Przyciski sterowania pozycją
        position_buttons_layout = QHBoxLayout()
        
        move_up_btn = QPushButton("↑ W górę")
        move_up_btn.clicked.connect(self.move_item_up)
        position_buttons_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("↓ W dół")
        move_down_btn.clicked.connect(self.move_item_down)
        position_buttons_layout.addWidget(move_down_btn)
        
        position_buttons_layout.addStretch()
        layout.addLayout(position_buttons_layout)
        
        # Separator
        layout.addSpacing(20)
        
        # Przyciski akcji
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Zapisz")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Zastosuj style motywu do przycisków
        if self.theme_manager:
            save_btn.setStyleSheet(self.theme_manager.get_primary_button_style())
            cancel_btn.setStyleSheet(self.theme_manager.get_secondary_button_style())
    
    def load_list_content(self):
        """Ładuje zawartość listy"""
        try:
            # TODO: Załaduj rzeczywistą zawartość z bazy danych
            # Na razie używamy przykładowych danych
            sample_content = {
                "Status zadań": ["Do zrobienia", "W trakcie", "Gotowe", "Anulowane"],
                "Priorytety": ["Niski", "Normalny", "Wysoki", "Krytyczny"],
                "Kategorie": ["Praca", "Osobiste", "Projekt", "Spotkanie"],
                "Zespoły": ["Frontend", "Backend", "Design", "QA", "Marketing"]
            }
            
            content = sample_content.get(self.list_name, [])
            
            self.content_list.clear()
            for item in content:
                self.content_list.addItem(item)
                
        except Exception as e:
            print(f"Błąd ładowania zawartości listy: {e}")
    
    def add_list_item(self):
        """Dodaje nowy element do listy"""
        try:
            item_text, ok = QInputDialog.getText(
                self, 
                "Nowy element", 
                "Wprowadź tekst elementu:"
            )
            
            if ok and item_text.strip():
                self.content_list.addItem(item_text.strip())
                
        except Exception as e:
            print(f"Błąd dodawania elementu: {e}")
    
    def edit_list_item(self):
        """Edytuje wybrany element listy"""
        try:
            current_item = self.content_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uwaga", "Wybierz element do edycji")
                return
            
            old_text = current_item.text()
            new_text, ok = QInputDialog.getText(
                self, 
                "Edytuj element", 
                "Wprowadź nowy tekst elementu:", 
                text=old_text
            )
            
            if ok and new_text.strip():
                current_item.setText(new_text.strip())
                
        except Exception as e:
            print(f"Błąd edycji elementu: {e}")
    
    def delete_list_item(self):
        """Usuwa wybrany element z listy"""
        try:
            current_item = self.content_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uwaga", "Wybierz element do usunięcia")
                return
            
            item_text = current_item.text()
            reply = QMessageBox.question(
                self,
                "Potwierdź usunięcie",
                f"Czy na pewno chcesz usunąć element '{item_text}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.content_list.takeItem(self.content_list.row(current_item))
                
        except Exception as e:
            print(f"Błąd usuwania elementu: {e}")
    
    def move_item_up(self):
        """Przesuwa element w górę"""
        try:
            current_row = self.content_list.currentRow()
            if current_row <= 0:
                return
            
            item = self.content_list.takeItem(current_row)
            self.content_list.insertItem(current_row - 1, item)
            self.content_list.setCurrentRow(current_row - 1)
            
        except Exception as e:
            print(f"Błąd przesuwania elementu: {e}")
    
    def move_item_down(self):
        """Przesuwa element w dół"""
        try:
            current_row = self.content_list.currentRow()
            if current_row < 0 or current_row >= self.content_list.count() - 1:
                return
            
            item = self.content_list.takeItem(current_row)
            self.content_list.insertItem(current_row + 1, item)
            self.content_list.setCurrentRow(current_row + 1)
            
        except Exception as e:
            print(f"Błąd przesuwania elementu: {e}")
    
    def get_list_content(self):
        """Zwraca zawartość listy jako listę stringów"""
        content = []
        for i in range(self.content_list.count()):
            item = self.content_list.item(i)
            if item:
                content.append(item.text())
        return content