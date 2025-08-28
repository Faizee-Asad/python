; Inno Setup Script for DineDash POS

[Setup]
AppName=DineDash POS
AppVersion=1.0
DefaultDirName={autopf}\DineDashPOS
DefaultGroupName=DineDash POS
UninstallDisplayIcon={app}\main.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
OutputBaseFilename=DineDash_POS_Setup_v1.0

[Files]
; This tells the installer to take your generated main.exe and place it in the installation directory.
Source: "E:\GITHUB\python\gemini_License\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Create a Start Menu shortcut
Name: "{group}\DineDash POS"; Filename: "{app}\main.exe"
; Create a Desktop shortcut
Name: "{autodesktop}\DineDash POS"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:";

[Run]
Filename: "{app}\main.exe"; Description: "Launch DineDash POS"; Flags: nowait postinstall skipifsilent