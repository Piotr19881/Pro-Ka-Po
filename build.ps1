# Skrypt budowania instalatora Pro-Ka-Po
# Wymaga: pip install pyinstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Pro-Ka-Po - Budowanie Instalatora   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Sprawdź czy PyInstaller jest zainstalowany
Write-Host "[1/5] Sprawdzanie PyInstaller..." -ForegroundColor Yellow
try {
    $pyinstaller = pip show pyinstaller 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyInstaller nie jest zainstalowany. Instaluję..." -ForegroundColor Yellow
        pip install pyinstaller
    } else {
        Write-Host "✓ PyInstaller zainstalowany" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Błąd podczas sprawdzania PyInstaller" -ForegroundColor Red
    exit 1
}

# 2. Sprawdź czy UPX jest dostępny (opcjonalnie)
Write-Host ""
Write-Host "[2/5] Sprawdzanie UPX (opcjonalnie)..." -ForegroundColor Yellow
try {
    $upx = upx --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ UPX dostępny - będzie użyty do kompresji" -ForegroundColor Green
    } else {
        Write-Host "! UPX niedostępny - budowanie bez kompresji (większy plik)" -ForegroundColor Yellow
        Write-Host "  Pobierz UPX z: https://github.com/upx/upx/releases" -ForegroundColor Gray
    }
} catch {
    Write-Host "! UPX niedostępny - budowanie bez kompresji" -ForegroundColor Yellow
}

# 3. Wyczyść poprzednie buildy
Write-Host ""
Write-Host "[3/5] Czyszczenie poprzednich buildów..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
Write-Host "✓ Wyczyszczono" -ForegroundColor Green

# 4. Buduj exe
Write-Host ""
Write-Host "[4/5] Budowanie exe..." -ForegroundColor Yellow
Write-Host "To może potrwać kilka minut..." -ForegroundColor Gray
pyinstaller pro-ka-po.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Błąd podczas budowania" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Exe zbudowany" -ForegroundColor Green

# 5. Sprawdź rozmiar
Write-Host ""
Write-Host "[5/5] Sprawdzanie rozmiaru..." -ForegroundColor Yellow
if (Test-Path "dist\Pro-Ka-Po.exe") {
    $size = (Get-Item "dist\Pro-Ka-Po.exe").Length / 1MB
    Write-Host "✓ Rozmiar exe: $([math]::Round($size, 2)) MB" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "        SUKCES!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Plik exe: dist\Pro-Ka-Po.exe" -ForegroundColor White
    Write-Host "Rozmiar: $([math]::Round($size, 2)) MB" -ForegroundColor White
    Write-Host ""
    Write-Host "Następny krok: Stwórz instalator używając Inno Setup" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✗ Nie znaleziono pliku exe!" -ForegroundColor Red
    exit 1
}
