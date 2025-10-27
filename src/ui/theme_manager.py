"""
System zarządzania motywami aplikacji
"""

class ThemeManager:
    """Zarządza stylami jasnym i ciemnym dla całej aplikacji"""
    
    def __init__(self):
        self.current_theme = 'light'
        self._style_cache = {}  # Cache dla wygenerowanych stylów
        self._cache_version = 0  # Wersja cache do invalidacji
    
    def _cache_key(self, style_name):
        """Generuje klucz cache dla stylu"""
        return f"{style_name}_{self.current_theme}_{self._cache_version}"
    
    def _get_cached_style(self, style_name, generator_func):
        """Pobiera styl z cache lub generuje nowy"""
        cache_key = self._cache_key(style_name)
        if cache_key not in self._style_cache:
            self._style_cache[cache_key] = generator_func()
        return self._style_cache[cache_key]
    
    def _invalidate_cache(self):
        """Invaliduje cache stylów przy zmianie motywu"""
        self._cache_version += 1
        self._style_cache.clear()
    
    def set_theme(self, theme_name):
        """Ustawia aktywny motyw"""
        new_theme = None
        if theme_name.lower() in ['jasny', 'light']:
            new_theme = 'light'
        elif theme_name.lower() in ['ciemny', 'dark', 'ciemny (matrix)']:
            new_theme = 'dark'
        else:
            new_theme = 'light'  # domyślny
            
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self._invalidate_cache()
    
    # === STYLE JASNY (jak w widoku tabel) ===
    LIGHT_THEME = {
        'main_bg': '#f8f9fa',
        'widget_bg': '#ffffff',
        'border_color': '#dee2e6',
        'text_color': '#2c3e50',
        'text_secondary': '#666666',
        'header_bg': '#f8f9fa',
        'header_text': '#2c3e50',
        'selection_bg': '#e3f2fd',
        'selection_text': '#1976d2',
        'button_bg': '#ffffff',
        'button_border': '#ccc',
        'button_hover': '#f0f0f0',
        'grid_color': '#dee2e6',
        'font_family': "'Segoe UI', Arial, sans-serif",
        'font_size': '13px',
        'error_color': '#dc3545',
        'success_color': '#28a745',
        'warning_color': '#ffc107',
        'info_color': '#17a2b8',
        'accent_color': '#1976d2',
        'secondary_accent': '#1565c0',
        'text_muted': '#6c757d',
        'alternating_row': '#e8f4fd'  # jasnoniebieski dla co drugiego wiersza
    }
    
    # === STYLE CIEMNY (jak w widoku zadań Matrix) ===
    DARK_THEME = {
        'main_bg': '#0d1117',
        'widget_bg': '#161b22',
        'border_color': '#00ff41',
        'text_color': '#00ff41',
        'text_secondary': '#238636',
        'header_bg': '#161b22',
        'header_text': '#00ff41',
        'selection_bg': '#1f6feb',
        'selection_text': '#ffffff',
        'button_bg': '#161b22',
        'button_border': '#00ff41',
        'button_hover': '#00ff41',
        'grid_color': '#00ff41',
        'font_family': "'Consolas', 'Courier New', monospace",
        'font_size': '13px',
        'error_color': '#ff6b6b',
        'success_color': '#51cf66',
        'warning_color': '#ffd43b',
        'info_color': '#74c0fc',
        'accent_color': '#238636',
        'secondary_accent': '#2ea043',
        'text_muted': '#7d8590',
        'label_important': '#ff6b6b',  # czerwony dla ważnych opisów
        'label_secondary': '#ff6b6b',   # czerwony zamiast szarego
        'alternating_row': '#1c2128'  # ciemny odcień dla co drugiego wiersza
    }
        
    
    def get_current_colors(self):
        """Zwraca kolory aktualnego motywu"""
        if self.current_theme == 'dark':
            return self.DARK_THEME
        else:
            return self.LIGHT_THEME
    
    def get_current_theme_dict(self):
        """Zwraca słownik z właściwościami aktualnego motywu dla kompatybilności"""
        if self.current_theme == 'dark':
            return {
                'background': self.DARK_THEME['main_bg'],
                'secondary_background': self.DARK_THEME['widget_bg'],
                'text': self.DARK_THEME['text_color'],
                'border': self.DARK_THEME['border_color'],
                'header_background': self.DARK_THEME['header_bg'],
                'accent': self.DARK_THEME['border_color'],  # używamy border_color jako accent
                'accent_text': self.DARK_THEME['main_bg'],
                'hover': self.DARK_THEME['button_hover'],
                'pressed': '#005000',  # ciemniejszy odcień zielonego
                'selection': self.DARK_THEME['selection_bg'],
                'input_background': self.DARK_THEME['widget_bg']
            }
        else:
            return {
                'background': self.LIGHT_THEME['main_bg'],
                'secondary_background': self.LIGHT_THEME['widget_bg'],
                'text': self.LIGHT_THEME['text_color'],
                'border': self.LIGHT_THEME['border_color'],
                'header_background': self.LIGHT_THEME['header_bg'],
                'accent': '#007ACC',
                'accent_text': '#ffffff',
                'hover': self.LIGHT_THEME['button_hover'],
                'pressed': '#005a9e',
                'selection': self.LIGHT_THEME['selection_bg'],
                'input_background': self.LIGHT_THEME['widget_bg']
            }
    
    # === STYLE GŁÓWNEGO OKNA ===
    def get_main_window_style(self):
        """Zwraca styl dla głównego okna aplikacji"""
        colors = self.get_current_colors()
        return f"""
            QMainWindow {{
                background-color: {colors['main_bg']};
                color: {colors['text_color']};
                font-family: {colors['font_family']};
            }}
            QStackedWidget {{
                background-color: {colors['main_bg']};
            }}
        """
    
    def get_navigation_style(self):
        """Zwraca styl dla nawigacji bocznej"""
        colors = self.get_current_colors()
        return f"""
            QWidget {{
                background-color: {colors['widget_bg']};
                border-right: 2px solid {colors['border_color']};
            }}
            QPushButton {{
                background-color: {colors['widget_bg']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {colors['button_hover']};
                border-color: {colors['text_color']};
            }}
            QPushButton:pressed {{
                background-color: {colors['selection_bg']};
                color: {colors['selection_text']};
            }}
        """
    
    def get_navigation_button_style(self):
        """Zwraca styl dla nieaktywnego przycisku nawigacji z cache"""
        return self._get_cached_style('nav_button', self._generate_navigation_button_style)
    
    def _generate_navigation_button_style(self):
        """Generuje styl dla nieaktywnego przycisku nawigacji"""
        colors = self.get_current_colors()
        return f"""
            QPushButton {{
                background-color: {colors['button_bg']};
                color: {colors['text_color']};
                border: 2px solid {colors['border_color']};
                border-radius: 8px;
                padding: 8px 12px;
                margin: 2px;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {colors['button_hover']};
                border-color: {colors['text_color']};
            }}
        """
    
    def get_active_navigation_button_style(self):
        """Zwraca styl dla aktywnego przycisku nawigacji z cache"""
        return self._get_cached_style('active_nav_button', self._generate_active_navigation_button_style)
    
    def _generate_active_navigation_button_style(self):
        """Generuje styl dla aktywnego przycisku nawigacji"""
        colors = self.get_current_colors()
        
        # Wybierz kolor aktywnego przycisku na podstawie motywu
        if self.current_theme == 'dark':
            active_color = '#28a745'  # Zielony dla trybu ciemnego
            active_text = '#ffffff'
        else:
            active_color = '#fd7e14'  # Pomarańczowy dla trybu jasnego  
            active_text = '#ffffff'
        
        return f"""
            QPushButton {{
                background-color: {active_color};
                color: {active_text};
                border: 2px solid {active_color};
                border-radius: 8px;
                padding: 8px 12px;
                margin: 2px;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {active_color};
                border-color: {active_color};
            }}
        """
            
    def get_main_widget_style(self):
        """Zwraca główny styl dla widgetów"""
        colors = self.get_current_colors()
        return f"""
            QWidget {{
                background-color: {colors['main_bg']};
                color: {colors['text_color']};
                font-family: {colors['font_family']};
                font-size: {colors['font_size']};
            }}
        """
    
    def get_dialog_style(self):
        """Zwraca styl dla dialogów"""
        colors = self.get_current_colors()
        return f"""
            QDialog {{
                background-color: {colors['main_bg']};
                color: {colors['text_color']};
                font-family: {colors['font_family']};
                font-size: {colors['font_size']};
            }}
        """
        
    def get_controls_widget_style(self):
        """Zwraca styl dla paneli kontrolek"""
        colors = self.get_current_colors()
        
        # Używaj ciemniejszego koloru ramki dla ciemnego motywu
        if self.current_theme == 'dark':
            border_color = colors['main_bg']  # Używaj koloru głównego tła jako ramki
            border_width = "1px"
        else:
            border_color = colors['border_color']
            border_width = "1px"
            
        return f"""
            QWidget {{
                background-color: {colors['widget_bg']};
                border-radius: 8px;
                border: {border_width} solid {border_color};
            }}
        """
        
    def get_label_style(self, bold=False):
        """Zwraca styl dla etykiet"""
        colors = self.get_current_colors()
        weight = "bold" if bold else "normal"
        return f"""
            QLabel {{
                color: {colors['text_color']};
                font-weight: {weight};
                font-size: 14px;
                background-color: transparent;
            }}
        """
        
    def get_combo_style(self):
        """Zwraca styl dla ComboBox"""
        colors = self.get_current_colors()
        return f"""
            QComboBox {{
                color: {colors['text_color']};
                background-color: {colors['main_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }}
            QComboBox:drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                color: {colors['text_color']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors['main_bg']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                selection-background-color: {colors['selection_bg']};
            }}
        """
        
    def get_line_edit_style(self):
        """Zwraca styl dla pól tekstowych"""
        colors = self.get_current_colors()
        return f"""
            QLineEdit {{
                color: {colors['text_color']};
                background-color: {colors['main_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }}
            QLineEdit::placeholder {{
                color: {colors['text_secondary']};
            }}
            QLineEdit:focus {{
                border: 2px solid {colors['border_color']};
                background-color: {colors['widget_bg']};
            }}
        """
    
    def get_text_edit_style(self):
        """Zwraca styl dla większych pól tekstowych"""
        colors = self.get_current_colors()
        return f"""
            QTextEdit {{
                color: {colors['text_color']};
                background-color: {colors['widget_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 4px;
                padding: 8px;
                font-family: {colors['font_family']};
            }}
            QTextEdit:focus {{
                border: 2px solid {colors['text_color']};
            }}
        """
        
    def get_table_style(self):
        """Zwraca styl dla tabel z cache"""
        return self._get_cached_style('table', self._generate_table_style)
    
    def _generate_table_style(self):
        """Generuje styl dla tabel"""
        colors = self.get_current_colors()
        
        if self.current_theme == 'dark':
            return f"""
                QTableWidget {{
                    gridline-color: {colors['grid_color']};
                    background-color: {colors['main_bg']};
                    color: {colors['text_color']};
                    selection-background-color: {colors['selection_bg']};
                    selection-color: {colors['selection_text']};
                    border: 1px solid {colors['border_color']};
                    font-family: {colors['font_family']};
                    font-size: 12px;
                    font-weight: bold;
                    alternate-background-color: {colors.get('alternating_row', '#1c2128')};
                }}
                QTableWidget::item {{
                    padding: 8px;
                    border-bottom: 1px solid {colors['text_secondary']};
                    border-right: 1px solid {colors['text_secondary']};
                    color: {colors['text_color']};
                }}
                QTableWidget::item:alternate {{
                    color: {colors['text_color']};
                }}
                QTableWidget::item:selected {{
                    background-color: {colors['selection_bg']};
                    color: {colors['selection_text']};
                }}
                QTableWidget::item:hover {{
                    background-color: {colors['text_secondary']};
                    color: #7ee787;
                }}
                QHeaderView::section {{
                    background-color: {colors['header_bg']};
                    color: {colors['header_text']};
                    border: 1px solid {colors['border_color']};
                    padding: 10px;
                    font-weight: bold;
                    font-family: {colors['font_family']};
                    font-size: 13px;
                }}
                QHeaderView::section:hover {{
                    background-color: {colors['text_secondary']};
                    color: {colors['selection_text']};
                }}
            """
        else:
            return f"""
                QTableWidget {{
                    gridline-color: {colors['grid_color']};
                    background-color: {colors['widget_bg']};
                    color: {colors['text_color']};
                    selection-background-color: {colors['selection_bg']};
                    selection-color: {colors['selection_text']};
                    border: 1px solid {colors['border_color']};
                    font-family: {colors['font_family']};
                    font-size: 12px;
                    alternate-background-color: {colors.get('alternating_row', '#e8f4fd')};
                }}
                QTableWidget::item {{
                    padding: 8px;
                    border-bottom: 1px solid #f0f0f0;
                    color: #2c3e50;
                    font-family: {colors['font_family']};
                    font-size: 12px;
                }}
                QTableWidget::item:alternate {{
                    color: #2c3e50;
                }}
                QTableWidget::item:selected {{
                    background-color: {colors['selection_bg']};
                    color: {colors['selection_text']};
                }}
                QTableWidget::item:hover {{
                    background-color: #e9ecef;
                    color: #212529;
                }}
                QHeaderView::section {{
                    background-color: #e9ecef;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    border-bottom: 2px solid #007ACC;
                    padding: 12px 8px;
                    font-weight: bold;
                    font-family: {colors['font_family']};
                    font-size: 13px;
                    text-align: center;
                }}
                QHeaderView::section:hover {{
                    background-color: #dee2e6;
                    color: #212529;
                }}
                QHeaderView::section:pressed {{
                    background-color: #ced4da;
                    color: #212529;
                }}
            """
    
    def get_tree_style(self):
        """Zwraca styl dla drzew (QTreeWidget)"""
        colors = self.get_current_colors()
        
        if self.current_theme == 'dark':
            return f"""
                QTreeWidget {{
                    background-color: {colors['widget_bg']};
                    color: {colors['text_color']};
                    border: 1px solid {colors['border_color']};
                    border-radius: 4px;
                    outline: none;
                    font-family: {colors['font_family']};
                    alternate-background-color: {colors['main_bg']};
                }}
                QTreeWidget::item {{
                    padding: 5px;
                    border-bottom: 1px solid {colors['text_secondary']};
                    color: {colors['text_color']};
                }}
                QTreeWidget::item:selected {{
                    background-color: {colors['selection_bg']};
                    color: {colors['selection_text']};
                }}
                QTreeWidget::item:hover {{
                    background-color: {colors['button_hover']};
                    color: {colors['text_color']};
                }}
                QHeaderView::section {{
                    background-color: {colors['header_bg']};
                    color: {colors['header_text']};
                    border: 1px solid {colors['border_color']};
                    padding: 10px;
                    font-weight: bold;
                }}
            """
        else:
            return f"""
                QTreeWidget {{
                    background-color: {colors['widget_bg']};
                    color: {colors['text_color']};
                    border: 1px solid {colors['border_color']};
                    border-radius: 4px;
                    outline: none;
                    font-family: {colors['font_family']};
                    alternate-background-color: {colors.get('alternating_row', '#e8f4fd')};
                }}
                QTreeWidget::item {{
                    padding: 5px;
                    border-bottom: 1px solid #f0f0f0;
                    color: {colors['text_color']};
                }}
                QTreeWidget::item:selected {{
                    background-color: {colors['selection_bg']};
                    color: {colors['selection_text']};
                }}
                QTreeWidget::item:hover {{
                    background-color: {colors['button_hover']};
                    color: {colors['text_color']};
                }}
                QHeaderView::section {{
                    background-color: {colors['header_bg']};
                    color: {colors['header_text']};
                    border: none;
                    border-bottom: 2px solid {colors['border_color']};
                    padding: 10px;
                    font-weight: bold;
                }}
            """
            
    def get_list_style(self):
        """Zwraca styl dla list (QListWidget)"""
        colors = self.get_current_colors()
        
        if self.current_theme == 'dark':
            return f"""
                QListWidget {{
                    background-color: {colors['widget_bg']};
                    color: {colors['text_color']};
                    border: 1px solid {colors['border_color']};
                    border-radius: 4px;
                    outline: none;
                    font-family: {colors['font_family']};
                    font-size: 12px;
                    alternate-background-color: {colors['text_secondary']};
                }}
                QListWidget::item {{
                    padding: 8px;
                    border-bottom: 1px solid {colors['border_color']};
                    color: {colors['text_color']};
                }}
                QListWidget::item:selected {{
                    background-color: {colors['selection_bg']};
                    color: {colors['selection_text']};
                }}
                QListWidget::item:hover {{
                    background-color: {colors['text_secondary']};
                    color: {colors['text_color']};
                }}
            """
        else:
            return f"""
                QListWidget {{
                    background-color: {colors['widget_bg']};
                    color: {colors['text_color']};
                    border: 1px solid {colors['border_color']};
                    border-radius: 4px;
                    outline: none;
                    font-family: {colors['font_family']};
                    font-size: 12px;
                    alternate-background-color: {colors.get('alternating_row', '#e8f4fd')};
                }}
                QListWidget::item {{
                    padding: 8px;
                    border-bottom: 1px solid #f0f0f0;
                    color: {colors['text_color']};
                    background-color: transparent;
                }}
                QListWidget::item:selected {{
                    background-color: {colors['selection_bg']};
                    color: {colors['selection_text']};
                }}
                QListWidget::item:hover {{
                    background-color: #f5f5f5;
                    color: {colors['text_color']};
                }}
            """
            
    def get_button_style(self, color_variant='default'):
        """Zwraca styl dla przycisków"""
        colors = self.get_current_colors()
        
        if self.current_theme == 'dark':
            return f"""
                QPushButton {{
                    background-color: {colors['button_bg']};
                    color: {colors['text_color']};
                    border: 1px solid {colors['button_border']};
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                    font-family: {colors['font_family']};
                }}
                QPushButton:hover {{
                    background-color: {colors['button_hover']};
                    color: {colors['main_bg']};
                }}
                QPushButton:pressed {{
                    background-color: #7ee787;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {colors['button_bg']};
                    color: {colors['text_color']};
                    border: 1px solid {colors['button_border']};
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['button_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['border_color']};
                }}
            """
    
    def get_primary_button_style(self):
        """Zwraca styl dla głównych przycisków (primary)"""
        colors = self.get_current_colors()
        
        if self.current_theme == 'dark':
            return f"""
                QPushButton {{
                    background-color: {colors['accent_color']};
                    color: {colors['main_bg']};
                    border: 1px solid {colors['accent_color']};
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-family: {colors['font_family']};
                }}
                QPushButton:hover {{
                    background-color: {colors['secondary_accent']};
                    border-color: {colors['secondary_accent']};
                }}
                QPushButton:pressed {{
                    background-color: #0969da;
                }}
                QPushButton:disabled {{
                    background-color: {colors['border_color']};
                    color: {colors['text_muted']};
                    border-color: {colors['border_color']};
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {colors['accent_color']};
                    color: white;
                    border: 1px solid {colors['accent_color']};
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['secondary_accent']};
                    border-color: {colors['secondary_accent']};
                }}
                QPushButton:pressed {{
                    background-color: #0550ae;
                }}
                QPushButton:disabled {{
                    background-color: {colors['border_color']};
                    color: {colors['text_muted']};
                    border-color: {colors['border_color']};
                }}
            """
            
    def get_checkbox_style(self):
        """Zwraca styl dla checkbox"""
        colors = self.get_current_colors()
        
        if self.current_theme == 'dark':
            return f"""
                QCheckBox {{
                    color: {colors['text_color']};
                    font-weight: bold;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                }}
                QCheckBox::indicator:unchecked {{
                    border: 2px solid {colors['border_color']};
                    background-color: {colors['main_bg']};
                }}
                QCheckBox::indicator:checked {{
                    border: 2px solid {colors['border_color']};
                    background-color: {colors['border_color']};
                }}
            """
        else:
            return f"""
                QCheckBox {{
                    color: {colors['text_color']};
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                QCheckBox::indicator:unchecked {{
                    border: 1px solid {colors['border_color']};
                    background-color: {colors['widget_bg']};
                }}
                QCheckBox::indicator:checked {{
                    border: 1px solid {colors['selection_text']};
                    background-color: {colors['selection_text']};
                }}
            """
    
    def get_tab_widget_style(self):
        """Zwraca styl dla QTabWidget"""
        colors = self.get_current_colors()
        return f"""
            QTabWidget::pane {{
                border: 1px solid {colors['border_color']};
                background-color: {colors['widget_bg']};
            }}
            QTabBar::tab {{
                background-color: {colors['main_bg']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {colors['widget_bg']};
                color: {colors['text_color']};
                border-bottom: 2px solid {colors['text_color']};
            }}
            QTabBar::tab:hover {{
                background-color: {colors['button_hover']};
            }}
        """
    
    def get_group_box_style(self):
        """Zwraca styl dla QGroupBox z poprawionymi kolorami"""
        colors = self.get_current_colors()
        return f"""
            QGroupBox {{
                color: {colors['text_color']};
                background-color: {colors['widget_bg']};
                border: 2px solid {colors['border_color']};
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: {colors['widget_bg']};
                color: {colors['text_color']};
            }}
        """
    
    def get_spin_box_style(self):
        """Zwraca styl dla QSpinBox/QDoubleSpinBox"""
        colors = self.get_current_colors()
        return f"""
            QSpinBox, QDoubleSpinBox {{
                color: {colors['text_color']};
                background-color: {colors['widget_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 4px;
                padding: 5px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {colors['text_color']};
            }}
        """
    
    def get_date_edit_style(self):
        """Zwraca styl dla QDateEdit/QDateTimeEdit/QTimeEdit"""
        colors = self.get_current_colors()
        return f"""
            QDateEdit, QDateTimeEdit, QTimeEdit {{
                color: {colors['text_color']};
                background-color: {colors['widget_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: 4px;
                padding: 5px;
            }}
            QDateEdit:focus, QDateTimeEdit:focus, QTimeEdit:focus {{
                border: 2px solid {colors['text_color']};
            }}
            QDateEdit::drop-down, QDateTimeEdit::drop-down, QTimeEdit::drop-down {{
                border: none;
            }}
        """
    
    def get_secondary_label_style(self):
        """Zwraca styl dla opisów dodatkowych (czerwony w ciemnym, czarny w jasnym)"""
        colors = self.get_current_colors()
        if self.current_theme == 'dark':
            return f"""
                QLabel {{
                    color: {colors.get('label_secondary', '#ff6b6b')};
                    font-weight: normal;
                    font-size: 12px;
                    background-color: transparent;
                }}
            """
        else:
            return f"""
                QLabel {{
                    color: {colors['text_color']};
                    font-weight: normal;
                    font-size: 12px;
                    background-color: transparent;
                }}
            """
    
    def get_timer_work_style(self):
        """Zwraca styl dla timera w trybie pracy"""
        colors = self.get_current_colors()
        return f"""
            color: #e74c3c;
            background-color: {colors['widget_bg']};
            border: 3px solid #fee2e2;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
        """
    
    def get_timer_break_style(self):
        """Zwraca styl dla timera w trybie przerwy"""
        colors = self.get_current_colors()
        return f"""
            color: #27ae60;
            background-color: {colors['widget_bg']};
            border: 3px solid #d4edd7;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
        """
    
    def get_progress_work_style(self):
        """Zwraca styl dla paska postępu w trybie pracy"""
        colors = self.get_current_colors()
        return f"""
            QProgressBar {{
                border: 2px solid {colors['border_color']};
                border-radius: 6px;
                background-color: {colors['widget_bg']};
            }}
            QProgressBar::chunk {{
                background-color: #e74c3c;
                border-radius: 4px;
            }}
        """
    
    def get_progress_break_style(self):
        """Zwraca styl dla paska postępu w trybie przerwy"""
        colors = self.get_current_colors()
        return f"""
            QProgressBar {{
                border: 2px solid {colors['border_color']};
                border-radius: 6px;
                background-color: {colors['widget_bg']};
            }}
            QProgressBar::chunk {{
                background-color: #27ae60;
                border-radius: 4px;
            }}
        """
    
    def get_pause_button_style(self):
        """Zwraca styl dla przycisku pauzy"""
        return f"""
            QPushButton {{
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #d35400;
            }}
        """
    
    def get_info_label_style(self):
        """Zwraca styl dla etykiet informacyjnych"""
        colors = self.get_current_colors()
        if self.current_theme == 'dark':
            return f"""
                QLabel {{
                    color: {colors.get('label_secondary', '#ff6b6b')};
                    font-style: italic;
                    background-color: transparent;
                }}
            """
        else:
            return f"""
                QLabel {{
                    color: {colors['text_color']};
                    font-style: italic;
                    background-color: transparent;
                }}
            """
    
    def get_error_label_style(self):
        """Zwraca styl dla etykiet błędów"""
        return f"""
            QLabel {{
                color: #e74c3c;
                font-weight: bold;
                background-color: transparent;
            }}
        """
    
    def get_danger_button_style(self):
        """Zwraca styl dla przycisków niebezpiecznych (usuwanie)"""
        return f"""
            QPushButton {{
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
            QPushButton:pressed {{
                background-color: #a71e2a;
            }}
        """
    
    def get_title_label_style(self):
        """Zwraca styl dla etykiet tytułowych"""
        colors = self.get_current_colors()
        return f"""
            QLabel {{
                color: {colors['text_color']};
                background-color: transparent;
                font-family: {colors['font_family']};
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
            }}
        """
    
    def get_add_task_panel_style(self):
        """Zwraca style dla panelu dodawania zadań"""
        return self._get_cached_style('add_task_panel', self._generate_add_task_panel_style)
    
    def _generate_add_task_panel_style(self):
        """Generuje style dla panelu dodawania zadań"""
        colors = self.get_current_colors()
        
        return {
            'frame': f"""
                QFrame {{
                    background-color: {colors['widget_bg']};
                    border: 2px solid {colors['border_color']};
                    border-radius: 8px;
                    margin: 5px;
                }}
            """,
            
            'title': f"""
                QLabel {{
                    color: {colors['text_color']};
                    font-family: {colors['font_family']};
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 5px;
                    background-color: transparent;
                }}
            """,
            
            'field_label': f"""
                QLabel {{
                    color: {colors['text_secondary']};
                    font-family: {colors['font_family']};
                    font-size: 10px;
                    font-weight: bold;
                    background-color: transparent;
                    margin-right: 5px;
                }}
            """,
            
            'task_input': f"""
                QTextEdit {{
                    background-color: {colors['widget_bg']};
                    border: 2px solid {colors['border_color']};
                    border-radius: 6px;
                    padding: 8px;
                    font-family: {colors['font_family']};
                    font-size: 10px;
                    color: {colors['text_color']};
                }}
                QTextEdit:focus {{
                    border-color: {colors.get('accent_color', '#3498db')};
                }}
            """,
            
            'add_button': f"""
                QPushButton {{
                    background-color: {colors.get('accent_color', '#3498db')};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-family: {colors['font_family']};
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('accent_hover', '#2980b9')};
                }}
                QPushButton:pressed {{
                    background-color: {colors.get('accent_pressed', '#21618c')};
                }}
            """,
            
            'panel_widget': f"""
                QComboBox, QLineEdit, QSpinBox, QDateTimeEdit {{
                    background-color: {colors['widget_bg']};
                    border: 2px solid {colors['border_color']};
                    border-radius: 4px;
                    padding: 5px;
                    font-family: {colors['font_family']};
                    font-size: 9px;
                    color: {colors['text_color']};
                }}
                QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QDateTimeEdit:focus {{
                    border-color: {colors.get('accent_color', '#3498db')};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                }}
                QComboBox::down-arrow {{
                    width: 12px;
                    height: 12px;
                }}
            """,
            
            'checkbox': f"""
                QCheckBox {{
                    color: {colors['text_color']};
                    font-family: {colors['font_family']};
                    font-size: 9px;
                    background-color: transparent;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid {colors['border_color']};
                    border-radius: 3px;
                    background-color: {colors['widget_bg']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {colors.get('accent_color', '#3498db')};
                    border-color: {colors.get('accent_color', '#3498db')};
                }}
            """,
            
            'separator': f"""
                QLabel {{
                    color: {colors['text_secondary']};
                    font-family: {colors['font_family']};
                    font-size: 12px;
                    font-weight: bold;
                    background-color: transparent;
                    margin: 0 10px;
                }}
            """
        }