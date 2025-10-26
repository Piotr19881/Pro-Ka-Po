@echo off
echo Uruchamianie Pro-Ka-Po V2...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python main.py
pause