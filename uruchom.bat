@echo off
REM Uruchamia aplikację Pro-Ka-Po V2 bez pokazywania okna konsoli

REM Sprawdź czy istnieje wirtualne środowisko
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "main.py"
) else if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" "main.py"
) else (
    REM Jeśli nie ma venv, użyj systemowego Python
    start "" pythonw.exe "main.py"
)
