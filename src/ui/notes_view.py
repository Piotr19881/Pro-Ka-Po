import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QTreeWidget, QTreeWidgetItem,
                             QSplitter, QFrame, QMessageBox, QInputDialog,
                             QToolBar, QApplication, QDialog, QDialogButtonBox,
                             QLineEdit, QFormLayout, QColorDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QIcon, QTextCursor, QTextCharFormat, QColor, QAction

# Import bazy danych
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import Database


class NoteDialog(QDialog):
    """Dialog do tworzenia/edycji notatek"""
    
    def __init__(self, parent=None, title="", content="", note_id=None):
        super().__init__(parent)
        self.note_id = note_id
        self.init_ui()
        
        if title:
            self.title_edit.setText(title)
        if content:
            self.content_edit.setPlainText(content)
    
    def init_ui(self):
        self.setWindowTitle("Notatka")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Formularz
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Tytuł notatki...")
        form_layout.addRow("Tytuł:", self.title_edit)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Treść notatki...")
        form_layout.addRow("Treść:", self.content_edit)
        
        layout.addLayout(form_layout)
        
        # Przyciski
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_data(self):
        return {
            'title': self.title_edit.text().strip(),
            'content': self.content_edit.toPlainText(),
            'id': self.note_id
        }


class NotesView(QWidget):
    """Widok systemu notatek z zagnieżdżaniem"""
    
    # Sygnały
    note_created = pyqtSignal(dict)
    note_updated = pyqtSignal(dict)
    note_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None, theme_manager=None):
        super().__init__(parent)
        
        # ThemeManager
        self.theme_manager = theme_manager
        
        # Inicjalizuj bazę danych
        self.db = Database()
        
        # Stan aplikacji
        self.notes_data = {}  # Cache notatek {id: data}
        self.current_note_id = None
        
        self.init_ui()
        self.load_notes_from_database()
    
    def apply_theme(self):
        """Aplikuje motyw do widoku notatek"""
        if not self.theme_manager:
            return
            
        # Pobierz słownik aktualnego motywu
        theme_dict = self.theme_manager.get_current_theme_dict()
        
        # Główne tło widoku
        self.setStyleSheet(f"""
            NotesView {{
                background-color: {theme_dict['background']};
                color: {theme_dict['text']};
            }}
        """)
        
        # Zastosuj styl do wszystkich komponentów
        self._apply_theme_to_components(theme_dict)
    
    def _apply_theme_to_components(self, theme_dict):
        """Aplikuje motyw do wszystkich komponentów"""
        if not self.theme_manager:
            return
            
        # Lewa sekcja - drzewo notatek
        self.notes_tree.setStyleSheet(self.theme_manager.get_tree_style())
        
        # Nagłówek
        title_label_style = f"""
            color: {theme_dict['text']};
            padding: 10px;
            background-color: {theme_dict['header_background']};
            border-radius: 6px;
            border-left: 4px solid {theme_dict['accent']};
        """
        
        # Editor title
        editor_title_style = f"""
            color: {theme_dict['text']}; 
            padding: 15px 10px; 
            background-color: {theme_dict['header_background']};
            border-radius: 8px;
            border-left: 4px solid {theme_dict['accent']};
            margin-bottom: 10px;
        """
        
        # Text editor
        text_editor_style = f"""
            QTextEdit {{
                border: 2px solid {theme_dict['border']};
                border-radius: 8px;
                padding: 15px;
                font-family: "Segoe UI", "Calibri", Arial, sans-serif;
                font-size: 13px;
                line-height: 1.6;
                background-color: {theme_dict['input_background']};
                color: {theme_dict['text']};
                selection-background-color: {theme_dict['selection']};
            }}
            QTextEdit:focus {{
                border: 2px solid {theme_dict['accent']};
                background-color: {theme_dict['input_background']};
            }}
        """
        
        # Toolbar
        toolbar_style = f"""
            QWidget {{
                background-color: {theme_dict['secondary_background']};
                border-radius: 8px;
                border: 1px solid {theme_dict['border']};
            }}
        """
        
        # Tools label
        tools_label_style = f"""
            color: {theme_dict['text']}; 
            padding: 8px; 
            background-color: {theme_dict['header_background']};
            border-radius: 4px;
            margin-bottom: 5px;
        """
        
        # Przyciski
        button_style = self.theme_manager.get_button_style()
        
        # Separators
        separator_style = f"""
            QFrame {{
                color: {theme_dict['border']};
                background-color: {theme_dict['border']};
                height: 2px;
                margin: 5px 0;
            }}
        """
        
        # Formatowanie przycisków
        format_button_style = f"""
            QPushButton {{
                background-color: {theme_dict['secondary_background']};
                border: 2px solid {theme_dict['border']};
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                color: {theme_dict['text']};
            }}
            QPushButton:hover {{
                background-color: {theme_dict['hover']};
                border-color: {theme_dict['accent']};
            }}
            QPushButton:checked {{
                background-color: {theme_dict['accent']};
                color: {theme_dict['accent_text']};
                border-color: {theme_dict['accent']};
            }}
            QPushButton:pressed {{
                background-color: {theme_dict['pressed']};
            }}
        """
        
        # Aplikuj style
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(title_label_style)
        if hasattr(self, 'editor_title'):
            self.editor_title.setStyleSheet(editor_title_style)
        if hasattr(self, 'text_editor'):
            self.text_editor.setStyleSheet(text_editor_style)
        if hasattr(self, 'toolbar_widget'):
            self.toolbar_widget.setStyleSheet(toolbar_style)
        if hasattr(self, 'tools_label'):
            self.tools_label.setStyleSheet(tools_label_style)
        if hasattr(self, 'add_note_btn'):
            self.add_note_btn.setStyleSheet(button_style)
        if hasattr(self, 'nest_btn'):
            self.nest_btn.setStyleSheet(button_style)
            
        # Formatowanie przycisków
        for btn in [getattr(self, attr, None) for attr in ['bold_btn', 'italic_btn', 'underline_btn', 'clear_format_btn']]:
            if btn:
                btn.setStyleSheet(format_button_style)
                
        # Separatory
        for sep in [getattr(self, attr, None) for attr in ['separator', 'separator2']]:
            if sep:
                sep.setStyleSheet(separator_style)
        
        # Specjalne style dla przycisków kolorów
        if hasattr(self, 'text_color_btn'):
            self.text_color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme_dict['secondary_background']};
                    border: 2px solid {theme_dict['border']};
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11px;
                    color: #e74c3c;
                }}
            """)
            
        if hasattr(self, 'highlight_btn'):
            self.highlight_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #fff3cd;
                    border: 2px solid #ffd43b;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11px;
                }}
            """)
        
        # Widget containers
        for widget_attr in ['left_widget', 'right_widget']:
            widget = getattr(self, widget_attr, None)
            if widget:
                widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {theme_dict['secondary_background']};
                        border-radius: 10px;
                        border: 1px solid {theme_dict['border']};
                    }}
                """)
        
        # Splitter
        if hasattr(self, 'main_splitter'):
            self.main_splitter.setStyleSheet(f"""
                QSplitter::handle {{
                    background-color: {theme_dict['border']};
                    width: 3px;
                    margin: 2px 0;
                    border-radius: 1px;
                }}
                QSplitter::handle:hover {{
                    background-color: {theme_dict['accent']};
                }}
            """)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Główny splitter poziomy
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(True)
        
        # === LEWA SEKCJA - DRZEWO NOTATEK ===
        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Nagłówek z przyciskiem
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("📝 Notatki")
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.add_note_btn = QPushButton("+ Nowy notes")
        self.add_note_btn.clicked.connect(self.add_new_note)
        header_layout.addWidget(self.add_note_btn)
        
        left_layout.addLayout(header_layout)
        
        # Drzewo notatek
        self.notes_tree = QTreeWidget()
        self.notes_tree.setHeaderLabel("Struktura notatek")
        self.notes_tree.itemClicked.connect(self.on_note_selected)
        self.notes_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        
        left_layout.addWidget(self.notes_tree)
        
        # === PRAWA SEKCJA - EDYTOR ===
        self.right_widget = QWidget()
        right_layout = QHBoxLayout(self.right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Główne pole edycji
        editor_layout = QVBoxLayout()
        
        # Nagłówek edytora
        self.editor_title = QLabel("Wybierz notatkę")
        self.editor_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        editor_layout.addWidget(self.editor_title)
        
        # Pole tekstowe
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Wybierz notatkę z drzewa lub utwórz nową...")
        self.text_editor.textChanged.connect(self.on_text_changed)
        self.text_editor.selectionChanged.connect(self.on_selection_changed)
        
        editor_layout.addWidget(self.text_editor)
        right_layout.addLayout(editor_layout)
        
        # === PASEK NARZĘDZI ===
        self.toolbar_widget = QWidget()
        self.toolbar_widget.setMaximumWidth(70)
        toolbar_layout = QVBoxLayout(self.toolbar_widget)
        toolbar_layout.setContentsMargins(8, 5, 8, 5)
        toolbar_layout.setSpacing(8)
        
        # Tytuł paska narzędzi
        self.tools_label = QLabel("Narzędzia")
        self.tools_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.tools_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addWidget(self.tools_label)
        
        # Przycisk zagnieżdżenia (główny)
        self.nest_btn = QPushButton("↘")
        self.nest_btn.setToolTip("Utwórz zagnieżdżoną notatkę z zaznaczonego tekstu")
        self.nest_btn.setEnabled(False)
        self.nest_btn.setFixedSize(45, 35)
        self.nest_btn.clicked.connect(self.create_nested_note)
        toolbar_layout.addWidget(self.nest_btn)
        
        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        toolbar_layout.addWidget(self.separator)
        
        # Podstawowe narzędzia formatowania
        self.bold_btn = QPushButton("B")
        self.bold_btn.setToolTip("Pogrubienie")
        self.bold_btn.setFixedSize(45, 30)
        self.bold_btn.setCheckable(True)
        self.bold_btn.clicked.connect(self.toggle_bold)
        toolbar_layout.addWidget(self.bold_btn)
        
        self.italic_btn = QPushButton("I")
        self.italic_btn.setToolTip("Kursywa")
        self.italic_btn.setFixedSize(45, 30)
        self.italic_btn.setCheckable(True)
        self.italic_btn.clicked.connect(self.toggle_italic)
        toolbar_layout.addWidget(self.italic_btn)
        
        self.underline_btn = QPushButton("U")
        self.underline_btn.setToolTip("Podkreślenie")
        self.underline_btn.setFixedSize(45, 30)
        self.underline_btn.setCheckable(True)
        self.underline_btn.clicked.connect(self.toggle_underline)
        toolbar_layout.addWidget(self.underline_btn)
        
        # Separator
        self.separator2 = QFrame()
        self.separator2.setFrameShape(QFrame.Shape.HLine)
        toolbar_layout.addWidget(self.separator2)
        
        # Narzędzia kolorowania
        self.text_color_btn = QPushButton("A")
        self.text_color_btn.setToolTip("Kolor tekstu")
        self.text_color_btn.setFixedSize(45, 30)
        self.text_color_btn.clicked.connect(self.change_text_color)
        toolbar_layout.addWidget(self.text_color_btn)
        
        self.highlight_btn = QPushButton("🖍")
        self.highlight_btn.setToolTip("Zakreśl tekst")
        self.highlight_btn.setFixedSize(45, 30)
        self.highlight_btn.clicked.connect(self.highlight_text)
        toolbar_layout.addWidget(self.highlight_btn)
        
        self.clear_format_btn = QPushButton("⌫")
        self.clear_format_btn.setToolTip("Usuń formatowanie")
        self.clear_format_btn.setFixedSize(45, 30)
        self.clear_format_btn.clicked.connect(self.clear_formatting)
        toolbar_layout.addWidget(self.clear_format_btn)
        
        toolbar_layout.addStretch()
        right_layout.addWidget(self.toolbar_widget)
        
        # Dodanie sekcji do głównego splittera
        self.main_splitter.addWidget(self.left_widget)
        self.main_splitter.addWidget(self.right_widget)
        self.main_splitter.setStretchFactor(0, 1)  # Lewa sekcja
        self.main_splitter.setStretchFactor(1, 3)  # Prawa sekcja
        
        layout.addWidget(self.main_splitter)
        
        # Zastosuj motyw po inicjalizacji UI
        self.apply_theme()
    
    def load_notes_from_database(self):
        """Ładuje notatki z bazy danych"""
        try:
            db_notes = self.db.get_all_notes()
            
            # Konwertuj format bazy na format aplikacji
            self.notes_data = {}
            
            if not db_notes:
                # Jeśli baza jest pusta, dodaj przykładowe notatki
                self.create_sample_notes()
                return
            
            # Załaduj notatki z bazy
            for note in db_notes:
                self.notes_data[note['id']] = {
                    'title': note['title'],
                    'content': note['content'],
                    'parent_id': note['parent_id'],
                    'children': [],
                    'color': '#2c3e50'  # Domyślny kolor
                }
            
            # Buduj relacje dzieci
            for note_id, note_data in self.notes_data.items():
                if note_data['parent_id']:
                    parent_id = note_data['parent_id']
                    if parent_id in self.notes_data:
                        if 'children' not in self.notes_data[parent_id]:
                            self.notes_data[parent_id]['children'] = []
                        self.notes_data[parent_id]['children'].append(note_id)
            
            self.refresh_tree()
            print(f"Załadowano {len(self.notes_data)} notatek z bazy danych")
            
        except Exception as e:
            print(f"Błąd ładowania notatek: {e}")
            self.create_sample_notes()
    
    def create_sample_notes(self):
        """Tworzy przykładowe notatki w bazie"""
        try:
            # Dodaj główną notatkę
            main_id = self.db.add_note(
                title="Witaj w systemie notatek!",
                content="To jest główna notatka. Możesz zaznaczać tekst i tworzyć z niego zagnieżdżone notatki.\n\nSpróbuj zaznaczyć ten fragment i kliknij strzałkę!"
            )
            
            # Dodaj przykład zagnieżdżonej notatki
            child_id = self.db.add_note(
                title="Przykład zagnieżdżonej notatki",
                content="Ta notatka była utworzona z zaznaczonego tekstu w notatce nadrzędnej.",
                parent_id=main_id
            )
            
            # Przeładuj z bazy
            self.load_notes_from_database()
            
        except Exception as e:
            print(f"Błąd tworzenia przykładowych notatek: {e}")
    
    def refresh_tree(self):
        """Odświeża drzewo notatek"""
        self.notes_tree.clear()
        
        # Znajdź notatki główne (bez rodzica)
        root_notes = [note_id for note_id, data in self.notes_data.items() 
                     if data['parent_id'] is None]
        
        for note_id in root_notes:
            self.add_note_to_tree(note_id, None)
    
    def add_note_to_tree(self, note_id, parent_item):
        """Dodaje notatkę do drzewa rekurencyjnie"""
        if note_id not in self.notes_data:
            return
        
        note_data = self.notes_data[note_id]
        
        if parent_item:
            item = QTreeWidgetItem(parent_item)
        else:
            item = QTreeWidgetItem(self.notes_tree)
        
        item.setText(0, note_data['title'])
        item.setData(0, Qt.ItemDataRole.UserRole, note_id)
        
        # Dodaj ikony i ustaw kolor w zależności od poziomu
        note_color = note_data.get('color', '#e3f2fd')  # Domyślny jasny niebieski
        print(f"DEBUG: Ustawianie koloru dla notatki '{note_data['title']}': {note_color}")
        color = QColor(note_color)
        
        if note_data['parent_id'] is None:
            # Główna notatka - bardziej wyrazista
            item.setText(0, f"� {note_data['title']}")
            # Ustaw wyraziste kolorowe tło zamiast kolorów tekstu
            if self.theme_manager and self.theme_manager.current_theme == 'dark':
                item.setForeground(0, QColor('#ff6b6b'))  # Czerwony tekst w trybie ciemnym
            else:
                item.setForeground(0, QColor('#000000'))  # Czarny tekst w trybie jasnym
            # Dodaj kolorowe tło
            bg_color = QColor(note_color)
            bg_color.setAlpha(255)  # Pełna nieprzezroczystość!
            item.setBackground(0, bg_color)
            item.setData(0, Qt.ItemDataRole.BackgroundRole, bg_color)  # Alternatywna metoda
            print(f"DEBUG: Ustawiono kolor tła głównej notatki: {bg_color.name()}")
        else:
            # Podnotatka
            item.setText(0, f"📑 {note_data['title']}")
            # Ustaw kolorowe tło dla podnotatek
            if self.theme_manager and self.theme_manager.current_theme == 'dark':
                item.setForeground(0, QColor('#ff6b6b'))  # Czerwony tekst w trybie ciemnym
            else:
                item.setForeground(0, QColor('#000000'))  # Czarny tekst w trybie jasnym
            # Subtelniejsze tło dla podnotatek
            bg_color = QColor(note_color)
            bg_color.setAlpha(220)  # Prawie pełna nieprzezroczystość
            item.setBackground(0, bg_color)
            item.setData(0, Qt.ItemDataRole.BackgroundRole, bg_color)  # Alternatywna metoda
            print(f"DEBUG: Ustawiono kolor tła podnotatki: {bg_color.name()}")
        
        # Pogrub wszystkie notatki dla lepszej widoczności
        font = item.font(0)
        font.setBold(True)
        font.setPointSize(12)  # Większa czcionka
        item.setFont(0, font)
        
        # Dodaj dzieci rekurencyjnie
        for child_id in note_data.get('children', []):
            self.add_note_to_tree(child_id, item)
        
        item.setExpanded(True)
    
    def on_note_selected(self, item):
        """Obsługuje wybór notatki z drzewa"""
        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        if note_id and note_id in self.notes_data:
            self.current_note_id = note_id
            note_data = self.notes_data[note_id]
            
            # Zaktualizuj edytor
            self.editor_title.setText(note_data['title'])
            self.text_editor.blockSignals(True)  # Zablokuj sygnał textChanged
            self.text_editor.setPlainText(note_data['content'])
            self.text_editor.blockSignals(False)
            
            # Włącz edycję
            self.text_editor.setEnabled(True)
    
    def on_text_changed(self):
        """Obsługuje zmiany tekstu - automatyczny zapis do bazy"""
        if self.current_note_id and self.current_note_id in self.notes_data:
            content = self.text_editor.toPlainText()
            
            # Aktualizuj cache
            self.notes_data[self.current_note_id]['content'] = content
            
            # Zapisz do bazy z opóźnieniem (debounce)
            if not hasattr(self, '_save_timer'):
                from PyQt6.QtCore import QTimer
                self._save_timer = QTimer()
                self._save_timer.setSingleShot(True)
                self._save_timer.timeout.connect(self.save_current_note_to_db)
            
            self._save_timer.stop()
            self._save_timer.start(1000)  # Zapisz po 1 sekundzie bezczynności
    
    def save_current_note_to_db(self):
        """Zapisuje bieżącą notatkę do bazy danych"""
        if self.current_note_id and self.current_note_id in self.notes_data:
            try:
                note_data = self.notes_data[self.current_note_id]
                self.db.update_note(
                    self.current_note_id,
                    title=note_data['title'],
                    content=note_data['content']
                )
                print(f"Automatycznie zapisano notatkę: {note_data['title']}")
            except Exception as e:
                print(f"Błąd zapisu notatki: {e}")
    
    def on_selection_changed(self):
        """Obsługuje zmianę zaznaczenia tekstu"""
        cursor = self.text_editor.textCursor()
        has_selection = cursor.hasSelection()
        self.nest_btn.setEnabled(has_selection and self.current_note_id is not None)
    
    def add_new_note(self):
        """Dodaje nową główną notatkę"""
        dialog = NoteDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['title']:
                try:
                    # Zapisz do bazy
                    note_id = self.db.add_note(data['title'], data['content'])
                    
                    # Dodaj do cache
                    self.notes_data[note_id] = {
                        'title': data['title'],
                        'content': data['content'],
                        'parent_id': None,
                        'children': []
                    }
                    
                    self.refresh_tree()
                    self.note_created.emit(self.notes_data[note_id])
                    print(f"Dodano nową notatkę: {data['title']}")
                    
                except Exception as e:
                    QMessageBox.warning(self, "Błąd", f"Nie udało się dodać notatki: {e}")
    
    def create_nested_note(self):
        """Tworzy zagnieżdżoną notatkę z zaznaczonego tekstu"""
        if not self.current_note_id:
            return
        
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            QMessageBox.warning(self, "Brak zaznaczenia", 
                              "Najpierw zaznacz tekst, który ma stać się nową notatką.")
            return
        
        selected_text = cursor.selectedText()
        if not selected_text.strip():
            QMessageBox.warning(self, "Pusty tekst", "Zaznaczony tekst jest pusty.")
            return
        
        try:
            # Utwórz tytuł (skróć jeśli za długi)
            title = selected_text.strip()[:50] + ('...' if len(selected_text.strip()) > 50 else '')
            
            # Zapisz do bazy
            note_id = self.db.add_note(title, selected_text, self.current_note_id)
            
            # Dodaj do cache
            self.notes_data[note_id] = {
                'title': title,
                'content': selected_text,
                'parent_id': self.current_note_id,
                'children': [],
                'color': '#2c3e50'  # Domyślny kolor
            }
            
            # Dodaj do dzieci rodzica
            if 'children' not in self.notes_data[self.current_note_id]:
                self.notes_data[self.current_note_id]['children'] = []
            self.notes_data[self.current_note_id]['children'].append(note_id)
            
            # Zamień zaznaczony tekst na link
            link_text = f"→ {title}"
            cursor.insertText(link_text)
            
            # Zapisz zmiany w tekście macierzystym
            self.save_current_note_to_db()
            
            # Odśwież drzewo i wybierz nową notatkę
            self.refresh_tree()
            self.select_note_in_tree(note_id)
            
            QMessageBox.information(self, "Notatka utworzona", 
                                   f"Utworzono zagnieżdżoną notatkę: '{title}'")
            
            self.note_created.emit(self.notes_data[note_id])
            
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie udało się utworzyć notatki: {e}")
    
    def select_note_in_tree(self, note_id):
        """Wybiera notatkę w drzewie"""
        def find_item(item, target_id):
            if item.data(0, Qt.ItemDataRole.UserRole) == target_id:
                return item
            
            for i in range(item.childCount()):
                child = item.child(i)
                result = find_item(child, target_id)
                if result:
                    return result
            return None
        
        # Szukaj w elementach głównych
        for i in range(self.notes_tree.topLevelItemCount()):
            item = self.notes_tree.topLevelItem(i)
            found = find_item(item, note_id)
            if found:
                self.notes_tree.setCurrentItem(found)
                self.on_note_selected(found)
                break
    
    def show_tree_context_menu(self, position):
        """Pokazuje menu kontekstowe dla drzewa"""
        item = self.notes_tree.itemAt(position)
        if not item:
            return
        
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        
        # Styluj menu kontekstowe
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 2px solid #007ACC;
                border-radius: 8px;
                padding: 5px;
                font-size: 12px;
                color: #2c3e50;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 20px;
                border-radius: 4px;
                margin: 1px;
                color: #2c3e50;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
            QMenu::item:pressed {
                background-color: #bbdefb;
                color: #0d47a1;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 5px 10px;
            }
        """)
        
        edit_action = menu.addAction("✏️ Edytuj notatkę")
        color_action = menu.addAction("🎨 Zmień kolor")
        menu.addSeparator()
        add_child_action = menu.addAction("➕ Dodaj podnotatkę")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Usuń notatkę")
        
        action = menu.exec(self.notes_tree.mapToGlobal(position))
        
        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        
        if action == edit_action:
            self.edit_note(note_id)
        elif action == color_action:
            self.change_note_color(note_id)
        elif action == delete_action:
            self.delete_note(note_id)
        elif action == add_child_action:
            self.add_child_note(note_id)
    
    def edit_note(self, note_id):
        """Edytuje notatkę"""
        if note_id not in self.notes_data:
            return
        
        note_data = self.notes_data[note_id]
        dialog = NoteDialog(self, note_data['title'], note_data['content'], note_id)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['title']:
                try:
                    # Aktualizuj w bazie
                    self.db.update_note(note_id, data['title'], data['content'])
                    
                    # Aktualizuj cache
                    self.notes_data[note_id]['title'] = data['title']
                    self.notes_data[note_id]['content'] = data['content']
                    
                    self.refresh_tree()
                    if self.current_note_id == note_id:
                        self.editor_title.setText(data['title'])
                        self.text_editor.blockSignals(True)
                        self.text_editor.setPlainText(data['content'])
                        self.text_editor.blockSignals(False)
                    
                    self.note_updated.emit(self.notes_data[note_id])
                    print(f"Zaktualizowano notatkę: {data['title']}")
                    
                except Exception as e:
                    QMessageBox.warning(self, "Błąd", f"Nie udało się zaktualizować notatki: {e}")
    
    def delete_note(self, note_id):
        """Usuwa notatkę"""
        if note_id not in self.notes_data:
            return
        
        note_data = self.notes_data[note_id]
        
        # Sprawdź czy ma dzieci
        if note_data.get('children'):
            reply = QMessageBox.question(
                self, "Usuwanie notatki",
                f"Notatka '{note_data['title']}' ma {len(note_data['children'])} podnotatek.\n"
                "Czy na pewno chcesz ją usunąć wraz z wszystkimi podnotatkami?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        try:
            # Usuń z bazy (CASCADE automatycznie usuwa podnotatki)
            self.db.delete_note(note_id)
            
            # Usuń z rodzica w cache
            if note_data['parent_id'] and note_data['parent_id'] in self.notes_data:
                parent = self.notes_data[note_data['parent_id']]
                if note_id in parent['children']:
                    parent['children'].remove(note_id)
            
            # Usuń z cache rekurencyjnie
            self.delete_note_from_cache(note_id)
            
            # Wyczyść edytor jeśli usuwana notatka była wybrana
            if self.current_note_id == note_id:
                self.current_note_id = None
                self.editor_title.setText("Wybierz notatkę")
                self.text_editor.clear()
                self.text_editor.setEnabled(False)
            
            self.refresh_tree()
            self.note_deleted.emit(note_id)
            print(f"Usunięto notatkę: {note_data['title']}")
            
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie udało się usunąć notatki: {e}")
    
    def delete_note_from_cache(self, note_id):
        """Usuwa notatkę z cache rekurencyjnie"""
        if note_id not in self.notes_data:
            return
        
        note_data = self.notes_data[note_id]
        
        # Usuń dzieci
        for child_id in note_data.get('children', []):
            self.delete_note_from_cache(child_id)
        
        # Usuń samą notatkę
        del self.notes_data[note_id]
    
    def add_child_note(self, parent_id):
        """Dodaje podnotatkę"""
        dialog = NoteDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['title']:
                try:
                    # Zapisz do bazy
                    note_id = self.db.add_note(data['title'], data['content'], parent_id)
                    
                    # Dodaj do cache
                    self.notes_data[note_id] = {
                        'title': data['title'],
                        'content': data['content'],
                        'parent_id': parent_id,
                        'children': [],
                        'color': '#2c3e50'  # Domyślny kolor
                    }
                    
                    # Dodaj do dzieci rodzica
                    if 'children' not in self.notes_data[parent_id]:
                        self.notes_data[parent_id]['children'] = []
                    self.notes_data[parent_id]['children'].append(note_id)
                    
                    self.refresh_tree()
                    self.note_created.emit(self.notes_data[note_id])
                    print(f"Dodano podnotatkę: {data['title']}")
                    
                except Exception as e:
                    QMessageBox.warning(self, "Błąd", f"Nie udało się dodać podnotatki: {e}")
    
    def change_note_color(self, note_id):
        """Zmienia kolor notatki w drzewie"""
        if note_id not in self.notes_data:
            return
        
        current_color = self.notes_data[note_id].get('color', '#e3f2fd')
        
        # Pokaż dialog wyboru koloru z predefiniowanymi opcjami
        color_dialog = QColorDialog(QColor(current_color), self)
        color_dialog.setWindowTitle("Wybierz kolor notatki")
        
        # Dodaj predefiniowane kolory - bardziej wyraziste
        predefined_colors = [
            "#2c3e50",  # Ciemny szary (domyślny)
            "#e74c3c",  # Jasny czerwony
            "#e67e22",  # Pomarańczowy
            "#f1c40f",  # Żółty
            "#27ae60",  # Jasny zielony
            "#3498db",  # Jasny niebieski
            "#9b59b6",  # Jasny fioletowy
            "#e91e63",  # Różowy
            "#00bcd4",  # Cyjan
            "#ff5722",  # Ciemnorodzowy
            "#4caf50",  # Zielony
            "#2196f3",  # Błękitny
            "#ff9800",  # Amber
            "#795548",  # Brązowy
            "#607d8b",  # Niebiesko-szary
            "#9c27b0"   # Purpurowy
        ]
        
        for i, color_hex in enumerate(predefined_colors):
            color_dialog.setCustomColor(i, QColor(color_hex))
        
        if color_dialog.exec() == QDialog.DialogCode.Accepted:
            selected_color = color_dialog.selectedColor()
            if selected_color.isValid():
                color_hex = selected_color.name()
                
                # Aktualizuj kolor w cache
                self.notes_data[note_id]['color'] = color_hex
                
                # Odśwież drzewo żeby pokazać nowy kolor
                self.refresh_tree()
                
                # Wymuś odświeżenie wizualne
                self.notes_tree.repaint()
                self.notes_tree.update()
                
                # TODO: Zapisz kolor do bazy danych (rozszerzenie tabeli)
                print(f"Zmieniono kolor notatki '{self.notes_data[note_id]['title']}' na: {color_hex}")
    
    # Funkcje formatowania tekstu
    def toggle_bold(self):
        """Przełącza pogrubienie"""
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        if format.fontWeight() == QFont.Weight.Bold:
            format.setFontWeight(QFont.Weight.Normal)
        else:
            format.setFontWeight(QFont.Weight.Bold)
        cursor.setCharFormat(format)
        self.text_editor.setTextCursor(cursor)
    
    def toggle_italic(self):
        """Przełącza kursywę"""
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        format.setFontItalic(not format.fontItalic())
        cursor.setCharFormat(format)
        self.text_editor.setTextCursor(cursor)
    
    def toggle_underline(self):
        """Przełącza podkreślenie"""
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        format.setFontUnderline(not format.fontUnderline())
        cursor.setCharFormat(format)
        self.text_editor.setTextCursor(cursor)
    
    def change_text_color(self):
        """Zmienia kolor tekstu"""
        color = QColorDialog.getColor(QColor("#000000"), self, "Wybierz kolor tekstu")
        if color.isValid():
            cursor = self.text_editor.textCursor()
            if cursor.hasSelection():
                format = cursor.charFormat()
                format.setForeground(color)
                cursor.setCharFormat(format)
                self.text_editor.setTextCursor(cursor)
            else:
                # Jeśli nic nie zaznaczono, ustaw kolor dla następnego tekstu
                format = self.text_editor.currentCharFormat()
                format.setForeground(color)
                self.text_editor.setCurrentCharFormat(format)
    
    def highlight_text(self):
        """Zakreśla tekst kolorem"""
        color = QColorDialog.getColor(QColor("#ffff00"), self, "Wybierz kolor zakreślenia")
        if color.isValid():
            cursor = self.text_editor.textCursor()
            if cursor.hasSelection():
                format = cursor.charFormat()
                format.setBackground(color)
                cursor.setCharFormat(format)
                self.text_editor.setTextCursor(cursor)
            else:
                QMessageBox.information(self, "Zakreślanie", 
                                      "Najpierw zaznacz tekst, który chcesz zakreślić.")
    
    def clear_formatting(self):
        """Usuwa formatowanie z zaznaczonego tekstu"""
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            cursor.setCharFormat(format)
            self.text_editor.setTextCursor(cursor)
        else:
            QMessageBox.information(self, "Usuwanie formatowania", 
                                  "Zaznacz tekst, z którego chcesz usunąć formatowanie.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    notes_view = NotesView()
    notes_view.show()
    sys.exit(app.exec())