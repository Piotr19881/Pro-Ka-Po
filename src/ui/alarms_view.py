import sys
import os
import winsound
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QTimeEdit,
                             QDateEdit, QCheckBox, QComboBox, QSpinBox, QGroupBox,
                             QGridLayout, QTextEdit, QSlider, QProgressBar,
                             QTabWidget, QFrame, QSplitter, QScrollArea,
                             QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
                             QLineEdit, QFileDialog, QApplication)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate, QDateTime, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

class AlarmDialog(QDialog):
    """Dialog do dodawania/edycji alarmów"""
    
    def __init__(self, parent=None, alarm_data=None):
        super().__init__(parent)
        self.alarm_data = alarm_data
        self.is_edit_mode = alarm_data is not None
        
        self.setWindowTitle("Edytuj alarm" if self.is_edit_mode else "Dodaj nowy alarm")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_alarm_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Formularz alarmu
        form_layout = QFormLayout()
        
        # Nazwa alarmu
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nazwa alarmu...")
        form_layout.addRow("Nazwa:", self.name_edit)
        
        # Czas alarmu
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        form_layout.addRow("Czas:", self.time_edit)
        
        # Data (dla alarmu jednorazowego)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Data:", self.date_edit)
        
        # Typ alarmu
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Jednorazowy", "Codziennie", "Dni robocze", "Weekendy", "Niestandardowy"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form_layout.addRow("Typ:", self.type_combo)
        
        # Dni tygodnia (dla niestandardowego)
        self.days_widget = QWidget()
        days_layout = QHBoxLayout(self.days_widget)
        self.day_checkboxes = {}
        days = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nd"]
        for day in days:
            checkbox = QCheckBox(day)
            self.day_checkboxes[day] = checkbox
            days_layout.addWidget(checkbox)
        self.days_widget.setVisible(False)
        form_layout.addRow("Dni:", self.days_widget)
        
        # Aktywny
        self.active_checkbox = QCheckBox("Alarm aktywny")
        self.active_checkbox.setChecked(True)
        form_layout.addRow("", self.active_checkbox)
        
        # Notatka
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(60)
        self.note_edit.setPlaceholderText("Opcjonalna notatka...")
        form_layout.addRow("Notatka:", self.note_edit)
        
        layout.addLayout(form_layout)
        
        # Przyciski
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def on_type_changed(self, type_text):
        """Obsługuje zmianę typu alarmu"""
        self.date_edit.setVisible(type_text == "Jednorazowy")
        self.days_widget.setVisible(type_text == "Niestandardowy")
    
    def load_alarm_data(self):
        """Ładuje dane alarmu do edycji"""
        if self.alarm_data:
            self.name_edit.setText(self.alarm_data.get('name', ''))
            
            time_str = self.alarm_data.get('time', '00:00')
            time_obj = QTime.fromString(time_str, "HH:mm")
            self.time_edit.setTime(time_obj)
            
            self.type_combo.setCurrentText(self.alarm_data.get('type', 'Jednorazowy'))
            self.active_checkbox.setChecked(self.alarm_data.get('active', True))
            self.note_edit.setPlainText(self.alarm_data.get('note', ''))
    
    def get_alarm_data(self):
        """Zwraca dane alarmu z formularza"""
        return {
            'name': self.name_edit.text(),
            'time': self.time_edit.time().toString("HH:mm"),
            'date': self.date_edit.date().toString("yyyy-MM-dd") if self.type_combo.currentText() == "Jednorazowy" else None,
            'type': self.type_combo.currentText(),
            'active': self.active_checkbox.isChecked(),
            'note': self.note_edit.toPlainText(),
            'days': [day for day, checkbox in self.day_checkboxes.items() if checkbox.isChecked()] if self.type_combo.currentText() == "Niestandardowy" else []
        }

class TimerDialog(QDialog):
    """Dialog do ustawiania timera"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nowy timer")
        self.setModal(True)
        self.setMinimumSize(300, 200)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Formularz timera
        form_layout = QFormLayout()
        
        # Nazwa timera
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nazwa timera...")
        form_layout.addRow("Nazwa:", self.name_edit)
        
        # Czas timera
        timer_layout = QHBoxLayout()
        
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 23)
        self.hours_spin.setSuffix(" h")
        timer_layout.addWidget(self.hours_spin)
        
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setValue(5)
        self.minutes_spin.setSuffix(" min")
        timer_layout.addWidget(self.minutes_spin)
        
        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setSuffix(" s")
        timer_layout.addWidget(self.seconds_spin)
        
        form_layout.addRow("Czas:", timer_layout)
        
        layout.addLayout(form_layout)
        
        # Przyciski
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_timer_data(self):
        """Zwraca dane timera z formularza"""
        total_seconds = (self.hours_spin.value() * 3600 + 
                        self.minutes_spin.value() * 60 + 
                        self.seconds_spin.value())
        
        return {
            'name': self.name_edit.text() or f"Timer {total_seconds//60}min",
            'total_seconds': total_seconds,
            'remaining_seconds': total_seconds
        }

class AlarmsView(QWidget):
    """Główny widok alarmów z trzema sekcjami"""
    
    alarm_triggered = pyqtSignal(dict)  # Sygnał dla alarmów
    timer_finished = pyqtSignal(dict)   # Sygnał dla timerów
    
    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.alarms = []
        self.timers = []
        self.active_timers = {}  # QTimer objects for running timers
        
        # Audio
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Timer do sprawdzania alarmów
        self.alarm_check_timer = QTimer()
        self.alarm_check_timer.timeout.connect(self.check_alarms)
        self.alarm_check_timer.start(1000)  # Sprawdzaj co sekundę
        
        # Timer do odświeżania timerów
        self.timer_update_timer = QTimer()
        self.timer_update_timer.timeout.connect(self.update_timers)
        self.timer_update_timer.start(1000)  # Odświeżaj co sekundę
        
        self.init_ui()
        self.load_settings()
    
    def apply_theme(self):
        """Aplikuje motyw do widoku alarmów"""
        if not self.theme_manager:
            return
            
        # Pobierz słownik aktualnego motywu
        theme_dict = self.theme_manager.get_current_theme_dict()
        colors = self.theme_manager.get_current_colors()
        
        # Główne tło widoku z prawidłowym kolorem tekstu
        main_style = f"""
            AlarmsView {{
                background-color: {theme_dict['background']};
                color: {colors['text_color']};
                font-family: 'Segoe UI', sans-serif;
            }}
            AlarmsView QLabel {{
                color: {colors['text_color']} !important;
                background-color: transparent;
            }}
            AlarmsView QGroupBox {{
                color: {colors['text_color']};
                background-color: {colors['widget_bg']};
                border: 2px solid {colors['border_color']};
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                padding-top: 10px;
            }}
            AlarmsView QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: {colors['widget_bg']};
                color: {colors['text_color']};
            }}
        """
        
        self.setStyleSheet(main_style)
        
        # Aplikuj style do tabel
        if hasattr(self, 'alarms_table'):
            self.alarms_table.setStyleSheet(self.theme_manager.get_table_style())
        if hasattr(self, 'timers_table'):
            self.timers_table.setStyleSheet(self.theme_manager.get_table_style())
        
        # Aplikuj style do wszystkich komponentów
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(self.theme_manager.get_button_style())
        
        # NIE nadpisuj stylu GroupBox - użyj globalnego z main_style
        # for group_box in self.findChildren(QGroupBox):
        #     group_box.setStyleSheet(self.theme_manager.get_group_box_style())
        
        # NIE nadpisuj stylu Label - użyj globalnego z main_style
        # for label in self.findChildren(QLabel):
        #     label.setStyleSheet(self.theme_manager.get_label_style())
        
        # Zaktualizuj kolory etykiet w ustawieniach
        if hasattr(self, 'settings_labels'):
            label_color = colors['text_color']
            for label in self.settings_labels:
                label.setStyleSheet(f"color: {label_color};")
        
        # Zaktualizuj kolory checkboxów w ustawieniach
        if hasattr(self, 'boost_volume_checkbox'):
            checkbox_style = f"QCheckBox {{ color: {colors['text_color']}; }}"
            self.boost_volume_checkbox.setStyleSheet(checkbox_style)
        if hasattr(self, 'show_notification_checkbox'):
            checkbox_style = f"QCheckBox {{ color: {colors['text_color']}; }}"
            self.show_notification_checkbox.setStyleSheet(checkbox_style)
        if hasattr(self, 'repeat_alarm_checkbox'):
            checkbox_style = f"QCheckBox {{ color: {colors['text_color']}; }}"
            self.repeat_alarm_checkbox.setStyleSheet(checkbox_style)
        
        for combo in self.findChildren(QComboBox):
            combo.setStyleSheet(self.theme_manager.get_combo_style())
        
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setStyleSheet(self.theme_manager.get_checkbox_style())
        
        for spinbox in self.findChildren(QSpinBox):
            spinbox.setStyleSheet(self.theme_manager.get_spin_box_style())
        
        for time_edit in self.findChildren(QTimeEdit):
            time_edit.setStyleSheet(self.theme_manager.get_date_edit_style())
        
        for date_edit in self.findChildren(QDateEdit):
            date_edit.setStyleSheet(self.theme_manager.get_date_edit_style())
        
        for text_edit in self.findChildren(QTextEdit):
            text_edit.setStyleSheet(self.theme_manager.get_text_edit_style())
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Główny splitter poziomy
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Lewa sekcja - Tab widget dla alarmów i timerów
        self.tab_widget = QTabWidget()
        
        # Tab alarmów
        alarms_tab = self.create_alarms_tab()
        self.tab_widget.addTab(alarms_tab, "🔔 Alarmy")
        
        # Tab timerów
        timers_tab = self.create_timers_tab()
        self.tab_widget.addTab(timers_tab, "⏱️ Timery")
        
        main_splitter.addWidget(self.tab_widget)
        
        # Prawa sekcja - Ustawienia
        settings_widget = self.create_settings_section()
        main_splitter.addWidget(settings_widget)
        
        # Proporcje splittera - więcej miejsca dla alarmów/timerów, mniej dla ustawień
        main_splitter.setSizes([700, 350])
        
        layout.addWidget(main_splitter)
    
    def create_alarms_tab(self):
        """Tworzy zakładkę alarmów"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Przyciski akcji
        buttons_layout = QHBoxLayout()
        
        add_alarm_btn = QPushButton("➕ Dodaj alarm")
        add_alarm_btn.clicked.connect(self.add_alarm)
        buttons_layout.addWidget(add_alarm_btn)
        
        edit_alarm_btn = QPushButton("✏️ Edytuj")
        edit_alarm_btn.clicked.connect(self.edit_alarm)
        buttons_layout.addWidget(edit_alarm_btn)
        
        delete_alarm_btn = QPushButton("🗑️ Usuń")
        delete_alarm_btn.clicked.connect(self.delete_alarm)
        buttons_layout.addWidget(delete_alarm_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Tabela alarmów
        self.alarms_table = QTableWidget()
        self.alarms_table.setColumnCount(5)
        self.alarms_table.setHorizontalHeaderLabels(["Nazwa", "Czas", "Typ", "Aktywny", "Notatka"])
        
        # Konfiguracja tabeli
        header = self.alarms_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        self.alarms_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.alarms_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.alarms_table)
        
        return widget
    
    def create_timers_tab(self):
        """Tworzy zakładkę timerów"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Przyciski akcji
        buttons_layout = QHBoxLayout()
        
        add_timer_btn = QPushButton("➕ Dodaj timer")
        add_timer_btn.clicked.connect(self.add_timer)
        buttons_layout.addWidget(add_timer_btn)
        
        start_timer_btn = QPushButton("▶️ Start")
        start_timer_btn.clicked.connect(self.start_timer)
        buttons_layout.addWidget(start_timer_btn)
        
        pause_timer_btn = QPushButton("⏸️ Pauza")
        pause_timer_btn.clicked.connect(self.pause_timer)
        buttons_layout.addWidget(pause_timer_btn)
        
        stop_timer_btn = QPushButton("⏹️ Stop")
        stop_timer_btn.clicked.connect(self.stop_timer)
        buttons_layout.addWidget(stop_timer_btn)
        
        delete_timer_btn = QPushButton("🗑️ Usuń")
        delete_timer_btn.clicked.connect(self.delete_timer)
        buttons_layout.addWidget(delete_timer_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Tabela timerów
        self.timers_table = QTableWidget()
        self.timers_table.setColumnCount(4)
        self.timers_table.setHorizontalHeaderLabels(["Nazwa", "Czas całkowity", "Pozostało", "Status"])
        
        # Konfiguracja tabeli
        header = self.timers_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        self.timers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.timers_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.timers_table)
        
        return widget
    
    def create_settings_section(self):
        """Tworzy sekcję ustawień"""
        settings_group = QGroupBox("⚙️ Ustawienia")
        layout = QVBoxLayout(settings_group)
        
        # Lista do przechowywania etykiet dla późniejszego stosowania motywu
        self.settings_labels = []
        
        # Dźwięki alarmów
        alarm_sound_layout = QFormLayout()
        
        # Etykieta dla dźwięku alarmu
        alarm_sound_label = QLabel("Dźwięk alarmu:")
        alarm_sound_label.setStyleSheet("color: #2c3e50;")  # Bezpośrednie ustawienie koloru
        self.settings_labels.append(alarm_sound_label)
        
        self.alarm_sound_combo = QComboBox()
        self.alarm_sound_combo.addItems([
            "Systemowy beep",
            "Alarm klasyczny", 
            "Alarm cyfrowy",
            "Budzik retro",
            "Dzwonek telefonu",
            "Własny plik..."
        ])
        self.alarm_sound_combo.currentTextChanged.connect(self.on_alarm_sound_changed)
        alarm_sound_layout.addRow(alarm_sound_label, self.alarm_sound_combo)
        
        # Przycisk test dźwięku alarmu
        test_alarm_sound_btn = QPushButton("🔊 Test alarmu")
        test_alarm_sound_btn.clicked.connect(self.test_alarm_sound)
        alarm_sound_layout.addRow("", test_alarm_sound_btn)
        
        layout.addLayout(alarm_sound_layout)
        
        # Separator
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)
        
        # Dźwięki timerów
        timer_sound_layout = QFormLayout()
        
        # Etykieta dla dźwięku timera
        timer_sound_label = QLabel("Dźwięk timera:")
        timer_sound_label.setStyleSheet("color: #2c3e50;")  # Bezpośrednie ustawienie koloru
        self.settings_labels.append(timer_sound_label)
        
        self.timer_sound_combo = QComboBox()
        self.timer_sound_combo.addItems([
            "Systemowy beep",
            "Dzwonek kuchenny", 
            "Gong",
            "Chime",
            "Brzęczyk",
            "Własny plik..."
        ])
        self.timer_sound_combo.currentTextChanged.connect(self.on_timer_sound_changed)
        timer_sound_layout.addRow(timer_sound_label, self.timer_sound_combo)
        
        # Przycisk test dźwięku timera
        test_timer_sound_btn = QPushButton("🔊 Test timera")
        test_timer_sound_btn.clicked.connect(self.test_timer_sound)
        timer_sound_layout.addRow("", test_timer_sound_btn)
        
        layout.addLayout(timer_sound_layout)
        
        # Separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)
        
        # Głośność
        volume_layout = QFormLayout()
        
        # Etykieta dla głośności
        volume_main_label = QLabel("Głośność:")
        volume_main_label.setStyleSheet("color: #2c3e50;")  # Bezpośrednie ustawienie koloru
        self.settings_labels.append(volume_main_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setStyleSheet("color: #2c3e50;")  # Bezpośrednie ustawienie koloru
        self.settings_labels.append(self.volume_label)
        
        volume_widget = QWidget()
        volume_widget_layout = QHBoxLayout(volume_widget)
        volume_widget_layout.addWidget(self.volume_slider)
        volume_widget_layout.addWidget(self.volume_label)
        volume_layout.addRow(volume_main_label, volume_widget)
        
        layout.addLayout(volume_layout)
        
        # Separator
        line3 = QFrame()
        line3.setFrameShape(QFrame.Shape.HLine)
        line3.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line3)
        
        # Opcje systemu
        system_layout = QFormLayout()
        
        self.boost_volume_checkbox = QCheckBox("Podgłośnij system gdy jest wyciszony")
        self.boost_volume_checkbox.setStyleSheet("QCheckBox { color: #2c3e50; }")
        system_layout.addRow("", self.boost_volume_checkbox)
        
        self.show_notification_checkbox = QCheckBox("Pokaż powiadomienie systemowe")
        self.show_notification_checkbox.setChecked(True)
        self.show_notification_checkbox.setStyleSheet("QCheckBox { color: #2c3e50; }")
        system_layout.addRow("", self.show_notification_checkbox)
        
        self.repeat_alarm_checkbox = QCheckBox("Powtarzaj alarm co 5 minut")
        self.repeat_alarm_checkbox.setStyleSheet("QCheckBox { color: #2c3e50; }")
        system_layout.addRow("", self.repeat_alarm_checkbox)
        
        layout.addLayout(system_layout)
        
        # Przycisk zapisz ustawienia
        save_settings_btn = QPushButton("💾 Zapisz ustawienia")
        save_settings_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_settings_btn)
        
        layout.addStretch()
        
        return settings_group
    
    # === METODY ALARMÓW ===
    def add_alarm(self):
        """Dodaje nowy alarm"""
        dialog = AlarmDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            alarm_data = dialog.get_alarm_data()
            alarm_data['id'] = len(self.alarms) + 1
            self.alarms.append(alarm_data)
            self.refresh_alarms_table()
            print(f"Dodano alarm: {alarm_data['name']}")
    
    def edit_alarm(self):
        """Edytuje wybrany alarm"""
        current_row = self.alarms_table.currentRow()
        if current_row >= 0 and current_row < len(self.alarms):
            alarm_data = self.alarms[current_row]
            dialog = AlarmDialog(self, alarm_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_alarm_data()
                updated_data['id'] = alarm_data['id']
                self.alarms[current_row] = updated_data
                self.refresh_alarms_table()
                print(f"Zaktualizowano alarm: {updated_data['name']}")
    
    def delete_alarm(self):
        """Usuwa wybrany alarm"""
        current_row = self.alarms_table.currentRow()
        if current_row >= 0 and current_row < len(self.alarms):
            alarm = self.alarms[current_row]
            reply = QMessageBox.question(self, "Usuń alarm", 
                                       f"Czy na pewno chcesz usunąć alarm '{alarm['name']}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.alarms[current_row]
                self.refresh_alarms_table()
                print(f"Usunięto alarm: {alarm['name']}")
    
    def refresh_alarms_table(self):
        """Odświeża tabelę alarmów"""
        self.alarms_table.setRowCount(len(self.alarms))
        
        for row, alarm in enumerate(self.alarms):
            self.alarms_table.setItem(row, 0, QTableWidgetItem(alarm['name']))
            self.alarms_table.setItem(row, 1, QTableWidgetItem(alarm['time']))
            self.alarms_table.setItem(row, 2, QTableWidgetItem(alarm['type']))
            self.alarms_table.setItem(row, 3, QTableWidgetItem("Tak" if alarm['active'] else "Nie"))
            self.alarms_table.setItem(row, 4, QTableWidgetItem(alarm.get('note', '')))
    
    # === METODY TIMERÓW ===
    def add_timer(self):
        """Dodaje nowy timer"""
        dialog = TimerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            timer_data = dialog.get_timer_data()
            if timer_data['total_seconds'] > 0:
                timer_data['id'] = len(self.timers) + 1
                timer_data['status'] = 'Zatrzymany'
                self.timers.append(timer_data)
                self.refresh_timers_table()
                print(f"Dodano timer: {timer_data['name']}")
            else:
                QMessageBox.warning(self, "Błąd", "Timer musi mieć czas większy niż 0!")
    
    def start_timer(self):
        """Rozpoczyna wybrany timer"""
        current_row = self.timers_table.currentRow()
        if current_row >= 0 and current_row < len(self.timers):
            timer_data = self.timers[current_row]
            timer_id = timer_data['id']
            
            if timer_id not in self.active_timers:
                # Utwórz nowy QTimer
                qt_timer = QTimer()
                qt_timer.timeout.connect(lambda: self.timer_tick(timer_id))
                self.active_timers[timer_id] = qt_timer
                qt_timer.start(1000)  # Co sekundę
                
                timer_data['status'] = 'Aktywny'
                self.refresh_timers_table()
                print(f"Uruchomiono timer: {timer_data['name']}")
    
    def pause_timer(self):
        """Pauzuje wybrany timer"""
        current_row = self.timers_table.currentRow()
        if current_row >= 0 and current_row < len(self.timers):
            timer_data = self.timers[current_row]
            timer_id = timer_data['id']
            
            if timer_id in self.active_timers:
                self.active_timers[timer_id].stop()
                del self.active_timers[timer_id]
                timer_data['status'] = 'Pauzowany'
                self.refresh_timers_table()
                print(f"Spauzowano timer: {timer_data['name']}")
    
    def stop_timer(self):
        """Zatrzymuje i resetuje wybrany timer"""
        current_row = self.timers_table.currentRow()
        if current_row >= 0 and current_row < len(self.timers):
            timer_data = self.timers[current_row]
            timer_id = timer_data['id']
            
            if timer_id in self.active_timers:
                self.active_timers[timer_id].stop()
                del self.active_timers[timer_id]
            
            # Reset timera
            timer_data['remaining_seconds'] = timer_data['total_seconds']
            timer_data['status'] = 'Zatrzymany'
            self.refresh_timers_table()
            print(f"Zatrzymano timer: {timer_data['name']}")
    
    def delete_timer(self):
        """Usuwa wybrany timer"""
        current_row = self.timers_table.currentRow()
        if current_row >= 0 and current_row < len(self.timers):
            timer_data = self.timers[current_row]
            reply = QMessageBox.question(self, "Usuń timer", 
                                       f"Czy na pewno chcesz usunąć timer '{timer_data['name']}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                timer_id = timer_data['id']
                
                # Zatrzymaj timer jeśli jest aktywny
                if timer_id in self.active_timers:
                    self.active_timers[timer_id].stop()
                    del self.active_timers[timer_id]
                
                del self.timers[current_row]
                self.refresh_timers_table()
                print(f"Usunięto timer: {timer_data['name']}")
    
    def timer_tick(self, timer_id):
        """Obsługuje tick timera"""
        # Znajdź timer o danym ID
        timer_data = None
        for timer in self.timers:
            if timer['id'] == timer_id:
                timer_data = timer
                break
        
        if timer_data:
            timer_data['remaining_seconds'] -= 1
            
            if timer_data['remaining_seconds'] <= 0:
                # Timer zakończony
                self.timer_finished.emit(timer_data)
                self.play_timer_sound()  # Użyj dźwięku timera
                
                # Zatrzymaj timer
                if timer_id in self.active_timers:
                    self.active_timers[timer_id].stop()
                    del self.active_timers[timer_id]
                
                timer_data['status'] = 'Zakończony'
                
                # Pokaż powiadomienie
                QMessageBox.information(self, "Timer zakończony", 
                                      f"Timer '{timer_data['name']}' został zakończony!")
            
            self.refresh_timers_table()
    
    def refresh_timers_table(self):
        """Odświeża tabelę timerów"""
        self.timers_table.setRowCount(len(self.timers))
        
        for row, timer in enumerate(self.timers):
            self.timers_table.setItem(row, 0, QTableWidgetItem(timer['name']))
            
            # Czas całkowity
            total_time = self.format_time(timer['total_seconds'])
            self.timers_table.setItem(row, 1, QTableWidgetItem(total_time))
            
            # Pozostały czas
            remaining_time = self.format_time(timer['remaining_seconds'])
            self.timers_table.setItem(row, 2, QTableWidgetItem(remaining_time))
            
            # Status
            self.timers_table.setItem(row, 3, QTableWidgetItem(timer['status']))
    
    def update_timers(self):
        """Odświeża wyświetlanie timerów"""
        if self.timers:
            self.refresh_timers_table()
    
    def format_time(self, seconds):
        """Formatuje sekundy na HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    # === METODY USTAWIEŃ ===
    def on_alarm_sound_changed(self, sound_name):
        """Obsługuje zmianę dźwięku alarmu"""
        if sound_name == "Własny plik...":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Wybierz plik dźwiękowy dla alarmu", "", 
                "Pliki audio (*.mp3 *.wav *.ogg *.m4a *.aac)")
            if file_path:
                self.custom_alarm_sound_path = file_path
                print(f"Wybrano własny dźwięk alarmu: {file_path}")
    
    def on_timer_sound_changed(self, sound_name):
        """Obsługuje zmianę dźwięku timera"""
        if sound_name == "Własny plik...":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Wybierz plik dźwiękowy dla timera", "", 
                "Pliki audio (*.mp3 *.wav *.ogg *.m4a *.aac)")
            if file_path:
                self.custom_timer_sound_path = file_path
                print(f"Wybrano własny dźwięk timera: {file_path}")
    
    def on_volume_changed(self, value):
        """Obsługuje zmianę głośności"""
        self.volume_label.setText(f"{value}%")
        self.audio_output.setVolume(value / 100.0)
    
    def test_alarm_sound(self):
        """Testuje dźwięk alarmu"""
        self.play_alarm_sound()
        print("Test dźwięku alarmu")
    
    def test_timer_sound(self):
        """Testuje dźwięk timera"""
        self.play_timer_sound()
        print("Test dźwięku timera")
    
    def get_system_beep_sound(self):
        """Odtwarza systemowy beep"""
        try:
            QApplication.beep()
            return True
        except:
            return False
    
    def play_alarm_sound(self):
        """Odtwarza dźwięk alarmu"""
        try:
            sound_name = self.alarm_sound_combo.currentText()
            
            if sound_name == "Systemowy beep":
                self.get_system_beep_sound()
                return
            elif sound_name == "Własny plik..." and hasattr(self, 'custom_alarm_sound_path'):
                sound_url = QUrl.fromLocalFile(self.custom_alarm_sound_path)
            else:
                # Mapowanie dźwięków systemowych Windows
                sound_map = {
                    "Alarm klasyczny": "SystemHand",
                    "Alarm cyfrowy": "SystemExclamation", 
                    "Budzik retro": "SystemQuestion",
                    "Dzwonek telefonu": "SystemAsterisk"
                }
                
                # Spróbuj odtworzyć dźwięk systemowy Windows
                if sound_name in sound_map:
                    import winsound
                    try:
                        winsound.PlaySound(sound_map[sound_name], winsound.SND_ALIAS | winsound.SND_ASYNC)
                        return
                    except:
                        pass
                
                # Fallback do beep
                self.get_system_beep_sound()
                return
            
            # Odtwórz własny plik
            self.media_player.setSource(sound_url)
            self.media_player.play()
            
        except Exception as e:
            print(f"Błąd odtwarzania dźwięku alarmu: {e}")
            self.get_system_beep_sound()
    
    def play_timer_sound(self):
        """Odtwarza dźwięk timera"""
        try:
            sound_name = self.timer_sound_combo.currentText()
            
            if sound_name == "Systemowy beep":
                self.get_system_beep_sound()
                return
            elif sound_name == "Własny plik..." and hasattr(self, 'custom_timer_sound_path'):
                sound_url = QUrl.fromLocalFile(self.custom_timer_sound_path)
            else:
                # Mapowanie dźwięków systemowych Windows dla timerów
                sound_map = {
                    "Dzwonek kuchenny": "SystemHand",
                    "Gong": "SystemExclamation",
                    "Chime": "SystemAsterisk", 
                    "Brzęczyk": "SystemQuestion"
                }
                
                # Spróbuj odtworzyć dźwięk systemowy Windows
                if sound_name in sound_map:
                    import winsound
                    try:
                        winsound.PlaySound(sound_map[sound_name], winsound.SND_ALIAS | winsound.SND_ASYNC)
                        return
                    except:
                        pass
                
                # Fallback do beep
                self.get_system_beep_sound()
                return
            
            # Odtwórz własny plik
            self.media_player.setSource(sound_url)
            self.media_player.play()
            
        except Exception as e:
            print(f"Błąd odtwarzania dźwięku timera: {e}")
            self.get_system_beep_sound()
    
    def check_alarms(self):
        """Sprawdza czy któryś alarm powinien być uruchomiony"""
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        current_datetime = QDateTime.currentDateTime()
        
        for alarm in self.alarms:
            if not alarm['active']:
                continue
                
            alarm_time = QTime.fromString(alarm['time'], "HH:mm")
            
            # Sprawdź czy to czas na alarm
            should_trigger = False
            
            if alarm['type'] == "Jednorazowy":
                alarm_date = QDate.fromString(alarm.get('date', ''), "yyyy-MM-dd")
                if current_date == alarm_date and current_time.hour() == alarm_time.hour() and current_time.minute() == alarm_time.minute():
                    should_trigger = True
                    
            elif alarm['type'] == "Codziennie":
                if current_time.hour() == alarm_time.hour() and current_time.minute() == alarm_time.minute():
                    should_trigger = True
                    
            elif alarm['type'] == "Dni robocze":
                weekday = current_date.dayOfWeek()  # 1-7, gdzie 1=poniedziałek
                if weekday <= 5 and current_time.hour() == alarm_time.hour() and current_time.minute() == alarm_time.minute():
                    should_trigger = True
                    
            elif alarm['type'] == "Weekendy":
                weekday = current_date.dayOfWeek()
                if weekday >= 6 and current_time.hour() == alarm_time.hour() and current_time.minute() == alarm_time.minute():
                    should_trigger = True
            
            if should_trigger:
                # Sprawdź czy alarm nie był już uruchomiony w tej minucie
                alarm_key = f"{alarm['id']}_{current_datetime.toString('yyyy-MM-dd_HH:mm')}"
                if not hasattr(self, 'triggered_alarms'):
                    self.triggered_alarms = set()
                
                if alarm_key not in self.triggered_alarms:
                    self.triggered_alarms.add(alarm_key)
                    self.trigger_alarm(alarm)
    
    def trigger_alarm(self, alarm):
        """Uruchamia alarm"""
        self.alarm_triggered.emit(alarm)
        self.play_alarm_sound()
        
        # Pokaż powiadomienie
        if self.show_notification_checkbox.isChecked():
            QMessageBox.information(self, "ALARM!", 
                                  f"⏰ {alarm['name']}\n\n{alarm.get('note', '')}")
        
        print(f"ALARM: {alarm['name']} - {alarm['time']}")
    
    def load_settings(self):
        """Ładuje ustawienia z pliku"""
        default_settings = {
            'alarm_sound': 'Systemowy Błąd',
            'timer_sound': 'Systemowy Asterisk',
            'volume': 70,
            'boost_volume': False,
            'show_notification': True,
            'repeat_alarm': False,
            'custom_alarm_sound_path': '',
            'custom_timer_sound_path': ''
        }
        
        # Tu można dodać wczytywanie z pliku JSON lub bazy danych
        settings = default_settings
        
        # Ustawianie wartości w kontrolkach
        alarm_index = self.alarm_sound_combo.findText(settings['alarm_sound'])
        if alarm_index >= 0:
            self.alarm_sound_combo.setCurrentIndex(alarm_index)
            
        timer_index = self.timer_sound_combo.findText(settings['timer_sound'])
        if timer_index >= 0:
            self.timer_sound_combo.setCurrentIndex(timer_index)
            
        self.volume_slider.setValue(settings['volume'])
        self.boost_volume_checkbox.setChecked(settings['boost_volume'])
        self.show_notification_checkbox.setChecked(settings['show_notification'])
        self.repeat_alarm_checkbox.setChecked(settings['repeat_alarm'])
        
        self.custom_alarm_sound_path = settings['custom_alarm_sound_path']
        self.custom_timer_sound_path = settings['custom_timer_sound_path']
        
        print("Ustawienia wczytane:", settings)
    
    def save_settings(self):
        """Zapisuje ustawienia do pliku"""
        settings = {
            'alarm_sound': self.alarm_sound_combo.currentText(),
            'timer_sound': self.timer_sound_combo.currentText(),
            'volume': self.volume_slider.value(),
            'boost_volume': self.boost_volume_checkbox.isChecked(),
            'show_notification': self.show_notification_checkbox.isChecked(),
            'repeat_alarm': self.repeat_alarm_checkbox.isChecked(),
            'custom_alarm_sound_path': getattr(self, 'custom_alarm_sound_path', ''),
            'custom_timer_sound_path': getattr(self, 'custom_timer_sound_path', '')
        }
        
        # Tu można dodać zapis do pliku JSON lub bazy danych
        print("Ustawienia zapisane:", settings)
        QMessageBox.information(self, "Ustawienia", "Ustawienia zostały zapisane!")