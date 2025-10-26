from src.database.db_manager import Database

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

# Sprawdź czy kolumna color już istnieje
cursor.execute('PRAGMA table_info(user_table_columns)')
columns = [col[1] for col in cursor.fetchall()]

if 'color' not in columns:
    cursor.execute('ALTER TABLE user_table_columns ADD COLUMN color TEXT DEFAULT "#ffffff"')
    conn.commit()
    print('Dodano kolumnę color do user_table_columns')
else:
    print('Kolumna color już istnieje')

print("\nAktualna struktura tabeli user_table_columns:")
cursor.execute('PRAGMA table_info(user_table_columns)')
columns = cursor.fetchall()
for col in columns:
    print(f'{col[1]} - {col[2]} (NOT NULL: {bool(col[3])})')