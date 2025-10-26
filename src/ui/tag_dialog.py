"""
Dialog do zarządzania tagami z obsługą kolorów
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QColorDialog, QFrame,
                             QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class TagDialog(QDialog):
    """Dialog do dodawania/edycji tagów z obsługą kolorów"""
    
    def __init__(self, parent=None, tag_data=None, theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.selected_color = QColor("#3498db")  # Domyślny niebieski
        
        # Jeśli edytujemy istniejący tag
        if tag_data:
            self.tag_name = tag_data.get("name", "")
            self.selected_color = QColor(tag_data.get("color", "#3498db"))
            self.setWindowTitle("Edytuj tag")
        else:
            self.tag_name = ""
            self.setWindowTitle("Dodaj nowy tag")
        
        self.setModal(True)
        self.resize(350, 200)
        
        self.init_ui()
        
        # Zastosuj motyw
        if self.theme_manager:
            self.setStyleSheet(self.theme_manager.get_dialog_style())
    
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Formularz
        form_layout = QFormLayout()
        
        # Nazwa tagu
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.tag_name)
        self.name_edit.setPlaceholderText("Wprowadź nazwę tagu...")
        form_layout.addRow("Nazwa tagu:", self.name_edit)
        
        # Kolor tagu
        color_layout = QHBoxLayout()
        
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(50, 30)
        self.color_preview.setFrameStyle(QFrame.Shape.Box)
        self.color_preview.setStyleSheet(f"background-color: {self.selected_color.name()}; border: 1px solid #ccc;")
        color_layout.addWidget(self.color_preview)
        
        self.color_button = QPushButton("Wybierz kolor")
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        
        # Dodaj kilka predefiniowanych kolorów
        predefined_colors = ["#e74c3c", "#f39c12", "#f1c40f", "#2ecc71", "#3498db", "#9b59b6", "#34495e", "#95a5a6"]
        for i, color in enumerate(predefined_colors):
            color_btn = QPushButton()
            color_btn.setFixedSize(25, 25)
            color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc; border-radius: 3px;")
            color_btn.clicked.connect(lambda checked, c=color: self.set_predefined_color(c))
            color_layout.addWidget(color_btn)
        
        color_layout.addStretch()
        
        color_widget = QFrame()
        color_widget.setLayout(color_layout)
        form_layout.addRow("Kolor tagu:", color_widget)
        
        layout.addLayout(form_layout)
        
        # Separator
        layout.addSpacing(20)
        
        # Podgląd tagu
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Podgląd:")
        preview_label.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(preview_label)
        
        self.preview_tag = QLabel("Przykładowy tag")
        self.update_preview()
        preview_layout.addWidget(self.preview_tag)
        
        layout.addLayout(preview_layout)
        
        # Separator
        layout.addSpacing(20)
        
        # Przyciski akcji
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Zapisz")
        save_btn.clicked.connect(self.accept_tag)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Zastosuj style motywu
        if self.theme_manager:
            save_btn.setStyleSheet(self.theme_manager.get_primary_button_style())
            cancel_btn.setStyleSheet(self.theme_manager.get_button_style())
            self.color_button.setStyleSheet(self.theme_manager.get_button_style())
        
        # Połącz sygnały
        self.name_edit.textChanged.connect(self.update_preview)
    
    def choose_color(self):
        """Otwiera dialog wyboru koloru"""
        color = QColorDialog.getColor(self.selected_color, self, "Wybierz kolor tagu")
        if color.isValid():
            self.selected_color = color
            self.color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self.update_preview()
    
    def set_predefined_color(self, color_hex):
        """Ustawia predefiniowany kolor"""
        self.selected_color = QColor(color_hex)
        self.color_preview.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #ccc;")
        self.update_preview()
    
    def update_preview(self):
        """Aktualizuje podgląd tagu"""
        tag_text = self.name_edit.text() or "Przykładowy tag"
        
        # Oblicz kolor tekstu na podstawie jasności tła
        brightness = (self.selected_color.red() * 299 + 
                     self.selected_color.green() * 587 + 
                     self.selected_color.blue() * 114) / 1000
        text_color = "#000000" if brightness > 128 else "#ffffff"
        
        tag_style = f"""
            background-color: {self.selected_color.name()};
            color: {text_color};
            border: 1px solid {self.selected_color.darker(120).name()};
            border-radius: 12px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: bold;
        """
        
        self.preview_tag.setText(tag_text)
        self.preview_tag.setStyleSheet(tag_style)
        self.preview_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def accept_tag(self):
        """Sprawdza dane i akceptuje dialog"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Błąd", "Nazwa tagu nie może być pusta")
            return
        
        self.accept()
    
    def get_tag_data(self):
        """Zwraca dane tagu"""
        return {
            "name": self.name_edit.text().strip(),
            "color": self.selected_color.name()
        }