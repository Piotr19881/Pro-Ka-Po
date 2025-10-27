import sqlite3
import os
from datetime import datetime
import time

class Database:
    def __init__(self, db_path='data/tasks.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Tworzy połączenie z bazą z timeout"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        # Tymczasowo wyłączamy WAL mode ze względu na problemy z wydajnością
        # conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging dla lepszej współbieżności
        return conn
    
    def init_database(self):
        """Inicjalizuje bazę danych i tworzy tabele jeśli nie istnieją"""
        # Upewnij się, że folder data istnieje
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela zadań
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'todo',
                    priority TEXT DEFAULT 'medium',
                    category TEXT,
                    due_date TEXT,
                    note_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE SET NULL
                )
            ''')
            
            # Tabela kategorii
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#3498db',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela tagów zadań
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#3498db',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela definicji tabel użytkownika
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela kolumn dla tabel użytkownika
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_table_columns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_id INTEGER,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    is_required BOOLEAN DEFAULT 0,
                    is_visible BOOLEAN DEFAULT 1,
                    column_order INTEGER DEFAULT 0,
                    dictionary_list TEXT,
                    settings TEXT,
                    FOREIGN KEY (table_id) REFERENCES user_tables (id) ON DELETE CASCADE
                )
            ''')
            
            # Sprawdź czy kolumna note_id istnieje w tabeli tasks, jeśli nie - dodaj ją
            cursor.execute("PRAGMA table_info(tasks)")
            task_columns = [row[1] for row in cursor.fetchall()]
            
            if 'note_id' not in task_columns:
                cursor.execute('''
                    ALTER TABLE tasks 
                    ADD COLUMN note_id INTEGER
                ''')
            
            # Sprawdź czy kolumna kanban istnieje w tabeli tasks, jeśli nie - dodaj ją
            if 'kanban' not in task_columns:
                cursor.execute('''
                    ALTER TABLE tasks 
                    ADD COLUMN kanban INTEGER DEFAULT 0
                ''')
            
            # Sprawdź czy kolumna archived istnieje w tabeli tasks, jeśli nie - dodaj ją
            if 'archived' not in task_columns:
                cursor.execute('''
                    ALTER TABLE tasks 
                    ADD COLUMN archived INTEGER DEFAULT 0
                ''')

            # Sprawdź czy kolumna dictionary_list istnieje, jeśli nie - dodaj ją
            cursor.execute("PRAGMA table_info(user_table_columns)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'dictionary_list' not in columns:
                cursor.execute('''
                    ALTER TABLE user_table_columns 
                    ADD COLUMN dictionary_list TEXT
                ''')
            
            # Sprawdź czy istnieje kolumna context w dictionary_lists
            cursor.execute('PRAGMA table_info(dictionary_lists)')
            dict_columns = [row[1] for row in cursor.fetchall()]
            
            if 'context' not in dict_columns:
                cursor.execute('''
                    ALTER TABLE dictionary_lists 
                    ADD COLUMN context TEXT DEFAULT 'table'
                ''')
            
            # Tabela list słownikowych
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dictionary_lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    type TEXT DEFAULT 'Inne',
                    allow_custom BOOLEAN DEFAULT 0,
                    multiple_selection BOOLEAN DEFAULT 0,
                    required BOOLEAN DEFAULT 0,
                    default_item TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela elementów list słownikowych
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dictionary_list_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_id INTEGER,
                    value TEXT NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    FOREIGN KEY (list_id) REFERENCES dictionary_lists (id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela szerokości kolumn dla tabel użytkownika
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS table_column_widths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_id INTEGER,
                    column_index INTEGER,
                    width INTEGER,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (table_id) REFERENCES user_tables (id) ON DELETE CASCADE,
                    UNIQUE(table_id, column_index)
                )
            ''')
            
            # Tabela kolumn zadań
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_columns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,
                    visible BOOLEAN DEFAULT 1,
                    in_panel BOOLEAN DEFAULT 0,
                    default_value TEXT,
                    column_order INTEGER DEFAULT 0,
                    dictionary_list_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dictionary_list_id) REFERENCES dictionary_lists (id) ON DELETE SET NULL
                )
            ''')
            
            # Tabela notatek
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    parent_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES notes(id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela ustawień aplikacji
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Dodaj domyślne kategorie
            default_categories = [
                ('Praca', '#e74c3c'),
                ('Dom', '#2ecc71'),
                ('Nauka', '#f39c12'),
                ('Hobby', '#9b59b6')
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)
            ''', default_categories)
            
            conn.commit()
    
    def add_task(self, title, description='', status='todo', priority='medium', category=None, due_date=None, kanban=0):
        """Dodaje nowe zadanie do bazy danych"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (title, description, status, priority, category, due_date, kanban)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, status, priority, category, due_date, kanban))
            conn.commit()
            return cursor.lastrowid
    
    def get_tasks(self, status=None):
        """Pobiera zadania z bazy danych"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC', (status,))
            else:
                cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
            return cursor.fetchall()
    
    def get_task(self, task_id):
        """Pobiera pojedyncze zadanie z bazy danych"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            if row:
                # Konwertuj row na słownik dla łatwiejszego dostępu
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_categories(self):
        """Pobiera wszystkie kategorie"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM categories ORDER BY name')
            return cursor.fetchall()
    
    def get_task_tags(self):
        """Pobiera wszystkie tagi zadań"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM task_tags ORDER BY name')
            return cursor.fetchall()
    
    def add_task_tag(self, name, color='#3498db'):
        """Dodaje nowy tag zadania"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO task_tags (name, color) VALUES (?, ?)
            ''', (name, color))
            conn.commit()
            return cursor.lastrowid
    
    def update_task_tag(self, tag_id, name, color):
        """Aktualizuje tag zadania"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE task_tags SET name = ?, color = ? WHERE id = ?
            ''', (name, color, tag_id))
            conn.commit()
    
    def delete_task_tag(self, tag_id):
        """Usuwa tag zadania"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM task_tags WHERE id = ?', (tag_id,))
            conn.commit()
    
    def update_task(self, task_id, **kwargs):
        """Aktualizuje zadanie"""
        if not kwargs:
            return
        
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [task_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE tasks SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', values)
            conn.commit()
    
    def delete_task(self, task_id):
        """Usuwa zadanie"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
    
    # Metody obsługi tabel użytkownika
    def create_user_table(self, table_config):
        """Tworzy nową tabelę użytkownika"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Dodaj definicję tabeli
            cursor.execute('''
                INSERT INTO user_tables (name, description) VALUES (?, ?)
            ''', (table_config['name'], table_config.get('description', '')))
            
            table_id = cursor.lastrowid
            
            # Dodaj kolumny
            for i, column in enumerate(table_config['columns']):
                cursor.execute('''
                    INSERT INTO user_table_columns 
                    (table_id, name, type, is_required, is_visible, column_order, settings, color, dictionary_list_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    table_id,
                    column['name'],
                    column['type'],
                    column.get('required', False),
                    column.get('visible', True),
                    i,
                    str(column.get('settings', {})),
                    column.get('color', '#ffffff'),
                    column.get('dictionary_list_id')
                ))
            
            # Utwórz fizyczną tabelę dla danych
            self.create_physical_table(table_config['name'], table_config['columns'], conn)
            
            conn.commit()
            return table_id
    
    def update_user_table(self, table_id, table_config):
        """Aktualizuje istniejącą tabelę użytkownika"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Aktualizuj podstawowe informacje tabeli
            cursor.execute('''
                UPDATE user_tables 
                SET name = ?, description = ? 
                WHERE id = ?
            ''', (table_config['name'], table_config.get('description', ''), table_id))
            
            # Usuń stare kolumny
            cursor.execute('DELETE FROM user_table_columns WHERE table_id = ?', (table_id,))
            
            # Dodaj nowe kolumny
            for i, column in enumerate(table_config['columns']):
                dictionary_list_id = column.get('dictionary_list_id')
                cursor.execute('''
                    INSERT INTO user_table_columns 
                    (table_id, name, type, is_required, is_visible, column_order, settings, dictionary_list_id, color)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    table_id,
                    column['name'],
                    column['type'],
                    column.get('required', False),
                    column.get('visible', True),
                    i,
                    str(column.get('settings', {})),
                    dictionary_list_id,
                    column.get('color', '#ffffff')
                ))
            
            # TODO: Zaktualizuj fizyczną tabelę (to jest skomplikowane - wymaga migracji danych)
            # Na razie pozostaw starą strukturę fizycznej tabeli
            
            conn.commit()
            return table_id
    
    def create_physical_table(self, table_name, columns, conn=None):
        """Tworzy fizyczną tabelę w bazie danych"""
        if conn is None:
            with self.get_connection() as conn:
                self._create_physical_table_impl(table_name, columns, conn)
        else:
            self._create_physical_table_impl(table_name, columns, conn)
    
    def _create_physical_table_impl(self, table_name, columns, conn):
        """Implementacja tworzenia fizycznej tabeli"""
        cursor = conn.cursor()
        
        # Bezpieczna nazwa tabeli (dodajemy prefiks)
        safe_table_name = f"user_table_{table_name.lower().replace(' ', '_')}"
        
        # Buduj SQL dla kolumn
        column_definitions = ['id INTEGER PRIMARY KEY AUTOINCREMENT']
        used_names = set(['id', 'created_at', 'updated_at'])  # Zarezerwowane nazwy
        
        for i, col in enumerate(columns):
            # Bezpieczna nazwa kolumny
            base_name = col['name'].lower().replace(' ', '_').replace('-', '_')
            # Usuń niedozwolone znaki
            safe_name = ''.join(c for c in base_name if c.isalnum() or c == '_')
            
            # Upewnij się, że nazwa jest unikalna
            if safe_name in used_names or not safe_name:
                safe_name = f"column_{i+1}"
            
            # Jeśli nadal jest konflikt, dodaj numer
            counter = 1
            original_name = safe_name
            while safe_name in used_names:
                safe_name = f"{original_name}_{counter}"
                counter += 1
            
            used_names.add(safe_name)
            
            col_type = self.get_sql_type(col['type'])
            column_def = f"{safe_name} {col_type}"
            if col.get('required', False):
                column_def += " NOT NULL"
            
            column_definitions.append(column_def)
        
        # Dodaj timestamp'y
        column_definitions.extend([
            'created_at TEXT DEFAULT CURRENT_TIMESTAMP',
            'updated_at TEXT DEFAULT CURRENT_TIMESTAMP'
        ])
        
        create_sql = f'''
            CREATE TABLE IF NOT EXISTS {safe_table_name} (
                {', '.join(column_definitions)}
            )
        '''
        
        cursor.execute(create_sql)
        conn.commit()
    
    def get_sql_type(self, column_type):
        """Konwertuje typ kolumny na typ SQL"""
        type_mapping = {
            'Tekstowa': 'TEXT',
            'Data': 'DATE',
            'Godzina': 'TIME',
            'Czas': 'DATETIME',
            'Alarm': 'DATETIME',
            'Waluta': 'DECIMAL(10,2)',
            'Lista': 'TEXT',
            'Hiperłącze': 'TEXT',
            'Operacje matematyczne': 'DECIMAL(15,2)',
            'CheckBox': 'BOOLEAN'
        }
        return type_mapping.get(column_type, 'TEXT')
    
    def get_user_tables(self):
        """Pobiera listę tabel użytkownika"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, created_at 
                FROM user_tables 
                ORDER BY name
            ''')
            
            tables = []
            for row in cursor.fetchall():
                table_id, table_name, description, created_at = row
                
                # Pobierz kolumny dla tej tabeli
                cursor.execute('''
                    SELECT name, type, is_required, is_visible, column_order, settings, dictionary_list_id, color
                    FROM user_table_columns 
                    WHERE table_id = ? 
                    ORDER BY column_order
                ''', (table_id,))
                
                columns = []
                for col_row in cursor.fetchall():
                    col_name, col_type, is_required, is_visible, order, settings, dictionary_list_id, color = col_row
                    columns.append({
                        'name': col_name,
                        'type': col_type,
                        'required': bool(is_required),
                        'visible': bool(is_visible),
                        'order': order,
                        'settings': settings,
                        'dictionary_list_id': dictionary_list_id,
                        'color': color or '#ffffff'
                    })
                
                tables.append({
                    'id': table_id,
                    'name': table_name,  # Używamy table_name zamiast name
                    'description': description,
                    'created_at': created_at,
                    'columns': columns
                })
            
            return tables
    
    def delete_user_table(self, table_id):
        """Usuwa tabelę użytkownika"""
        print(f"DEBUG: delete_user_table wywoływana dla ID={table_id}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Pobierz nazwę tabeli
            cursor.execute('SELECT name FROM user_tables WHERE id = ?', (table_id,))
            result = cursor.fetchone()
            print(f"DEBUG: Znaleziono tabelę: {result}")
            
            if result:
                table_name = result[0]
                safe_table_name = f"user_table_{table_name.lower().replace(' ', '_')}"
                print(f"DEBUG: Usuwanie tabeli '{table_name}' (fizyczna: {safe_table_name})")
                
                # Usuń fizyczną tabelę
                cursor.execute(f'DROP TABLE IF EXISTS {safe_table_name}')
                print(f"DEBUG: Usunięto fizyczną tabelę {safe_table_name}")
                
                # Usuń definicję (CASCADE usunie też kolumny)
                cursor.execute('DELETE FROM user_tables WHERE id = ?', (table_id,))
                rows_affected = cursor.rowcount
                print(f"DEBUG: Usunięto definicję tabeli, wierszy usuniętych: {rows_affected}")
                
                conn.commit()
                print(f"DEBUG: Transakcja zakończona, tabela {table_name} usunięta")
            else:
                print(f"DEBUG: Nie znaleziono tabeli o ID={table_id}")
    
    # Metody obsługi list słownikowych
    def create_dictionary_list(self, list_config):
        """Tworzy nową listę słownikową"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO dictionary_lists 
                (name, description, type, allow_custom, multiple_selection, required, default_item, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                list_config['name'],
                list_config.get('description', ''),
                list_config.get('type', 'Inne'),
                list_config.get('allow_custom', False),
                list_config.get('multiple_selection', False),
                list_config.get('required', False),
                list_config.get('default_item'),
                list_config.get('context', 'table')
            ))
            
            list_id = cursor.lastrowid
            
            # Dodaj elementy listy
            for i, item in enumerate(list_config.get('items', [])):
                cursor.execute('''
                    INSERT INTO dictionary_list_items (list_id, value, order_index)
                    VALUES (?, ?, ?)
                ''', (list_id, item, i))
            
            conn.commit()
            return list_id
    
    def get_dictionary_lists(self, context="table"):
        """Pobiera listę słowników dla określonego kontekstu"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, type, allow_custom, multiple_selection, required, default_item, context
                FROM dictionary_lists 
                WHERE context = ?
                ORDER BY name
            ''', (context,))
            
            lists = []
            for row in cursor.fetchall():
                list_id, name, desc, type_, allow_custom, multi_sel, required, default, ctx = row
                
                # Pobierz elementy listy
                cursor.execute('''
                    SELECT value FROM dictionary_list_items 
                    WHERE list_id = ? ORDER BY order_index
                ''', (list_id,))
                
                items = [item[0] for item in cursor.fetchall()]
                
                lists.append({
                    'id': list_id,
                    'name': name,
                    'description': desc,
                    'type': type_,
                    'allow_custom': bool(allow_custom),
                    'multiple_selection': bool(multi_sel),
                    'required': bool(required),
                    'default_item': default,
                    'context': ctx,
                    'items': items
                })
            
            return lists
    
    def get_dictionary_list_by_id(self, list_id):
        """Pobiera konkretną listę słownikową po ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, type, allow_custom, multiple_selection, required, default_item, context
                FROM dictionary_lists 
                WHERE id = ?
            ''', (list_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            list_id, name, desc, type_, allow_custom, multi_sel, required, default, ctx = row
            
            # Pobierz elementy listy
            cursor.execute('''
                SELECT value FROM dictionary_list_items 
                WHERE list_id = ? ORDER BY order_index
            ''', (list_id,))
            
            items = [item[0] for item in cursor.fetchall()]
            
            return {
                'id': list_id,
                'name': name,
                'description': desc,
                'type': type_,
                'allow_custom': bool(allow_custom),
                'multiple_selection': bool(multi_sel),
                'required': bool(required),
                'default_item': default,
                'context': ctx,
                'items': items
            }
    
    def get_dictionary_list_by_name(self, name, context="table"):
        """Pobiera konkretną listę słownikową po nazwie i kontekście"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, type, allow_custom, multiple_selection, required, default_item, context
                FROM dictionary_lists 
                WHERE name = ? AND context = ?
            ''', (name, context))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            list_id, name, desc, type_, allow_custom, multi_sel, required, default, ctx = row
            
            # Pobierz elementy listy
            cursor.execute('''
                SELECT value FROM dictionary_list_items 
                WHERE list_id = ? ORDER BY order_index
            ''', (list_id,))
            
            items = [item[0] for item in cursor.fetchall()]
            
            return {
                'id': list_id,
                'name': name,
                'description': desc,
                'type': type_,
                'allow_custom': bool(allow_custom),
                'multiple_selection': bool(multi_sel),
                'required': bool(required),
                'default_item': default,
                'context': ctx,
                'items': items
            }
    
    def get_dictionary_list_items(self, list_id):
        """Pobiera elementy listy słownikowej"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, value, order_index FROM dictionary_list_items 
                WHERE list_id = ? ORDER BY order_index, value
            ''', (list_id,))
            return cursor.fetchall()
    
    def add_dictionary_list_item(self, list_id, value, description=""):
        """Dodaje element do listy słownikowej"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Pobierz następny order_index
            cursor.execute('SELECT MAX(order_index) FROM dictionary_list_items WHERE list_id = ?', (list_id,))
            result = cursor.fetchone()
            next_order = (result[0] or 0) + 1
            
            cursor.execute('''
                INSERT INTO dictionary_list_items (list_id, value, order_index) 
                VALUES (?, ?, ?)
            ''', (list_id, value, next_order))
            conn.commit()
            return cursor.lastrowid
    
    def delete_dictionary_list_item(self, item_id):
        """Usuwa element z listy słownikowej"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM dictionary_list_items WHERE id = ?', (item_id,))
            conn.commit()
    
    def delete_dictionary_list(self, list_id):
        """Usuwa listę słownikową i wszystkie jej elementy"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Usuń wszystkie elementy listy
            cursor.execute('DELETE FROM dictionary_list_items WHERE list_id = ?', (list_id,))
            
            # Usuń samą listę
            cursor.execute('DELETE FROM dictionary_lists WHERE id = ?', (list_id,))
            
            # Zaktualizuj kolumny które używały tej listy (ustaw dictionary_list_id na NULL)
            cursor.execute('UPDATE user_table_columns SET dictionary_list_id = NULL WHERE dictionary_list_id = ?', (list_id,))
            
            conn.commit()
            print(f"Usunięto listę słownikową ID: {list_id}")

    # Metody zarządzania szerokościami kolumn
    def save_column_widths(self, table_id, column_widths):
        """Zapisuje szerokości kolumn dla tabeli"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for column_index, width in enumerate(column_widths):
                cursor.execute('''
                    INSERT OR REPLACE INTO table_column_widths (table_id, column_index, width, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (table_id, column_index, width))
            
            conn.commit()
            print(f"DEBUG: Zapisano szerokości kolumn dla tabeli {table_id}: {column_widths}")

    def get_column_widths(self, table_id):
        """Pobiera zapisane szerokości kolumn dla tabeli"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT column_index, width 
                FROM table_column_widths 
                WHERE table_id = ? 
                ORDER BY column_index
            ''', (table_id,))
            
            widths = {}
            for column_index, width in cursor.fetchall():
                widths[column_index] = width
            
            print(f"DEBUG: Załadowano szerokości kolumn dla tabeli {table_id}: {widths}")
            return widths

    def delete_column_widths(self, table_id):
        """Usuwa zapisane szerokości kolumn dla tabeli"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM table_column_widths WHERE table_id = ?', (table_id,))
            conn.commit()

    # === ZARZĄDZANIE NOTATKAMI ===
    
    def add_note(self, title, content='', parent_id=None):
        """Dodaje nową notatkę"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notes (title, content, parent_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (title, content, parent_id))
            conn.commit()
            return cursor.lastrowid
    
    def update_note(self, note_id, title=None, content=None):
        """Aktualizuje notatkę"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if title is not None and content is not None:
                cursor.execute('''
                    UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (title, content, note_id))
            elif title is not None:
                cursor.execute('''
                    UPDATE notes SET title = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (title, note_id))
            elif content is not None:
                cursor.execute('''
                    UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (content, note_id))
            
            conn.commit()
    
    def delete_note(self, note_id):
        """Usuwa notatkę i wszystkie jej podnotatki (CASCADE)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            conn.commit()
    
    def get_all_notes(self):
        """Pobiera wszystkie notatki"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, content, parent_id, created_at, updated_at
                FROM notes ORDER BY created_at
            ''')
            notes = cursor.fetchall()
            
            # Konwertuj na słowniki
            notes_list = []
            for note in notes:
                notes_list.append({
                    'id': note[0],
                    'title': note[1],
                    'content': note[2],
                    'parent_id': note[3],
                    'created_at': note[4],
                    'updated_at': note[5]
                })
            
            return notes_list
    
    def get_note_by_id(self, note_id):
        """Pobiera notatkę po ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, content, parent_id, created_at, updated_at
                FROM notes WHERE id = ?
            ''', (note_id,))
            note = cursor.fetchone()
            
            if note:
                return {
                    'id': note[0],
                    'title': note[1],
                    'content': note[2],
                    'parent_id': note[3],
                    'created_at': note[4],
                    'updated_at': note[5]
                }
            return None
    
    def get_notes_by_parent(self, parent_id):
        """Pobiera podnotatki dla danego rodzica"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, content, parent_id, created_at, updated_at
                FROM notes WHERE parent_id = ? ORDER BY created_at
            ''', (parent_id,))
            notes = cursor.fetchall()
            
            notes_list = []
            for note in notes:
                notes_list.append({
                    'id': note[0],
                    'title': note[1],
                    'content': note[2],
                    'parent_id': note[3],
                    'created_at': note[4],
                    'updated_at': note[5]
                })
            
            return notes_list
    
    # ==================== Metody zarządzania kolumnami zadań ====================
    
    def get_task_columns(self):
        """Pobiera wszystkie kolumny zadań"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, type, visible, in_panel, default_value, column_order, dictionary_list_id
                FROM task_columns
                ORDER BY column_order
            ''')
            columns = cursor.fetchall()
            
            columns_list = []
            for col in columns:
                columns_list.append({
                    'id': col[0],
                    'name': col[1],
                    'type': col[2],
                    'visible': bool(col[3]),
                    'in_panel': bool(col[4]),
                    'default_value': col[5] or '',
                    'column_order': col[6],
                    'dictionary_list_id': col[7]
                })
            
            return columns_list
    
    def get_panel_columns(self):
        """Pobiera kolumny oznaczone do wyświetlania w dolnym panelu"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, type, visible, in_panel, default_value, column_order, dictionary_list_id
                FROM task_columns 
                WHERE in_panel = 1
                ORDER BY column_order
            ''')
            columns = cursor.fetchall()
            
            columns_list = []
            for col in columns:
                columns_list.append({
                    'id': col[0],
                    'name': col[1],
                    'type': col[2],
                    'visible': bool(col[3]),
                    'in_panel': bool(col[4]),
                    'default_value': col[5] or '',
                    'column_order': col[6],
                    'dictionary_list_id': col[7]
                })
            
            return columns_list
    
    def add_task_column(self, name, col_type, visible=True, in_panel=False, default_value='', dictionary_list_id=None):
        """Dodaje nową kolumnę zadania"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Pobierz maksymalny numer porządkowy
            cursor.execute('SELECT MAX(column_order) FROM task_columns')
            max_order = cursor.fetchone()[0]
            next_order = (max_order or 0) + 1
            
            cursor.execute('''
                INSERT INTO task_columns (name, type, visible, in_panel, default_value, column_order, dictionary_list_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, col_type, visible, in_panel, default_value, next_order, dictionary_list_id))
            
            conn.commit()
            return cursor.lastrowid
    
    def update_task_column(self, column_id, name=None, col_type=None, visible=None, in_panel=None, default_value=None, dictionary_list_id=None, column_order=None):
        """Aktualizuje kolumnę zadania"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Pobierz aktualną kolumnę
            cursor.execute('SELECT name, type, visible, in_panel, default_value, dictionary_list_id, column_order FROM task_columns WHERE id = ?', (column_id,))
            current = cursor.fetchone()
            
            if not current:
                return False
            
            # Użyj nowych wartości lub zachowaj obecne
            new_name = name if name is not None else current[0]
            new_type = col_type if col_type is not None else current[1]
            new_visible = visible if visible is not None else bool(current[2])
            new_in_panel = in_panel if in_panel is not None else bool(current[3])
            new_default = default_value if default_value is not None else current[4]
            new_dict_list = dictionary_list_id if dictionary_list_id is not None else current[5]
            new_order = column_order if column_order is not None else current[6]
            
            cursor.execute('''
                UPDATE task_columns
                SET name = ?, type = ?, visible = ?, in_panel = ?, default_value = ?, dictionary_list_id = ?, column_order = ?
                WHERE id = ?
            ''', (new_name, new_type, new_visible, new_in_panel, new_default, new_dict_list, new_order, column_id))
            
            conn.commit()
            return True
    
    def update_task_column_by_name(self, column_name, name=None, col_type=None, visible=None, in_panel=None, default_value=None, dictionary_list_id=None, column_order=None):
        """Aktualizuje kolumnę zadania przez nazwę (dla kolumn standardowych)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Pobierz aktualną kolumnę
            cursor.execute('SELECT id, name, type, visible, in_panel, default_value, dictionary_list_id, column_order FROM task_columns WHERE name = ?', (column_name,))
            current = cursor.fetchone()
            
            if not current:
                return False
            
            column_id = current[0]
            
            # Użyj nowych wartości lub zachowaj obecne
            new_name = name if name is not None else current[1]
            new_type = col_type if col_type is not None else current[2]
            new_visible = visible if visible is not None else bool(current[3])
            new_in_panel = in_panel if in_panel is not None else bool(current[4])
            new_default = default_value if default_value is not None else current[5]
            new_dict_list = dictionary_list_id if dictionary_list_id is not None else current[6]
            new_order = column_order if column_order is not None else current[7]
            
            cursor.execute('''
                UPDATE task_columns
                SET name = ?, type = ?, visible = ?, in_panel = ?, default_value = ?, dictionary_list_id = ?, column_order = ?
                WHERE id = ?
            ''', (new_name, new_type, new_visible, new_in_panel, new_default, new_dict_list, new_order, column_id))
            
            conn.commit()
            return True
    
    def delete_task_column(self, column_id):
        """Usuwa kolumnę zadania"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM task_columns WHERE id = ?', (column_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def set_setting(self, key, value):
        """Zapisuje ustawienie do bazy danych"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO app_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, str(value)))
                conn.commit()
        except Exception as e:
            print(f"Błąd podczas zapisywania ustawienia {key}: {e}")
    
    def get_setting(self, key, default=None):
        """Pobiera ustawienie z bazy danych"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM app_settings WHERE key = ?', (key,))
                result = cursor.fetchone()
                return result[0] if result else default
        except Exception as e:
            print(f"Błąd podczas odczytu ustawienia {key}: {e}")
            return default

# Test bazy danych
if __name__ == "__main__":
    db = Database()
    print("Baza danych została zainicjalizowana!")
    
    # Dodaj przykładowe zadanie
    task_id = db.add_task(
        title="Przykładowe zadanie",
        description="To jest test bazy danych",
        category="Praca"
    )
    print(f"Dodano zadanie o ID: {task_id}")
    
    # Pobierz zadania
    tasks = db.get_tasks()
    print(f"Liczba zadań w bazie: {len(tasks)}")
    
    # Pobierz kategorie
    categories = db.get_categories()
    print(f"Dostępne kategorie: {[cat[1] for cat in categories]}")
