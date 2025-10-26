"""
Delegat dla obsługi różnych typów kolumn w tabeli zadań
"""
from PyQt6.QtWidgets import (
    QStyledItemDelegate,
    QComboBox,
    QDateTimeEdit,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QStyleOptionViewItem,
)
from PyQt6.QtCore import Qt, QDateTime, QDate
from PyQt6.QtGui import QColor, QBrush


class ColumnDelegate(QStyledItemDelegate):
    """Delegat obsługujący różne typy edytorów dla kolumn"""
    
    def __init__(self, parent=None, db_manager=None, theme_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.theme_manager = theme_manager
        self.column_types = {}  # Mapa: nazwa_kolumny -> typ
        self.column_lists = {}  # Mapa: nazwa_kolumny -> lista_słownikowa_id
        
    def set_column_type(self, column_name, column_type, dictionary_list_id=None):
        """Ustawia typ dla kolumny"""
        self.column_types[column_name] = column_type
        if dictionary_list_id:
            self.column_lists[column_name] = dictionary_list_id
    
    def createEditor(self, parent, option, index):
        """Tworzy odpowiedni edytor dla kolumny na podstawie typu"""
        try:
            # Pobierz nazwę kolumny z nagłówka
            column_name = index.model().headerData(index.column(), Qt.Orientation.Horizontal)
            column_type = self.column_types.get(column_name, "Tekstowa")
            
            # Dla kolumny TAG zachowaj kolorowanie poprzez specjalną obsługę
            if column_name == "TAG" and column_type == "Lista":
                editor = QComboBox(parent)
                editor.setEditable(False)  # Nie pozwalaj na wpisywanie własnych wartości
                
                # Załaduj elementy listy słownikowej
                if column_name in self.column_lists and self.db_manager:
                    list_id = self.column_lists[column_name]
                    items = self.db_manager.get_dictionary_list_items(list_id)
                    if items:
                        # Wyciągnij tylko wartości z tupli (id, value, order_index)
                        values = [item[1] for item in items]  # item[1] to wartość
                        editor.addItems(values)
                
                # Zastosuj styl
                if self.theme_manager:
                    editor.setStyleSheet(self.theme_manager.get_combo_style())
                
                return editor
            
            # Wybierz edytor na podstawie typu kolumny
            if column_type == "Lista":
                editor = QComboBox(parent)
                editor.setEditable(False)  # Nie pozwalaj na wpisywanie własnych wartości
                
                # Załaduj elementy listy słownikowej
                if column_name in self.column_lists and self.db_manager:
                    list_id = self.column_lists[column_name]
                    items = self.db_manager.get_dictionary_list_items(list_id)
                    if items:
                        # Wyciągnij tylko wartości z tupli (id, value, order_index)
                        values = [item[1] for item in items]  # item[1] to wartość
                        editor.addItems(values)
                
                # Zastosuj styl
                if self.theme_manager:
                    editor.setStyleSheet(self.theme_manager.get_combo_style())
                
                return editor
                
            elif column_type == "Data":
                editor = QDateTimeEdit(parent)
                editor.setCalendarPopup(True)
                editor.setDisplayFormat("dd.MM.yyyy HH:mm")
                editor.setDateTime(QDateTime.currentDateTime())
                
                # Zastosuj styl
                if self.theme_manager:
                    editor.setStyleSheet(self.theme_manager.get_date_edit_style())
                
                return editor
                
            elif column_type == "Liczbowa":
                editor = QSpinBox(parent)
                editor.setRange(-999999999, 999999999)
                
                # Zastosuj styl
                if self.theme_manager:
                    editor.setStyleSheet(self.theme_manager.get_spin_box_style())
                
                return editor
                
            elif column_type == "Waluta":
                editor = QLineEdit(parent)
                editor.setPlaceholderText("0.00")
                
                # Zastosuj styl
                if self.theme_manager:
                    editor.setStyleSheet(self.theme_manager.get_line_edit_style())
                
                return editor
                
            elif column_type == "CheckBox":
                # CheckBox jest już obsługiwany jako widget w komórce, nie jako delegat
                return None
                
            else:  # Tekstowa lub inne
                editor = QLineEdit(parent)
                
                # Zastosuj styl
                if self.theme_manager:
                    editor.setStyleSheet(self.theme_manager.get_line_edit_style())
                
                return editor
                
        except Exception as e:
            print(f"Błąd tworzenia edytora: {e}")
            import traceback
            traceback.print_exc()
            return super().createEditor(parent, option, index)
    
    def setEditorData(self, editor, index):
        """Ustawia dane w edytorze na podstawie wartości w modelu"""
        try:
            column_name = index.model().headerData(index.column(), Qt.Orientation.Horizontal)
            column_type = self.column_types.get(column_name, "Tekstowa")
            value = index.model().data(index, Qt.ItemDataRole.EditRole)
            
            if column_type == "Lista":
                if isinstance(editor, QComboBox):
                    if value:
                        index_in_combo = editor.findText(str(value))
                        if index_in_combo >= 0:
                            editor.setCurrentIndex(index_in_combo)
                            
            elif column_type == "Data":
                if isinstance(editor, QDateTimeEdit):
                    if value:
                        # Spróbuj sparsować datę
                        try:
                            if isinstance(value, str):
                                # Format: "dd.MM.yyyy HH:mm"
                                dt = QDateTime.fromString(value, "dd.MM.yyyy HH:mm")
                                if dt.isValid():
                                    editor.setDateTime(dt)
                        except:
                            pass
                            
            elif column_type == "Liczbowa":
                if isinstance(editor, QSpinBox):
                    try:
                        editor.setValue(int(value) if value else 0)
                    except:
                        editor.setValue(0)
                        
            elif column_type == "Waluta":
                if isinstance(editor, QLineEdit):
                    editor.setText(str(value) if value else "0.00")
                    
            else:  # Tekstowa
                if isinstance(editor, QLineEdit):
                    editor.setText(str(value) if value else "")
                    
        except Exception as e:
            print(f"Błąd ustawiania danych edytora: {e}")
            import traceback
            traceback.print_exc()
            super().setEditorData(editor, index)
    
    def setModelData(self, editor, model, index):
        """Zapisuje dane z edytora do modelu"""
        try:
            column_name = model.headerData(index.column(), Qt.Orientation.Horizontal)
            column_type = self.column_types.get(column_name, "Tekstowa")
            
            if column_type == "Lista":
                if isinstance(editor, QComboBox):
                    model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)
                    
            elif column_type == "Data":
                if isinstance(editor, QDateTimeEdit):
                    dt = editor.dateTime()
                    model.setData(index, dt.toString("dd.MM.yyyy HH:mm"), Qt.ItemDataRole.EditRole)
                    
            elif column_type == "Liczbowa":
                if isinstance(editor, QSpinBox):
                    model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)
                    
            elif column_type == "Waluta":
                if isinstance(editor, QLineEdit):
                    model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
                    
            else:  # Tekstowa
                if isinstance(editor, QLineEdit):
                    model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
                    
        except Exception as e:
            print(f"Błąd zapisywania danych z edytora: {e}")
            import traceback
            traceback.print_exc()
            super().setModelData(editor, model, index)
    
    def updateEditorGeometry(self, editor, option, index):
        """Aktualizuje geometrię edytora"""
        editor.setGeometry(option.rect)
        
    def paint(self, painter, option, index):
        """Niestandardowe malowanie komórki, aby uwzględnić kolor tła."""
        background_role = index.data(Qt.ItemDataRole.BackgroundRole)

        # Przygotuj kopię opcji, aby nie modyfikować oryginału przekazanego przez Qt
        option_copy = QStyleOptionViewItem(option)

        brush = None
        if isinstance(background_role, QBrush):
            brush = background_role
        elif isinstance(background_role, QColor):
            brush = QBrush(background_role)

        if brush is not None:
            painter.save()
            painter.fillRect(option.rect, brush)
            painter.restore()
            option_copy.backgroundBrush = QBrush(Qt.BrushStyle.NoBrush)

        super().paint(painter, option_copy, index)

    def sizeHint(self, option, index):
        """Zwraca preferowany rozmiar dla komórki."""
        # Można tu dodać logikę dopasowującą rozmiar, jeśli jest potrzebna
        return super().sizeHint(option, index)
