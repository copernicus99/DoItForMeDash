#define MyAppName "DoItForMe Dash"
#define MyAppVersion "1.4.5"
#define MyAppExeName "DoItForMeDash.exe"
[Setup]
AppId={{7DAD6BE4-962D-491D-B19E-8C6F7A4E2B62}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Programs\DoItForMe Dash
DefaultGroupName=DoItForMe Dash
PrivilegesRequired=lowest
OutputDir=..\installer
OutputBaseFilename=DoItForMeDash_Setup_1.4.5
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
[Files]
Source: "..\dist\START_DASHBOARD.dist\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
[Icons]
Name: "{group}\DoItForMe Dash"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\DoItForMe Dash"; Filename: "{app}\{#MyAppExeName}"
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch DoItForMe Dash"; Flags: nowait postinstall skipifsilent
