; Skrypt Inno Setup dla Pro-Ka-Po
; Wymaga: Zbudowanego exe z PyInstaller (dist\Pro-Ka-Po.exe)
; Użycie: Otwórz ten plik w Inno Setup Compiler i kliknij "Compile"

#define MyAppName "Pro-Ka-Po"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Pro-Ka-Po Team"
#define MyAppURL "https://github.com/Piotr19881/Pro-Ka-Po"
#define MyAppExeName "Pro-Ka-Po.exe"

[Setup]
; UWAGA: Wartość AppId jednoznacznie identyfikuje aplikację.
; Nie używaj tej samej wartości AppId w innych instalatorach.
AppId={{B8F9A3D2-1E4C-4A5B-9F2D-6E8A7C3B1D4F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
; Usuń komentarz z następnej linii aby uruchomić w trybie "non administrative install mode" (zainstaluj tylko dla bieżącego użytkownika)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=installer_output
OutputBaseFilename=Pro-Ka-Po_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "autostart"; Description: "Uruchom automatycznie z systemem Windows"; GroupDescription: "Dodatkowe opcje:"; Flags: unchecked

[Files]
; GŁÓWNY PLIK EXE
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; UWAGA: Nie używaj "Flags: ignoreversion" na plikach współdzielonych systemowych

; Jeśli używasz folderu zamiast pojedynczego exe (--onedir zamiast --onefile):
; Source: "dist\Pro-Ka-Po\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; DODATKOWE PLIKI (opcjonalnie)
; Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
; Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Autostart (jeśli użytkownik zaznaczył opcję)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  OldVersion: String;
begin
  Result := True;
  
  // Sprawdź czy stara wersja jest zainstalowana
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1', 'UninstallString', OldVersion) then
  begin
    if MsgBox('Wykryto starszą wersję aplikacji. Czy chcesz ją najpierw odinstalować?' + #13#10 + #13#10 +
              'Zalecane jest odinstalowanie starej wersji przed instalacją nowej.', mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Uruchom deinstalator starej wersji
      Exec(RemoveQuotes(OldVersion), '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Tutaj możesz dodać dodatkowe akcje po instalacji
    // np. tworzenie bazy danych, konfiguracji itp.
  end;
end;

function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Sprawdź czy aplikacja jest uruchomiona
  if CheckForMutexes('{#MyAppName}') then
  begin
    MsgBox('Aplikacja {#MyAppName} jest obecnie uruchomiona.' + #13#10 + #13#10 +
           'Zamknij aplikację przed odinstalowaniem.', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  mRes: Integer;
begin
  case CurUninstallStep of
    usUninstall:
    begin
      // Zapytaj czy usunąć dane użytkownika
      mRes := MsgBox('Czy chcesz również usunąć dane aplikacji (baza danych, ustawienia)?' + #13#10 + #13#10 +
                     'Jeśli planujesz ponowną instalację, możesz je zachować.', 
                     mbConfirmation, MB_YESNO or MB_DEFBUTTON2);
      
      if mRes = IDYES then
      begin
        // Usuń folder z danymi w AppData użytkownika (jeśli istnieje)
        DelTree(ExpandConstant('{userappdata}\{#MyAppName}'), True, True, True);
        
        // Usuń folder data w folderze instalacji
        DelTree(ExpandConstant('{app}\data'), True, True, True);
      end;
    end;
  end;
end;
