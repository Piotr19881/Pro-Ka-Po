"""
System alarmów i powiadomień w aplikacji Pro-Ka-Po V2
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel, 
                             QGroupBox, QCheckBox, QComboBox, QSpinBox,
                             QTimeEdit, QDateEdit, QFrame, QListWidget,
                             QListWidgetItem, QMessageBox, QSystemTrayIcon,
                             QMenu, QApplication, QWidget)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate, QDateTime, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont
import datetime

class AlarmPopup(QDialog):
    """Popup alarmu z opcjami akcji"""
    
    # Sygnały
    alarm_snoozed = pyqtSignal(int)  # Snooze na X minut
    alarm_dismissed = pyqtSignal()   # Odrzuć alarm
    
    def __init__(self, parent=None, alarm_data=None):
        super().__init__(parent)
        self.alarm_data = alarm_data or {}
        
        self.setWindowTitle("⏰ ALARM")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.Dialog | 
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.WindowCloseButtonHint)
        
        self.init_ui()
        self.setup_animations()
    
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Nagłówek z ikoną alarmu
        self.create_header_section(layout)
        
        # Informacje o alarmie
        self.create_alarm_info_section(layout)
        
        # Opcje snooze
        self.create_snooze_section(layout)
        
        # Przyciski akcji
        self.create_action_buttons(layout)
    
    def create_header_section(self, parent_layout):
        """Tworzy sekcję nagłówka z ikoną"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #ff6b6b;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Ikona alarmu (emoji lub tekst)
        alarm_icon = QLabel("🔔")
        alarm_icon.setFont(QFont("Arial", 24))
        alarm_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alarm_icon.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(alarm_icon)
        
        # Tekst alarmu
        alarm_title = QLabel("ALARM!")
        alarm_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        alarm_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alarm_title.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(alarm_title)
        
        # Czas alarmu
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        time_label = QLabel(current_time)
        time_label.setFont(QFont("Arial", 12))
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(time_label)
        
        parent_layout.addWidget(header_frame)
    
    def create_alarm_info_section(self, parent_layout):
        """Tworzy sekcję informacji o alarmie"""
        info_group = QGroupBox("Szczegóły alarmu")
        info_layout = QFormLayout(info_group)
        
        # Tytuł zadania
        task_title = self.alarm_data.get('task_title', 'Bez tytułu')
        title_label = QLabel(task_title)
        title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        info_layout.addRow("Zadanie:", title_label)
        
        # Opis alarmu
        alarm_desc = self.alarm_data.get('alarm_description', 'Brak opisu')
        desc_label = QLabel(alarm_desc)
        desc_label.setWordWrap(True)
        info_layout.addRow("Opis:", desc_label)
        
        # Czas alarmu
        alarm_time = self.alarm_data.get('alarm_time', 'Nieznany')
        time_label = QLabel(str(alarm_time))
        info_layout.addRow("Czas alarmu:", time_label)
        
        # Kategoria
        category = self.alarm_data.get('category', 'Ogólne')
        category_label = QLabel(category)
        info_layout.addRow("Kategoria:", category_label)
        
        parent_layout.addWidget(info_group)
    
    def create_snooze_section(self, parent_layout):
        """Tworzy sekcję opcji snooze"""
        snooze_group = QGroupBox("Opcje drzemki")
        snooze_layout = QHBoxLayout(snooze_group)
        
        snooze_layout.addWidget(QLabel("Przypomnij za:"))
        
        # Combo box z opcjami snooze
        self.snooze_combo = QComboBox()
        self.snooze_combo.addItems([
            "5 minut", "10 minut", "15 minut", 
            "30 minut", "1 godzina", "2 godziny"
        ])
        self.snooze_combo.setCurrentText("10 minut")
        snooze_layout.addWidget(self.snooze_combo)
        
        snooze_layout.addStretch()
        
        parent_layout.addWidget(snooze_group)
    
    def create_action_buttons(self, parent_layout):
        """Tworzy przyciski akcji"""
        buttons_layout = QHBoxLayout()
        
        # Przycisk Snooze
        self.snooze_btn = QPushButton("💤 Drzemka")
        self.snooze_btn.clicked.connect(self.snooze_alarm)
        self.snooze_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45B7B8;
            }
        """)
        buttons_layout.addWidget(self.snooze_btn)
        
        # Przycisk Odrzuć
        self.dismiss_btn = QPushButton("✖ Odrzuć")
        self.dismiss_btn.clicked.connect(self.dismiss_alarm)
        self.dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        buttons_layout.addWidget(self.dismiss_btn)
        
        # Przycisk Pokaż zadanie
        self.show_task_btn = QPushButton("📝 Pokaż zadanie")
        self.show_task_btn.clicked.connect(self.show_task)
        self.show_task_btn.setStyleSheet("""
            QPushButton {
                background-color: #A8E6CF;
                color: #2C3E50;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7FB069;
            }
        """)
        buttons_layout.addWidget(self.show_task_btn)
        
        parent_layout.addLayout(buttons_layout)
    
    def setup_animations(self):
        """Konfiguruje animacje i efekty"""
        # Timer do migania okna
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_window)
        self.blink_timer.start(1000)  # Migaj co sekundę
        
        self.blink_state = False
    
    def blink_window(self):
        """Miganie okna dla zwrócenia uwagi"""
        if self.blink_state:
            self.setStyleSheet("")
        else:
            self.setStyleSheet("QDialog { border: 3px solid #ff6b6b; }")
        
        self.blink_state = not self.blink_state
    
    def snooze_alarm(self):
        """Obsługuje snooze alarmu"""
        snooze_text = self.snooze_combo.currentText()
        
        # Konwertuj tekst na minuty
        snooze_minutes = {
            "5 minut": 5,
            "10 minut": 10,
            "15 minut": 15,
            "30 minut": 30,
            "1 godzina": 60,
            "2 godziny": 120
        }.get(snooze_text, 10)
        
        self.blink_timer.stop()
        self.alarm_snoozed.emit(snooze_minutes)
        self.accept()
    
    def dismiss_alarm(self):
        """Obsługuje odrzucenie alarmu"""
        self.blink_timer.stop()
        self.alarm_dismissed.emit()
        self.accept()
    
    def show_task(self):
        """Pokazuje szczegóły zadania"""
        # TODO: Otwórz główne okno i przejdź do zadania
        self.blink_timer.stop()
        self.accept()
    
    def closeEvent(self, a0):
        """Obsługuje zamknięcie okna"""
        self.blink_timer.stop()
        super().closeEvent(a0)

class AlarmManager:
    """Manager do zarządzania alarmami"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.active_alarms = []
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_alarms)
        self.check_timer.start(10000)  # Sprawdzaj co 10 sekund
        
        self.setup_system_tray()
    
    def setup_system_tray(self):
        """Konfiguruje ikonę w zasobniku systemowym"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon()
            
            # TODO: Dodaj właściwą ikonę
            # icon = QIcon("path/to/icon.png")
            # self.tray_icon.setIcon(icon)
            
            # Menu kontekstowe
            tray_menu = QMenu()
            
            show_action = tray_menu.addAction("Pokaż aplikację")
            if show_action:
                show_action.triggered.connect(self.show_main_window)
            
            tray_menu.addSeparator()
            
            quit_action = tray_menu.addAction("Zakończ")
            if quit_action:
                quit_action.triggered.connect(QApplication.quit)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def add_alarm(self, alarm_data):
        """Dodaje nowy alarm"""
        self.active_alarms.append(alarm_data)
    
    def remove_alarm(self, alarm_id):
        """Usuwa alarm"""
        self.active_alarms = [alarm for alarm in self.active_alarms 
                             if alarm.get('id') != alarm_id]
    
    def check_alarms(self):
        """Sprawdza czy któryś alarm powinien zostać uruchomiony"""
        current_time = QDateTime.currentDateTime()
        
        for alarm in self.active_alarms[:]:  # Kopia listy
            alarm_time = alarm.get('datetime')
            if alarm_time and current_time >= alarm_time:
                self.trigger_alarm(alarm)
                self.active_alarms.remove(alarm)
    
    def trigger_alarm(self, alarm_data):
        """Uruchamia alarm"""
        # Pokaż popup alarmu
        popup = AlarmPopup(self.parent, alarm_data)
        popup.alarm_snoozed.connect(lambda minutes: self.snooze_alarm(alarm_data, minutes))
        popup.alarm_dismissed.connect(lambda: self.dismiss_alarm(alarm_data))
        
        # Pokaż powiadomienie systemowe
        if hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage(
                "Pro-Ka-Po Alarm",
                f"Alarm: {alarm_data.get('task_title', 'Zadanie')}",
                QSystemTrayIcon.MessageIcon.Information,
                5000  # 5 sekund
            )
        
        popup.show()
        popup.activateWindow()
        popup.raise_()
    
    def snooze_alarm(self, alarm_data, minutes):
        """Obsługuje snooze alarmu"""
        new_time = QDateTime.currentDateTime().addSecs(minutes * 60)
        alarm_data['datetime'] = new_time
        self.active_alarms.append(alarm_data)
        
        print(f"Alarm odłożony o {minutes} minut. Nowy czas: {new_time.toString()}")
    
    def dismiss_alarm(self, alarm_data):
        """Obsługuje odrzucenie alarmu"""
        print(f"Alarm odrzucony: {alarm_data.get('task_title', 'Nieznane zadanie')}")
    
    def show_main_window(self):
        """Pokazuje główne okno aplikacji"""
        if self.parent:
            self.parent.show()
            self.parent.activateWindow()
            self.parent.raise_()

class AlarmSettingsDialog(QDialog):
    """Dialog ustawień alarmu dla zadania"""
    
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.task_data = task_data
        
        self.setWindowTitle("Ustawienia alarmu")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        
        self.init_ui()
    
    def init_ui(self):
        """Inicjalizuje interfejs użytkownika"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Włączenie alarmu
        self.alarm_enabled = QCheckBox("Włącz alarm dla tego zadania")
        layout.addWidget(self.alarm_enabled)
        
        # Grupa ustawień alarmu
        self.alarm_group = QGroupBox("Ustawienia alarmu")
        self.alarm_group.setEnabled(False)
        alarm_layout = QFormLayout(self.alarm_group)
        
        # Data alarmu
        self.alarm_date = QDateEdit()
        self.alarm_date.setDate(QDate.currentDate())
        self.alarm_date.setCalendarPopup(True)
        alarm_layout.addRow("Data:", self.alarm_date)
        
        # Czas alarmu
        self.alarm_time = QTimeEdit()
        self.alarm_time.setTime(QTime.currentTime().addSecs(3600))  # +1 godzina
        alarm_layout.addRow("Godzina:", self.alarm_time)
        
        # Opis alarmu
        self.alarm_description = QTextEdit()
        self.alarm_description.setMaximumHeight(60)
        self.alarm_description.setPlaceholderText("Opcjonalny opis alarmu...")
        alarm_layout.addRow("Opis:", self.alarm_description)
        
        # Powtarzanie
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems([
            "Nie powtarzaj", "Codziennie", "Co tydzień", 
            "Co miesiąc", "Co rok"
        ])
        alarm_layout.addRow("Powtarzanie:", self.repeat_combo)
        
        layout.addWidget(self.alarm_group)
        
        # Podłączenie sygnałów
        self.alarm_enabled.toggled.connect(self.alarm_group.setEnabled)
        
        # Przyciski
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Zapisz")
        save_btn.clicked.connect(self.save_alarm)
        save_btn.setDefault(True)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def save_alarm(self):
        """Zapisuje ustawienia alarmu"""
        if self.alarm_enabled.isChecked():
            # Utwórz dane alarmu
            alarm_datetime = QDateTime(self.alarm_date.date(), self.alarm_time.time())
            
            alarm_data = {
                'id': f"alarm_{datetime.datetime.now().timestamp()}",
                'task_title': self.task_data.get('title', 'Zadanie') if self.task_data else 'Nowe zadanie',
                'alarm_description': self.alarm_description.toPlainText(),
                'datetime': alarm_datetime,
                'repeat': self.repeat_combo.currentText(),
                'category': self.task_data.get('category', 'Ogólne') if self.task_data else 'Ogólne'
            }
            
            # TODO: Zapisz alarm w systemie
            print(f"Alarm ustawiony: {alarm_data}")
        
        self.accept()