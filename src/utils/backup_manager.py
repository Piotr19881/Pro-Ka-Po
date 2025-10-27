"""
System zarządzania backupami bazy danych
"""
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


class BackupManager:
    """Zarządza eksportem i importem backupów bazy danych"""
    
    def __init__(self, db_path):
        """
        Inicjalizuje BackupManager
        
        Args:
            db_path: Ścieżka do pliku bazy danych
        """
        self.db_path = db_path
        
    def export_backup(self, backup_path):
        """
        Eksportuje backup bazy danych do wskazanego pliku
        
        Args:
            backup_path: Ścieżka docelowa dla pliku backupu
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Sprawdź czy baza danych istnieje
            if not os.path.exists(self.db_path):
                return False, "Baza danych nie istnieje"
            
            # Utwórz katalog docelowy jeśli nie istnieje
            backup_dir = os.path.dirname(backup_path)
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Skopiuj bazę danych do pliku backupu
            shutil.copy2(self.db_path, backup_path)
            
            # Sprawdź czy backup został utworzony
            if os.path.exists(backup_path):
                backup_size = os.path.getsize(backup_path)
                return True, f"Backup utworzony pomyślnie ({backup_size} bajtów)"
            else:
                return False, "Nie udało się utworzyć pliku backupu"
                
        except PermissionError:
            return False, "Brak uprawnień do zapisu w wybranej lokalizacji"
        except Exception as e:
            return False, f"Błąd podczas tworzenia backupu: {str(e)}"
    
    def import_backup(self, backup_path):
        """
        Importuje backup bazy danych ze wskazanego pliku
        
        Args:
            backup_path: Ścieżka do pliku backupu
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Sprawdź czy plik backupu istnieje
            if not os.path.exists(backup_path):
                return False, "Plik backupu nie istnieje"
            
            # Sprawdź czy to prawidłowy plik SQLite
            if not self._is_valid_sqlite_file(backup_path):
                return False, "Wybrany plik nie jest prawidłową bazą danych SQLite"
            
            # Utwórz backup aktualnej bazy przed nadpisaniem
            if os.path.exists(self.db_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                auto_backup_path = f"{self.db_path}.backup_{timestamp}"
                try:
                    shutil.copy2(self.db_path, auto_backup_path)
                    print(f"Utworzono automatyczny backup aktualnej bazy: {auto_backup_path}")
                except Exception as e:
                    print(f"Ostrzeżenie: Nie udało się utworzyć automatycznego backupu: {e}")
            
            # Zamknij wszystkie połączenia z bazą danych
            # (to powinno być zrobione przed wywołaniem tej metody)
            
            # Nadpisz bazę danych plikiem backupu
            shutil.copy2(backup_path, self.db_path)
            
            # Sprawdź czy import się powiódł
            if os.path.exists(self.db_path):
                return True, "Backup zaimportowany pomyślnie. Aplikacja wymaga ponownego uruchomienia."
            else:
                return False, "Nie udało się zaimportować backupu"
                
        except PermissionError:
            return False, "Brak uprawnień do zapisu w lokalizacji bazy danych"
        except Exception as e:
            return False, f"Błąd podczas importu backupu: {str(e)}"
    
    def _is_valid_sqlite_file(self, file_path):
        """
        Sprawdza czy plik jest prawidłową bazą danych SQLite
        
        Args:
            file_path: Ścieżka do pliku
            
        Returns:
            bool: True jeśli plik jest prawidłową bazą SQLite
        """
        try:
            # Sprawdź nagłówek pliku
            with open(file_path, 'rb') as f:
                header = f.read(16)
                if header[:16] != b'SQLite format 3\x00':
                    return False
            
            # Spróbuj otworzyć jako bazę danych
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            # Sprawdź czy są jakieś tabele
            return len(tables) > 0
            
        except Exception as e:
            print(f"Błąd walidacji pliku SQLite: {e}")
            return False
    
    def create_auto_backup(self, backup_dir=None):
        """
        Tworzy automatyczny backup z timestampem
        
        Args:
            backup_dir: Katalog dla backupów (domyślnie obok bazy danych)
            
        Returns:
            tuple: (success: bool, message: str, backup_path: str)
        """
        try:
            # Jeśli nie podano katalogu, użyj katalogu bazy danych
            if backup_dir is None:
                backup_dir = os.path.dirname(self.db_path)
            
            # Utwórz nazwę pliku z timestampem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_name = os.path.basename(self.db_path)
            backup_filename = f"{os.path.splitext(db_name)[0]}_backup_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Eksportuj backup
            success, message = self.export_backup(backup_path)
            
            return success, message, backup_path if success else None
            
        except Exception as e:
            return False, f"Błąd podczas tworzenia automatycznego backupu: {str(e)}", None
    
    def get_backup_info(self, backup_path):
        """
        Pobiera informacje o backupie
        
        Args:
            backup_path: Ścieżka do pliku backupu
            
        Returns:
            dict: Informacje o backupie (rozmiar, data utworzenia, liczba tabel)
        """
        try:
            if not os.path.exists(backup_path):
                return None
            
            info = {
                'path': backup_path,
                'size': os.path.getsize(backup_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(backup_path)),
                'tables': []
            }
            
            # Pobierz listę tabel
            if self._is_valid_sqlite_file(backup_path):
                conn = sqlite3.connect(backup_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                info['tables'] = [row[0] for row in cursor.fetchall()]
                conn.close()
            
            return info
            
        except Exception as e:
            print(f"Błąd pobierania informacji o backupie: {e}")
            return None
