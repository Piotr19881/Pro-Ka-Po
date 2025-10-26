"""
Dialog konfiguracji kolumn matematycznych z formułami
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel, 
                             QGroupBox, QCheckBox, QComboBox, QSpinBox,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QTableWidget, QTableWidgetItem, QSplitter)
from PyQt6.QtCore import Qt
import re

class MathColumnDialog(QDialog):
    """Dialog konfiguracji kolumny matematycznej"""
    
    def __init__(self, parent=None, column_config=None):
        super().__init__(parent)
        self.column_config = column_config or {}
        
        self.setWindowTitle("Konfiguracja kolumny matematycznej")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.setup_example_table()
        
        if self.column_config:
            self.load_config()
    
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        main_layout = QHBoxLayout(self)
        
        # Lewa strona - konfiguracja
        left_panel = self.create_config_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Prawa strona - podgląd tabeli
        right_panel = self.create_preview_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_config_panel(self):
        """Tworzy panel konfiguracji formuły"""
        panel = QGroupBox("Konfiguracja formuły")
        layout = QVBoxLayout(panel)
        
        # Podstawowe informacje
        basic_info = self.create_basic_info_section()
        layout.addWidget(basic_info)
        
        # Edytor formuły
        formula_editor = self.create_formula_editor()
        layout.addWidget(formula_editor)
        
        # Pomoc i przykłady
        help_section = self.create_help_section()
        layout.addWidget(help_section)
        
        # Przyciski
        buttons = self.create_buttons()
        layout.addLayout(buttons)
        
        return panel
    
    def create_basic_info_section(self):
        """Tworzy sekcję podstawowych informacji"""
        group = QGroupBox("Podstawowe ustawienia")
        layout = QFormLayout(group)
        
        # Nazwa kolumny
        self.column_name = QLineEdit()
        self.column_name.setPlaceholderText("np. 'Suma', 'VAT', 'Procent'")
        layout.addRow("Nazwa kolumny:", self.column_name)
        
        # Typ wyniku
        self.result_type = QComboBox()
        self.result_type.addItems([
            "Liczba całkowita", "Liczba dziesiętna", "Waluta", "Procent"
        ])
        layout.addRow("Typ wyniku:", self.result_type)
        
        # Wartość domyślna
        self.default_value = QLineEdit()
        self.default_value.setPlaceholderText("0")
        layout.addRow("Wartość domyślna:", self.default_value)
        
        # Automatyczne przeliczanie
        self.auto_calculate = QCheckBox("Automatyczne przeliczanie przy zmianie")
        self.auto_calculate.setChecked(True)
        layout.addRow(self.auto_calculate)
        
        return group
    
    def create_formula_editor(self):
        """Tworzy edytor formuły"""
        group = QGroupBox("Edytor formuły")
        layout = QVBoxLayout(group)
        
        # Instrukcja
        instruction = QLabel("""
        <b>Instrukcja tworzenia formuł:</b><br>
        • Kolumny oznaczaj literami: A, B, C, D...<br>
        • Wiersze numeruj: 1, 2, 3, 4...<br>
        • Komórki: A1, B2, C3 (kolumna + wiersz)<br>
        • Dostępne operatory: +, -, *, /, %, ^<br>
        • Funkcje: SUM(), AVG(), MIN(), MAX(), COUNT()
        """)
        instruction.setStyleSheet("color: #666; padding: 10px; background: #f0f0f0;")
        layout.addWidget(instruction)
        
        # Pole formuły
        formula_layout = QHBoxLayout()
        formula_layout.addWidget(QLabel("Formuła:"))
        
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("np. A1 + B1 * 0.23 lub SUM(A1:A10)")
        self.formula_input.textChanged.connect(self.validate_formula)
        formula_layout.addWidget(self.formula_input)
        
        self.validate_btn = QPushButton("✓ Sprawdź")
        self.validate_btn.clicked.connect(self.validate_and_preview)
        formula_layout.addWidget(self.validate_btn)
        
        layout.addLayout(formula_layout)
        
        # Status formuły
        self.formula_status = QLabel("Wprowadź formułę...")
        self.formula_status.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
        layout.addWidget(self.formula_status)
        
        # Szybkie przyciski formuł
        quick_formulas = self.create_quick_formulas()
        layout.addWidget(quick_formulas)
        
        return group
    
    def create_quick_formulas(self):
        """Tworzy przyciski szybkich formuł"""
        group = QGroupBox("Szybkie formuły")
        layout = QVBoxLayout(group)
        
        # Pierwszy rząd przycisków
        row1 = QHBoxLayout()
        
        sum_btn = QPushButton("SUM(A1:A10)")
        sum_btn.clicked.connect(lambda: self.insert_formula("SUM(A1:A10)"))
        row1.addWidget(sum_btn)
        
        avg_btn = QPushButton("AVG(B1:B10)")
        avg_btn.clicked.connect(lambda: self.insert_formula("AVG(B1:B10)"))
        row1.addWidget(avg_btn)
        
        vat_btn = QPushButton("A1 * 1.23")
        vat_btn.clicked.connect(lambda: self.insert_formula("A1 * 1.23"))
        row1.addWidget(vat_btn)
        
        layout.addLayout(row1)
        
        # Drugi rząd przycisków
        row2 = QHBoxLayout()
        
        percent_btn = QPushButton("A1 * 0.01")
        percent_btn.clicked.connect(lambda: self.insert_formula("A1 * 0.01"))
        row2.addWidget(percent_btn)
        
        diff_btn = QPushButton("B1 - A1")
        diff_btn.clicked.connect(lambda: self.insert_formula("B1 - A1"))
        row2.addWidget(diff_btn)
        
        count_btn = QPushButton("COUNT(C1:C10)")
        count_btn.clicked.connect(lambda: self.insert_formula("COUNT(C1:C10)"))
        row2.addWidget(count_btn)
        
        layout.addLayout(row2)
        
        return group
    
    def create_help_section(self):
        """Tworzy sekcję pomocy"""
        group = QGroupBox("Dostępne funkcje")
        layout = QVBoxLayout(group)
        
        help_text = QTextEdit()
        help_text.setMaximumHeight(120)
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <b>Funkcje matematyczne:</b><br>
        • <code>SUM(A1:A10)</code> - suma zakresu komórek<br>
        • <code>AVG(B1:B5)</code> - średnia arytmetyczna<br>
        • <code>MIN(C1:C10)</code> - wartość minimalna<br>
        • <code>MAX(D1:D10)</code> - wartość maksymalna<br>
        • <code>COUNT(E1:E10)</code> - liczba niepustych komórek<br><br>
        
        <b>Operatory inkrementacji/dekrementacji:</b><br>
        • <code>A1++</code> - zwraca wartość A1 (post-increment)<br>
        • <code>++A1</code> - zwraca A1 + 1 (pre-increment)<br>
        • <code>A1--</code> - zwraca wartość A1 (post-decrement)<br>
        • <code>--A1</code> - zwraca A1 - 1 (pre-decrement)<br>
        • <code>5++</code> - zwraca 5, <code>++5</code> - zwraca 6<br><br>
        
        <b>Przykłady formuł:</b><br>
        • <code>A1 + B1</code> - suma dwóch komórek<br>
        • <code>++A1</code> - ID następnego rekordu<br>
        • <code>MAX(A1:A10) + 1</code> - kolejny numer ID<br>
        • <code>SUM(A1:A10) - B1</code> - suma minus jedna komórka
        """)
        layout.addWidget(help_text)
        
        return group
    
    def create_preview_panel(self):
        """Tworzy panel podglądu tabeli"""
        panel = QGroupBox("Podgląd działania formuły")
        layout = QVBoxLayout(panel)
        
        # Instrukcja
        preview_info = QLabel("Tabela przykładowa - wprowadź dane, aby przetestować formułę:")
        preview_info.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(preview_info)
        
        # Tabela podglądu
        self.preview_table = QTableWidget()
        self.preview_table.setRowCount(10)
        self.preview_table.setColumnCount(6)
        
        # Nagłówki kolumn (A, B, C, D, E, F)
        column_headers = [chr(65 + i) for i in range(6)]  # A, B, C, D, E, F
        self.preview_table.setHorizontalHeaderLabels(column_headers)
        
        # Nagłówki wierszy (1, 2, 3...)
        row_headers = [str(i + 1) for i in range(10)]
        self.preview_table.setVerticalHeaderLabels(row_headers)
        
        # Podłącz sygnał zmiany komórki
        self.preview_table.itemChanged.connect(self.recalculate_formula)
        
        layout.addWidget(self.preview_table)
        
        # Wynik formuły
        self.result_label = QLabel("Wynik formuły: -")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2C3E50; padding: 5px;")
        layout.addWidget(self.result_label)
        
        return panel
    
    def create_buttons(self):
        """Tworzy przyciski akcji"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Zapisz konfigurację")
        save_btn.clicked.connect(self.save_configuration)
        save_btn.setDefault(True)
        layout.addWidget(save_btn)
        
        return layout
    
    def setup_example_table(self):
        """Wypełnia tabelę przykładowymi danymi"""
        example_data = [
            [100, 200, 50, None, None, None],
            [150, 300, 75, None, None, None],
            [80, 160, 40, None, None, None],
            [220, 440, 110, None, None, None],
            [90, 180, 45, None, None, None]
        ]
        
        for row, row_data in enumerate(example_data):
            for col, value in enumerate(row_data):
                if value is not None:
                    item = QTableWidgetItem(str(value))
                    self.preview_table.setItem(row, col, item)
    
    def insert_formula(self, formula):
        """Wstawia formułę do pola edycji"""
        self.formula_input.setText(formula)
        self.validate_and_preview()
    
    def validate_formula(self):
        """Waliduje formułę w czasie rzeczywistym"""
        formula = self.formula_input.text().strip()
        
        if not formula:
            self.formula_status.setText("Wprowadź formułę...")
            self.formula_status.setStyleSheet("color: #666; font-style: italic;")
            return
        
        # Sprawdź składnię formuły
        if self.is_valid_formula(formula):
            self.formula_status.setText("✓ Formuła poprawna")
            self.formula_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.formula_status.setText("✗ Błąd w formule")
            self.formula_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def is_valid_formula(self, formula):
        """Sprawdza czy formuła jest poprawna"""
        try:
            # Podstawowa walidacja składni
            
            # Sprawdź dozwolone znaki
            allowed_pattern = r'^[A-Z0-9+\-*/%()\s:.,]+$'
            if not re.match(allowed_pattern, formula.upper()):
                return False
            
            # Sprawdź czy referencje komórek są poprawne (A1, B2, etc.)
            cell_pattern = r'[A-Z]+[0-9]+'
            cells = re.findall(cell_pattern, formula.upper())
            
            # Sprawdź funkcje
            function_pattern = r'(SUM|AVG|MIN|MAX|COUNT)\([A-Z0-9:,\s]+\)'
            functions = re.findall(function_pattern, formula.upper())
            
            # Jeśli zawiera komórki lub funkcje, uznaj za potencjalnie poprawną
            return len(cells) > 0 or len(functions) > 0 or formula.replace(' ', '').replace('.', '').replace(',', '').isdigit()
            
        except:
            return False
    
    def validate_and_preview(self):
        """Waliduje i pokazuje podgląd formuły"""
        self.validate_formula()
        self.recalculate_formula()
    
    def recalculate_formula(self):
        """Przelicza formułę na podstawie danych w tabeli"""
        formula = self.formula_input.text().strip()
        
        if not formula or not self.is_valid_formula(formula):
            self.result_label.setText("Wynik formuły: -")
            return
        
        try:
            result = self.evaluate_formula(formula)
            self.result_label.setText(f"Wynik formuły: {result}")
            self.result_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #27ae60; padding: 5px;")
        except Exception as e:
            self.result_label.setText(f"Błąd: {str(e)}")
            self.result_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #e74c3c; padding: 5px;")
    
    def evaluate_formula(self, formula):
        """Oblicza wartość formuły"""
        # Zamień referencje komórek na wartości
        processed_formula = self.replace_cell_references(formula)
        
        # Obsłuż funkcje
        processed_formula = self.replace_functions(processed_formula)
        
        # Bezpieczne obliczenie (tylko podstawowe operacje)
        try:
            # Usuń niedozwolone znaki dla bezpieczeństwa
            safe_chars = set('0123456789+-*/.() ')
            if all(c in safe_chars for c in processed_formula):
                return round(eval(processed_formula), 2)
            else:
                return "Błąd: niedozwolone znaki"
        except:
            return "Błąd obliczenia"
    
    def replace_cell_references(self, formula):
        """Zamienia referencje komórek (A1, B2) na wartości"""
        def get_cell_value(match):
            cell_ref = match.group(0)
            
            # Parsuj referencję komórki (np. A1 -> kolumna A, wiersz 1)
            col_letters = ''
            row_digits = ''
            
            for char in cell_ref:
                if char.isalpha():
                    col_letters += char
                elif char.isdigit():
                    row_digits += char
            
            if not col_letters or not row_digits:
                return '0'
            
            # Konwertuj litere kolumny na indeks (A=0, B=1, ...)
            col_index = 0
            for char in col_letters:
                col_index = col_index * 26 + (ord(char) - ord('A') + 1)
            col_index -= 1
            
            row_index = int(row_digits) - 1
            
            # Pobierz wartość z tabeli
            if (0 <= row_index < self.preview_table.rowCount() and 
                0 <= col_index < self.preview_table.columnCount()):
                
                item = self.preview_table.item(row_index, col_index)
                if item and item.text().strip():
                    try:
                        return str(float(item.text()))
                    except:
                        return '0'
            
            return '0'
        
        # Zamień wszystkie referencje komórek
        cell_pattern = r'[A-Z]+[0-9]+'
        return re.sub(cell_pattern, get_cell_value, formula.upper())
    
    def replace_functions(self, formula):
        """Zamienia funkcje (SUM, AVG, etc.) na obliczone wartości"""
        # Najpierw obsłuż operatory inkrementacji/dekrementacji
        formula = self.replace_increment_operators(formula)
        
        # SUM(A1:A10)
        def replace_sum(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            return str(sum(values))
        
        # AVG(A1:A10)
        def replace_avg(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            return str(sum(values) / len(values) if values else 0)
        
        # MIN(A1:A10)
        def replace_min(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            return str(min(values) if values else 0)
        
        # MAX(A1:A10)
        def replace_max(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            return str(max(values) if values else 0)
        
        # COUNT(A1:A10)
        def replace_count(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            return str(len(values))
        
        # Zamień funkcje
        formula = re.sub(r'SUM\(([^)]+)\)', replace_sum, formula)
        formula = re.sub(r'AVG\(([^)]+)\)', replace_avg, formula)
        formula = re.sub(r'MIN\(([^)]+)\)', replace_min, formula)
        formula = re.sub(r'MAX\(([^)]+)\)', replace_max, formula)
        formula = re.sub(r'COUNT\(([^)]+)\)', replace_count, formula)
        
        return formula
        
    def replace_increment_operators(self, formula):
        """Obsługuje operatory inkrementacji (++) i dekrementacji (--)"""
        
        # Obsługa A1++ (post-increment - zwraca wartość przed zwiększeniem)
        def replace_post_increment(match):
            cell_ref = match.group(1)
            current_value = self.get_cell_value_by_ref(cell_ref)
            try:
                return str(float(current_value))
            except:
                return "0"
        
        # Obsługa ++A1 (pre-increment - zwraca wartość po zwiększeniu)
        def replace_pre_increment(match):
            cell_ref = match.group(1)
            current_value = self.get_cell_value_by_ref(cell_ref)
            try:
                return str(float(current_value) + 1)
            except:
                return "1"
        
        # Obsługa A1-- (post-decrement - zwraca wartość przed zmniejszeniem)
        def replace_post_decrement(match):
            cell_ref = match.group(1)
            current_value = self.get_cell_value_by_ref(cell_ref)
            try:
                return str(float(current_value))
            except:
                return "0"
        
        # Obsługa --A1 (pre-decrement - zwraca wartość po zmniejszeniu)
        def replace_pre_decrement(match):
            cell_ref = match.group(1)
            current_value = self.get_cell_value_by_ref(cell_ref)
            try:
                return str(float(current_value) - 1)
            except:
                return "-1"
        
        # Obsługa liczby++ (post-increment dla liczb)
        def replace_number_post_increment(match):
            number = match.group(1)
            try:
                return str(float(number))
            except:
                return "0"
        
        # Obsługa ++liczby (pre-increment dla liczb)
        def replace_number_pre_increment(match):
            number = match.group(1)
            try:
                return str(float(number) + 1)
            except:
                return "1"
        
        # Obsługa liczby-- (post-decrement dla liczb)
        def replace_number_post_decrement(match):
            number = match.group(1)
            try:
                return str(float(number))
            except:
                return "0"
        
        # Obsługa --liczby (pre-decrement dla liczb)
        def replace_number_pre_decrement(match):
            number = match.group(1)
            try:
                return str(float(number) - 1)
            except:
                return "-1"
        
        # Zastąp operatory inkrementacji/dekrementacji
        # Post-increment/decrement dla komórek (A1++, A1--)
        formula = re.sub(r'([A-Z]+\d+)\+\+', replace_post_increment, formula)
        formula = re.sub(r'([A-Z]+\d+)--', replace_post_decrement, formula)
        
        # Pre-increment/decrement dla komórek (++A1, --A1)
        formula = re.sub(r'\+\+([A-Z]+\d+)', replace_pre_increment, formula)
        formula = re.sub(r'--([A-Z]+\d+)', replace_pre_decrement, formula)
        
        # Post-increment/decrement dla liczb (5++, 10--)
        formula = re.sub(r'(\d+(?:\.\d+)?)\+\+', replace_number_post_increment, formula)
        formula = re.sub(r'(\d+(?:\.\d+)?)--', replace_number_post_decrement, formula)
        
        # Pre-increment/decrement dla liczb (++5, --10)
        formula = re.sub(r'\+\+(\d+(?:\.\d+)?)', replace_number_pre_increment, formula)
        formula = re.sub(r'--(\d+(?:\.\d+)?)', replace_number_pre_decrement, formula)
        
        return formula
    
    def get_cell_value_by_ref(self, cell_ref):
        """Pobiera wartość komórki po referencji (np. A1)"""
        # Parsuj referencję komórki
        col_letters = ''
        row_digits = ''
        
        for char in cell_ref:
            if char.isalpha():
                col_letters += char
            elif char.isdigit():
                row_digits += char
        
        if not col_letters or not row_digits:
            return 0
        
        # Konwertuj literę kolumny na indeks
        col_index = 0
        for char in col_letters:
            col_index = col_index * 26 + (ord(char) - ord('A') + 1)
        col_index -= 1
        
        row_index = int(row_digits) - 1
        
        # Pobierz wartość z tabeli podglądu
        if (0 <= row_index < self.preview_table.rowCount() and 
            0 <= col_index < self.preview_table.columnCount()):
            item = self.preview_table.item(row_index, col_index)
            if item and item.text():
                try:
                    return float(item.text())
                except:
                    return 0
        return 0
    
    def get_range_values(self, range_str):
        """Pobiera wartości z zakresu komórek (np. A1:A10)"""
        values = []
        
        if ':' in range_str:
            # Zakres komórek (A1:A10)
            start_cell, end_cell = range_str.split(':')
            start_cell, end_cell = start_cell.strip(), end_cell.strip()
            
            # Parsuj początek i koniec zakresu
            start_col, start_row = self.parse_cell_reference(start_cell)
            end_col, end_row = self.parse_cell_reference(end_cell)
            
            # Pobierz wszystkie wartości z zakresu
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    if (0 <= row < self.preview_table.rowCount() and 
                        0 <= col < self.preview_table.columnCount()):
                        
                        item = self.preview_table.item(row, col)
                        if item and item.text().strip():
                            try:
                                values.append(float(item.text()))
                            except:
                                pass
        
        return values
    
    def parse_cell_reference(self, cell_ref):
        """Parsuje referencję komórki na indeksy kolumny i wiersza"""
        col_letters = ''
        row_digits = ''
        
        for char in cell_ref:
            if char.isalpha():
                col_letters += char
            elif char.isdigit():
                row_digits += char
        
        # Konwertuj litere kolumny na indeks
        col_index = 0
        for char in col_letters:
            col_index = col_index * 26 + (ord(char) - ord('A') + 1)
        col_index -= 1
        
        row_index = int(row_digits) - 1 if row_digits else 0
        
        return col_index, row_index
    
    def load_config(self):
        """Ładuje istniejącą konfigurację"""
        if self.column_config:
            self.column_name.setText(self.column_config.get('name', ''))
            self.formula_input.setText(self.column_config.get('formula', ''))
            # TODO: załaduj więcej ustawień
    
    def save_configuration(self):
        """Zapisuje konfigurację kolumny matematycznej"""
        if not self.column_name.text().strip():
            QMessageBox.warning(self, "Błąd", "Nazwa kolumny nie może być pusta!")
            return
        
        if not self.formula_input.text().strip():
            QMessageBox.warning(self, "Błąd", "Formuła nie może być pusta!")
            return
        
        if not self.is_valid_formula(self.formula_input.text()):
            QMessageBox.warning(self, "Błąd", "Formuła zawiera błędy!")
            return
        
        # Zbierz konfigurację
        config = {
            'name': self.column_name.text().strip(),
            'formula': self.formula_input.text().strip(),
            'result_type': self.result_type.currentText(),
            'default_value': self.default_value.text().strip() or '0',
            'auto_calculate': self.auto_calculate.isChecked()
        }
        
        self.column_config = config
        
        QMessageBox.information(self, "Sukces", 
            f"Konfiguracja kolumny '{config['name']}' została zapisana!")
        
        self.accept()
    
    def get_configuration(self):
        """Zwraca konfigurację kolumny"""
        return self.column_config