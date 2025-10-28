"""
TranslationManager - Zarządzanie tłumaczeniami w aplikacji
Obsługuje ładowanie plików .qm, zmianę języka i konfigurację
"""

import os
import json
from typing import Optional, List, Dict
from PyQt6.QtCore import QTranslator, QLocale, QCoreApplication, QSettings


class TranslationManager:
    """Menedżer tłumaczeń aplikacji"""
    
    def __init__(self, app: QCoreApplication):
        """
        Inicjalizacja menedżera tłumaczeń
        
        Args:
            app: Instancja QApplication
        """
        self.app = app
        self.translator = QTranslator(app)
        self.current_language = None
        self.available_languages: List[Dict] = []
        self.settings = QSettings("ProKaPo", "ProKaPo")
        
        # Ścieżki
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.translations_dir = os.path.join(self.base_dir, "translations")
        self.languages_file = os.path.join(self.base_dir, "languages.json")
        
        # Załaduj konfigurację języków
        self._load_languages_config()
        
        # Załaduj zapisany język lub użyj domyślnego
        saved_language = self.settings.value("language", None)
        if saved_language and self._is_language_available(saved_language):
            self.load_language(saved_language)
        else:
            self._load_default_language()
    
    def _load_languages_config(self):
        """Ładuje konfigurację dostępnych języków z pliku JSON"""
        try:
            if os.path.exists(self.languages_file):
                with open(self.languages_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.available_languages = config.get('languages', [])
                    self.fallback_language = config.get('fallback_language', 'pl')
            else:
                # Domyślna konfiguracja jeśli plik nie istnieje
                self.available_languages = [
                    {
                        "code": "pl",
                        "name": "Polski",
                        "native_name": "Polski",
                        "flag": "🇵🇱",
                        "default": True
                    }
                ]
                self.fallback_language = 'pl'
        except Exception as e:
            print(f"Błąd podczas ładowania konfiguracji języków: {e}")
            self.available_languages = []
            self.fallback_language = 'pl'
    
    def _is_language_available(self, language_code: str) -> bool:
        """
        Sprawdza czy język jest dostępny
        
        Args:
            language_code: Kod języka (np. 'pl', 'en')
            
        Returns:
            True jeśli język jest dostępny
        """
        return any(lang['code'] == language_code for lang in self.available_languages)
    
    def _load_default_language(self):
        """Ładuje domyślny język"""
        # Znajdź język oznaczony jako domyślny
        default_lang = next(
            (lang for lang in self.available_languages if lang.get('default', False)),
            None
        )
        
        if default_lang:
            self.load_language(default_lang['code'])
        elif self.available_languages:
            # Jeśli nie ma domyślnego, użyj pierwszego dostępnego
            self.load_language(self.available_languages[0]['code'])
    
    def load_language(self, language_code: str) -> bool:
        """
        Ładuje i aktywuje wybrany język
        
        Args:
            language_code: Kod języka (np. 'pl', 'en', 'de')
            
        Returns:
            True jeśli język został załadowany pomyślnie
        """
        if not self._is_language_available(language_code):
            print(f"Język '{language_code}' nie jest dostępny")
            return False
        
        # Usuń poprzedni translator
        if self.translator:
            self.app.removeTranslator(self.translator)
        
        # Dla języka polskiego (domyślnego) nie ładujemy tłumaczeń
        if language_code == 'pl':
            self.current_language = language_code
            self.settings.setValue("language", language_code)
            return True
        
        # Ścieżka do pliku tłumaczenia
        qm_file = os.path.join(self.translations_dir, f"pro_ka_po_{language_code}.qm")
        
        # Załaduj plik tłumaczenia
        if os.path.exists(qm_file):
            if self.translator.load(qm_file):
                self.app.installTranslator(self.translator)
                self.current_language = language_code
                self.settings.setValue("language", language_code)
                print(f"Załadowano tłumaczenie: {language_code}")
                return True
            else:
                print(f"Nie udało się załadować tłumaczenia z pliku: {qm_file}")
                return False
        else:
            print(f"Plik tłumaczenia nie istnieje: {qm_file}")
            # Dla języków bez pliku .qm, zaznacz że język jest aktywny
            # (przydatne podczas rozwoju)
            self.current_language = language_code
            self.settings.setValue("language", language_code)
            return True
    
    def get_current_language(self) -> Optional[str]:
        """
        Zwraca kod aktualnie wybranego języka
        
        Returns:
            Kod języka lub None
        """
        return self.current_language
    
    def get_available_languages(self) -> List[Dict]:
        """
        Zwraca listę dostępnych języków
        
        Returns:
            Lista słowników z informacjami o językach
        """
        return self.available_languages
    
    def get_language_info(self, language_code: str) -> Optional[Dict]:
        """
        Zwraca informacje o języku
        
        Args:
            language_code: Kod języka
            
        Returns:
            Słownik z informacjami o języku lub None
        """
        return next(
            (lang for lang in self.available_languages if lang['code'] == language_code),
            None
        )
    
    def change_language(self, language_code: str) -> bool:
        """
        Zmienia język aplikacji
        
        Args:
            language_code: Kod języka
            
        Returns:
            True jeśli zmiana powiodła się
        """
        if language_code == self.current_language:
            return True
        
        return self.load_language(language_code)
    
    def retranslate_ui(self, widget):
        """
        Wymusza ponowne przetłumaczenie interfejsu
        Wywołuje metodę retranslateUi() jeśli istnieje
        
        Args:
            widget: Widget do przetłumaczenia
        """
        if hasattr(widget, 'retranslateUi'):
            widget.retranslateUi()
