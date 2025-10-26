from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QProgressBar, QGroupBox, QGridLayout,
                            QSpinBox, QCheckBox, QFrame, QApplication, QComboBox,
                            QFileDialog, QMessageBox)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
import time
import os

class PomodoroView(QWidget):
    """Widok techniki Pomodoro"""
    
    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.init_timer_state()
        self.setup_ui()
        self.load_settings()
        
    def apply_theme(self):
        """Aplikuje motyw do widoku Pomodoro"""
        if not self.theme_manager:
            return
            
        # Pobierz słownik aktualnego motywu
        theme_dict = self.theme_manager.get_current_theme_dict()
        
        # Główne tło widoku
        main_style = f"""
            PomodoroView {{
                background-color: {theme_dict['background']};
                color: {theme_dict['text']};
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
        """
        
        self.setStyleSheet(main_style)
        
        # Aplikuj theme do wszystkich komponentów
        self._apply_theme_to_components(theme_dict)
        
    def _apply_theme_to_components(self, theme_dict):
        """Aplikuje motyw do wszystkich komponentów Pomodoro"""
        
        # Timer widget (główny kontener timera)
        if hasattr(self, 'timer_widget'):
            timer_widget_style = f"""
                QWidget {{
                    background-color: {theme_dict['secondary_background']};
                    border-radius: 15px;
                    border: 2px solid {theme_dict['border']};
                }}
            """
            self.timer_widget.setStyleSheet(timer_widget_style)
        
        # Session label
        if hasattr(self, 'session_label'):
            session_label_style = f"""
                color: {theme_dict['text']};
                margin-bottom: 10px;
            """
            self.session_label.setStyleSheet(session_label_style)
        
        # Session counter label  
        if hasattr(self, 'session_counter_label'):
            counter_style = f"""
                color: {theme_dict['text']};
                margin-bottom: 20px;
            """
            self.session_counter_label.setStyleSheet(counter_style)
        
        # Time label (główny wyświetlacz czasu)
        if hasattr(self, 'time_label'):
            time_color = theme_dict['accent'] if self.theme_manager.current_theme == 'dark' else '#e74c3c'
            time_bg = theme_dict['secondary_background'] if self.theme_manager.current_theme == 'dark' else '#fef9f9'
            time_border = theme_dict['accent'] if self.theme_manager.current_theme == 'dark' else '#fee2e2'
            
            time_label_style = f"""
                color: {time_color};
                background-color: {time_bg};
                border: 3px solid {time_border};
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
            """
            self.time_label.setStyleSheet(time_label_style)
        
        # Progress bar
        if hasattr(self, 'progress_bar'):
            progress_chunk_color = theme_dict['accent'] if self.theme_manager.current_theme == 'dark' else '#e74c3c'
            progress_style = f"""
                QProgressBar {{
                    border: 2px solid {theme_dict['border']};
                    border-radius: 6px;
                    background-color: {theme_dict['background']};
                }}
                QProgressBar::chunk {{
                    background-color: {progress_chunk_color};
                    border-radius: 4px;
                }}
            """
            self.progress_bar.setStyleSheet(progress_style)
        
        # Start/Pause button
        if hasattr(self, 'start_pause_btn'):
            start_btn_style = self.theme_manager.get_button_style()
            self.start_pause_btn.setStyleSheet(start_btn_style)
        
        # Reset button
        if hasattr(self, 'reset_btn'):
            reset_btn_style = self.theme_manager.get_button_style()
            self.reset_btn.setStyleSheet(reset_btn_style)
        
        # Settings widget
        if hasattr(self, 'settings_widget'):
            settings_style = f"""
                QWidget {{
                    background-color: {theme_dict['secondary_background']};
                    border-radius: 15px;
                    border: 2px solid {theme_dict['border']};
                }}
            """
            self.settings_widget.setStyleSheet(settings_style)
        
        # Group boxes
        for group_box in self.findChildren(QGroupBox):
            group_style = f"""
                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {theme_dict['border']};
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                    color: {theme_dict['text']};
                    background-color: {theme_dict['secondary_background']};
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: {theme_dict['accent']};
                }}
            """
            group_box.setStyleSheet(group_style)
        
        # Spin boxes
        for spin_box in self.findChildren(QSpinBox):
            spin_style = f"""
                QSpinBox {{
                    border: 2px solid {theme_dict['border']};
                    border-radius: 4px;
                    padding: 5px;
                    background-color: {theme_dict['input_background']};
                    color: {theme_dict['text']};
                }}
                QSpinBox:focus {{
                    border-color: {theme_dict['accent']};
                }}
            """
            spin_box.setStyleSheet(spin_style)
        
        # Check boxes
        for check_box in self.findChildren(QCheckBox):
            check_style = f"""
                QCheckBox {{
                    color: {theme_dict['text']};
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                }}
                QCheckBox::indicator:unchecked {{
                    border: 2px solid {theme_dict['border']};
                    background-color: {theme_dict['input_background']};
                    border-radius: 3px;
                }}
                QCheckBox::indicator:checked {{
                    border: 2px solid {theme_dict['accent']};
                    background-color: {theme_dict['accent']};
                    border-radius: 3px;
                }}
            """
            check_box.setStyleSheet(check_style)
        
        # Combo boxes
        for combo_box in self.findChildren(QComboBox):
            combo_style = f"""
                QComboBox {{
                    border: 2px solid {theme_dict['border']};
                    border-radius: 4px;
                    padding: 5px;
                    background-color: {theme_dict['input_background']};
                    color: {theme_dict['text']};
                }}
                QComboBox:focus {{
                    border-color: {theme_dict['accent']};
                }}
                QComboBox::drop-down {{
                    border: none;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid {theme_dict['text']};
                }}
            """
            combo_box.setStyleSheet(combo_style)
        
        # Przyciski
        for button in self.findChildren(QPushButton):
            if button not in [getattr(self, 'start_pause_btn', None), getattr(self, 'reset_btn', None)]:
                button.setStyleSheet(self.theme_manager.get_button_style())
        
        # Separator
        for separator in self.findChildren(QFrame):
            if separator.frameShape() == QFrame.Shape.VLine:
                sep_style = f"""
                    QFrame {{
                        color: {theme_dict['border']};
                        background-color: {theme_dict['border']};
                    }}
                """
                separator.setStyleSheet(sep_style)
        
        # Wszystkie QLabel (oprócz głównych elementów timera)
        for label in self.findChildren(QLabel):
            if label not in [getattr(self, 'time_label', None), getattr(self, 'session_label', None), getattr(self, 'session_counter_label', None), getattr(self, 'status_label', None)]:
                # Dla opisów pól użyj koloru czerwonego w trybie ciemnym
                if self.theme_manager.current_theme == 'dark':
                    label_color = theme_dict.get('accent', '#ff6b6b')  # Czerwony w trybie ciemnym
                else:
                    label_color = theme_dict['text']  # Czarny w trybie jasnym
                
                label_style = f"""
                    QLabel {{
                        color: {label_color};
                        background-color: transparent;
                    }}
                """
                label.setStyleSheet(label_style)
        
    def init_timer_state(self):
        """Inicjalizuje stan timera"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # Stan timera
        self.is_running = False
        self.current_time = 0  # w sekundach
        self.session_type = "work"  # "work", "short_break", "long_break"
        self.session_count = 0
        
        # Domyślne ustawienia (w minutach)
        self.work_time = 25
        self.short_break_time = 5
        self.long_break_time = 15
        self.sessions_to_long_break = 4
        
        # Opcje
        self.auto_start_breaks = False
        self.auto_start_pomodoros = False
        
        # Ustawienia dźwięków
        self.work_sound = "Systemowy Błąd"
        self.break_sound = "Systemowy Asterisk"
        self.enable_work_sound = True
        self.enable_break_sound = True
        self.custom_work_sound_path = ""
        self.custom_break_sound_path = ""
        
    def setup_ui(self):
        """Tworzy interfejs użytkownika"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # === LEWA SEKCJA - TIMER ===
        self.create_timer_section(layout)
        
        # === SEPARATOR ===
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # === PRAWA SEKCJA - USTAWIENIA ===
        self.create_settings_section(layout)
        
        # Zastosuj motyw po utworzeniu UI
        self.apply_theme()
        
    def create_timer_section(self, parent_layout):
        """Tworzy sekcję timera"""
        self.timer_widget = QWidget()
        self.timer_widget.setFixedWidth(400)
        
        layout = QVBoxLayout(self.timer_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Tytuł sesji
        self.session_label = QLabel("Sesja pracy")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.addWidget(self.session_label)
        
        # Licznik sesji
        self.session_counter_label = QLabel("Sesja 1/4")
        self.session_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_counter_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.session_counter_label)
        
        # Główny timer
        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        layout.addWidget(self.time_label)
        
        # Pasek postępu
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        layout.addWidget(self.progress_bar)
        
        # Przyciski kontroli
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        self.start_pause_btn = QPushButton("▶ Start")
        self.start_pause_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.start_pause_btn.setFixedHeight(50)
        self.start_pause_btn.clicked.connect(self.toggle_timer)
        controls_layout.addWidget(self.start_pause_btn)
        
        self.reset_btn = QPushButton("⟲ Reset")
        self.reset_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.reset_btn.setFixedHeight(50)
        self.reset_btn.clicked.connect(self.reset_timer)
        controls_layout.addWidget(self.reset_btn)
        
        self.skip_btn = QPushButton("⏭ Pomiń")
        self.skip_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.skip_btn.setFixedHeight(50)
        self.skip_btn.clicked.connect(self.skip_session)
        controls_layout.addWidget(self.skip_btn)
        
        layout.addLayout(controls_layout)
        
        # Status
        self.status_label = QLabel("Gotowy do rozpoczęcia sesji pracy")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.status_label)
        
        parent_layout.addWidget(self.timer_widget)
        
    def create_settings_section(self, parent_layout):
        """Tworzy sekcję ustawień"""
        self.settings_widget = QWidget()
        
        layout = QVBoxLayout(self.settings_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Grupa czasów
        time_group = QGroupBox("Czasy sesji")
        time_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        time_layout = QGridLayout(time_group)
        time_layout.setSpacing(10)
        
        # Czas pracy
        work_label = QLabel("Czas pracy:")
        time_layout.addWidget(work_label, 0, 0)
        self.work_time_spin = QSpinBox()
        self.work_time_spin.setRange(1, 120)
        self.work_time_spin.setValue(25)
        self.work_time_spin.setSuffix(" min")
        self.work_time_spin.valueChanged.connect(self.on_settings_changed)
        time_layout.addWidget(self.work_time_spin, 0, 1)
        
        # Krótka przerwa
        short_break_label = QLabel("Krótka przerwa:")
        time_layout.addWidget(short_break_label, 1, 0)
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 30)
        self.short_break_spin.setValue(5)
        self.short_break_spin.setSuffix(" min")
        self.short_break_spin.valueChanged.connect(self.on_settings_changed)
        time_layout.addWidget(self.short_break_spin, 1, 1)
        
        # Długa przerwa
        long_break_label = QLabel("Długa przerwa:")
        time_layout.addWidget(long_break_label, 2, 0)
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(5, 60)
        self.long_break_spin.setValue(15)
        self.long_break_spin.setSuffix(" min")
        self.long_break_spin.valueChanged.connect(self.on_settings_changed)
        time_layout.addWidget(self.long_break_spin, 2, 1)
        
        # Liczba sesji do długiej przerwy
        sessions_label = QLabel("Sesje do długiej przerwy:")
        time_layout.addWidget(sessions_label, 3, 0)
        self.sessions_to_long_break_spin = QSpinBox()
        self.sessions_to_long_break_spin.setRange(2, 10)
        self.sessions_to_long_break_spin.setValue(4)
        self.sessions_to_long_break_spin.valueChanged.connect(self.on_settings_changed)
        time_layout.addWidget(self.sessions_to_long_break_spin, 3, 1)
        
        layout.addWidget(time_group)
        
        # Grupa opcji
        options_group = QGroupBox("Opcje automatyczne")
        options_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(10)
        
        self.auto_start_breaks_check = QCheckBox("Automatycznie rozpoczynaj przerwy")
        # Usuń hardcoded style - będzie ustawiony przez theme manager
        self.auto_start_breaks_check.stateChanged.connect(self.on_settings_changed)
        options_layout.addWidget(self.auto_start_breaks_check)
        
        self.auto_start_pomodoros_check = QCheckBox("Automatycznie rozpoczynaj następne Pomodoro")
        # Usuń hardcoded style - będzie ustawiony przez theme manager
        self.auto_start_pomodoros_check.stateChanged.connect(self.on_settings_changed)
        options_layout.addWidget(self.auto_start_pomodoros_check)
        
        layout.addWidget(options_group)
        
        # Grupa dźwięków
        sounds_group = QGroupBox("Powiadomienia dźwiękowe")
        sounds_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        # Usuń hardcoded style - będzie ustawiony przez theme manager
        sounds_layout = QVBoxLayout(sounds_group)
        sounds_layout.setSpacing(10)
        
        # Wybór dźwięku zakończenia sesji pracy
        work_sound_layout = QHBoxLayout()
        work_sound_label = QLabel("Dźwięk końca pracy:")
        # Usuń hardcoded style - będzie ustawiony przez theme manager
        work_sound_layout.addWidget(work_sound_label)
        
        self.work_sound_combo = QComboBox()
        self.work_sound_combo.addItems([
            "Systemowy Błąd",
            "Systemowy Asterisk", 
            "Systemowy Wykrzyknik",
            "Systemowy Pytanie",
            "Systemowy OK",
            "Niestandardowy dźwięk...",
            "Brak dźwięku"
        ])
        self.work_sound_combo.setStyleSheet("") # Usuń hardcoded style - będzie ustawiony przez theme manager
        self.work_sound_combo.currentTextChanged.connect(self.on_work_sound_changed)
        work_sound_layout.addWidget(self.work_sound_combo)
        sounds_layout.addLayout(work_sound_layout)
        
        # Wybór dźwięku zakończenia przerwy
        break_sound_layout = QHBoxLayout()
        break_sound_label = QLabel("Dźwięk końca przerwy:")
        # Usuń hardcoded style - będzie ustawiony przez theme manager
        break_sound_layout.addWidget(break_sound_label)
        
        self.break_sound_combo = QComboBox()
        self.break_sound_combo.addItems([
            "Systemowy Błąd",
            "Systemowy Asterisk", 
            "Systemowy Wykrzyknik",
            "Systemowy Pytanie",
            "Systemowy OK",
            "Niestandardowy dźwięk...",
            "Brak dźwięku"
        ])
        self.break_sound_combo.setCurrentText("Systemowy Asterisk")
        self.break_sound_combo.setStyleSheet("") # Usuń hardcoded style - będzie ustawiony przez theme manager
        self.break_sound_combo.currentTextChanged.connect(self.on_break_sound_changed)
        break_sound_layout.addWidget(self.break_sound_combo)
        sounds_layout.addLayout(break_sound_layout)
        
        # Checkboxy dla dźwięków
        self.enable_work_sound_check = QCheckBox("Odtwarzaj dźwięk po zakończeniu sesji pracy")
        self.enable_work_sound_check.setChecked(True)
        # Usuń hardcoded style - będzie ustawiony przez theme manager
        sounds_layout.addWidget(self.enable_work_sound_check)
        
        self.enable_break_sound_check = QCheckBox("Odtwarzaj dźwięk po zakończeniu przerwy")
        self.enable_break_sound_check.setChecked(True)
        # Usuń hardcoded style - będzie ustawiony przez theme manager
        sounds_layout.addWidget(self.enable_break_sound_check)
        
        # Przyciski testowania dźwięków
        test_buttons_layout = QHBoxLayout()
        
        test_work_btn = QPushButton("🔊 Test dźwięku pracy")
        # Usuń hardcoded style - będzie ustawiony przez theme manager
        test_work_btn.clicked.connect(lambda: self.play_sound(self.work_sound_combo.currentText()))
        test_buttons_layout.addWidget(test_work_btn)
        
        test_break_btn = QPushButton("🔊 Test dźwięku przerwy")
        # Usuń hardcoded style - będzie ustawiony przez theme manager
        test_break_btn.clicked.connect(lambda: self.play_sound(self.break_sound_combo.currentText()))
        test_buttons_layout.addWidget(test_break_btn)
        
        sounds_layout.addLayout(test_buttons_layout)
        
        layout.addWidget(sounds_group)
        
        # Statystyki
        stats_group = QGroupBox("Statystyki dzisiejszej sesji")
        stats_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
        """)
        stats_layout = QVBoxLayout(stats_group)
        
        self.completed_sessions_label = QLabel("Ukończone sesje: 0")
        self.completed_sessions_label.setFont(QFont("Segoe UI", 11))
        self.completed_sessions_label.setStyleSheet(self.theme_manager.get_label_style())
        stats_layout.addWidget(self.completed_sessions_label)
        
        self.total_focus_time_label = QLabel("Całkowity czas skupienia: 0 min")
        self.total_focus_time_label.setFont(QFont("Segoe UI", 11))
        self.total_focus_time_label.setStyleSheet(self.theme_manager.get_label_style())
        stats_layout.addWidget(self.total_focus_time_label)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        parent_layout.addWidget(self.settings_widget)
        
    def load_settings(self):
        """Ładuje ustawienia"""
        # TODO: Implementuj ładowanie z pliku konfiguracyjnego
        self.reset_timer()
        
    def on_settings_changed(self):
        """Obsługuje zmianę ustawień"""
        self.work_time = self.work_time_spin.value()
        self.short_break_time = self.short_break_spin.value()
        self.long_break_time = self.long_break_spin.value()
        self.sessions_to_long_break = self.sessions_to_long_break_spin.value()
        
        self.auto_start_breaks = self.auto_start_breaks_check.isChecked()
        self.auto_start_pomodoros = self.auto_start_pomodoros_check.isChecked()
        
        # Jeśli timer nie jest aktywny, zaktualizuj wyświetlany czas
        if not self.is_running:
            self.reset_timer()
            
    def toggle_timer(self):
        """Rozpoczyna/pauzuje timer"""
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()
            
    def start_timer(self):
        """Rozpoczyna timer"""
        self.is_running = True
        self.timer.start(1000)  # Aktualizuj co sekundę
        self.start_pause_btn.setText("⏸ Pauza")
        self.start_pause_btn.setStyleSheet(self.theme_manager.get_pause_button_style())
        
        if self.session_type == "work":
            self.status_label.setText("Fokus! Czas na produktywną pracę 🎯")
        else:
            self.status_label.setText("Czas na odpoczynek 😌")
            
    def pause_timer(self):
        """Pauzuje timer"""
        self.is_running = False
        self.timer.stop()
        self.start_pause_btn.setText("▶ Start")
        # Usuń hardcoded style - pozostaw domyślny styl z theme managera
        self.status_label.setText("Timer zatrzymany")
        
    def reset_timer(self):
        """Resetuje timer do początku bieżącej sesji"""
        self.pause_timer()
        
        if self.session_type == "work":
            self.current_time = self.work_time * 60
        elif self.session_type == "short_break":
            self.current_time = self.short_break_time * 60
        else:  # long_break
            self.current_time = self.long_break_time * 60
            
        self.update_display()
        self.progress_bar.setValue(0)
        self.status_label.setText("Gotowy do rozpoczęcia")
        
    def skip_session(self):
        """Pomija bieżącą sesję"""
        self.pause_timer()
        self.session_completed()
        
    def update_timer(self):
        """Aktualizuje timer co sekundę"""
        if self.current_time > 0:
            self.current_time -= 1
            self.update_display()
            self.update_progress()
        else:
            # Sesja zakończona
            self.session_completed()
            
    def update_display(self):
        """Aktualizuje wyświetlacz czasu"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        
    def update_progress(self):
        """Aktualizuje pasek postępu"""
        if self.session_type == "work":
            total_time = self.work_time * 60
        elif self.session_type == "short_break":
            total_time = self.short_break_time * 60
        else:  # long_break
            total_time = self.long_break_time * 60
            
        progress = int(((total_time - self.current_time) / total_time) * 100)
        self.progress_bar.setValue(progress)
        
    def session_completed(self):
        """Obsługuje zakończenie sesji"""
        self.pause_timer()
        
        if self.session_type == "work":
            self.session_count += 1
            
            # Sprawdź czy czas na długą przerwę
            if self.session_count % self.sessions_to_long_break == 0:
                self.session_type = "long_break"
                self.session_label.setText("Długa przerwa")
                self.status_label.setText("Świetna robota! Czas na dłuższą przerwę 🎉")
            else:
                self.session_type = "short_break"
                self.session_label.setText("Krótka przerwa")
                self.status_label.setText("Dobra robota! Czas na krótką przerwę ☕")
                
            # Aktualizuj kolory dla przerwy
            self.time_label.setStyleSheet(self.theme_manager.get_timer_break_style())
            self.progress_bar.setStyleSheet(self.theme_manager.get_progress_break_style())
            
        else:
            # Przerwa zakończona, wróć do pracy
            self.session_type = "work"
            self.session_label.setText("Sesja pracy")
            self.status_label.setText("Przerwa zakończona. Czas na pracę!")
            
            # Aktualizuj kolory dla pracy
            self.time_label.setStyleSheet(self.theme_manager.get_timer_work_style())
            self.progress_bar.setStyleSheet(self.theme_manager.get_progress_work_style())
            
        # Aktualizuj licznik sesji
        current_in_cycle = (self.session_count % self.sessions_to_long_break) or self.sessions_to_long_break
        self.session_counter_label.setText(f"Sesja {current_in_cycle}/{self.sessions_to_long_break}")
        
        # Aktualizuj statystyki
        self.completed_sessions_label.setText(f"Ukończone sesje: {self.session_count}")
        total_minutes = self.session_count * self.work_time
        self.total_focus_time_label.setText(f"Całkowity czas skupienia: {total_minutes} min")
        
        self.reset_timer()
        
        # Auto-start jeśli włączone
        if ((self.session_type != "work" and self.auto_start_breaks) or 
            (self.session_type == "work" and self.auto_start_pomodoros)):
            self.start_timer()
            
        # TODO: Dodaj notyfikację systemową
        QApplication.beep()  # Sygnał dźwiękowy
        
        # Odtwórz odpowiedni dźwięk
        if self.session_type == "work":
            # Zakończyła się sesja pracy
            if self.enable_work_sound_check.isChecked():
                self.play_sound(self.work_sound_combo.currentText())
        else:
            # Zakończyła się przerwa
            if self.enable_break_sound_check.isChecked():
                self.play_sound(self.break_sound_combo.currentText())
    
    def play_sound(self, sound_name):
        """Odtwarza wybrany dźwięk systemowy lub niestandardowy"""
        try:
            import winsound
            
            # Sprawdź czy to niestandardowy dźwięk
            if sound_name == "Niestandardowy dźwięk..." or sound_name.startswith("Niestandardowy:"):
                # Określ który plik użyć
                custom_path = ""
                if sound_name == self.work_sound_combo.currentText():
                    custom_path = self.custom_work_sound_path
                elif sound_name == self.break_sound_combo.currentText():
                    custom_path = self.custom_break_sound_path
                
                if custom_path and os.path.exists(custom_path):
                    try:
                        # Odtwórz niestandardowy plik
                        winsound.PlaySound(custom_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                        return
                    except Exception as e:
                        QMessageBox.warning(self, "Błąd", f"Nie można odtworzyć pliku dźwiękowego:\n{e}")
                        return
            
            # Obsługa dźwięków systemowych
            sound_mapping = {
                "Systemowy Błąd": winsound.MB_ICONHAND,
                "Systemowy Asterisk": winsound.MB_ICONASTERISK,
                "Systemowy Wykrzyknik": winsound.MB_ICONEXCLAMATION,
                "Systemowy Pytanie": winsound.MB_ICONQUESTION,
                "Systemowy OK": winsound.MB_OK,
                "Brak dźwięku": None
            }
            
            if sound_name in sound_mapping and sound_mapping[sound_name] is not None:
                winsound.MessageBeep(sound_mapping[sound_name])
                
        except ImportError:
            # Fallback na zwykły beep
            QApplication.beep()
    
    def on_work_sound_changed(self, sound_name):
        """Obsługuje zmianę dźwięku dla końca pracy"""
        if sound_name == "Niestandardowy dźwięk...":
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Wybierz plik dźwiękowy dla końca pracy",
                "",
                "Pliki dźwiękowe (*.wav *.mp3 *.ogg);;Wszystkie pliki (*)"
            )
            if file_path:
                self.custom_work_sound_path = file_path
                self.work_sound = "Niestandardowy dźwięk..."
                # Dodaj nazwę pliku do wyświetlania
                file_name = os.path.basename(file_path)
                current_index = self.work_sound_combo.findText("Niestandardowy dźwięk...")
                if current_index >= 0:
                    self.work_sound_combo.setItemText(current_index, f"Niestandardowy: {file_name}")
            else:
                # Użytkownik anulował, wróć do poprzedniego
                self.work_sound_combo.setCurrentText(self.work_sound)
        else:
            self.work_sound = sound_name
    
    def on_break_sound_changed(self, sound_name):
        """Obsługuje zmianę dźwięku dla końca przerwy"""
        if sound_name == "Niestandardowy dźwięk...":
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Wybierz plik dźwiękowy dla końca przerwy",
                "",
                "Pliki dźwiękowe (*.wav *.mp3 *.ogg);;Wszystkie pliki (*)"
            )
            if file_path:
                self.custom_break_sound_path = file_path
                self.break_sound = "Niestandardowy dźwięk..."
                # Dodaj nazwę pliku do wyświetlania
                file_name = os.path.basename(file_path)
                current_index = self.break_sound_combo.findText("Niestandardowy dźwięk...")
                if current_index >= 0:
                    self.break_sound_combo.setItemText(current_index, f"Niestandardowy: {file_name}")
            else:
                # Użytkownik anulował, wróć do poprzedniego
                self.break_sound_combo.setCurrentText(self.break_sound)
        else:
            self.break_sound = sound_name