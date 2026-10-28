; Instalador de DinTube (Inno Setup 6). Lo compila construir.ps1 con /DVersion=3.0.N
#ifndef Version
  #define Version "1.0.0"
#endif

[Setup]
AppId={{6B1F2C1E-8C5D-4E7A-9A55-D1A7B0E0D1B7}
AppName=DinTube
AppVersion={#Version}
AppPublisher=Cristian
; Se instala para el usuario (sin pedir admin): así las actualizaciones automáticas no muestran UAC
PrivilegesRequired=lowest
DefaultDirName={autopf}\DinTube
DefaultGroupName=DinTube
DisableProgramGroupPage=yes
DisableDirPage=yes
OutputDir=instalador
OutputBaseFilename=DinTube-Setup
SetupIconFile=build\dintube.ico
UninstallDisplayIcon={app}\DinTube.exe
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=force

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "escritorio"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"
Name: "inicio"; Description: "Abrir DinTube al iniciar Windows (para que el celu y la tele lo encuentren)"; GroupDescription: "Opciones:"; Flags: unchecked

[Files]
; Se reemplaza la carpeta entera para no dejar archivos de versiones viejas
Source: "dist\DinTube\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Icons]
Name: "{group}\DinTube"; Filename: "{app}\DinTube.exe"
Name: "{autodesktop}\DinTube"; Filename: "{app}\DinTube.exe"; Tasks: escritorio
Name: "{userstartup}\DinTube"; Filename: "{app}\DinTube.exe"; Tasks: inicio

[Run]
Filename: "{app}\DinTube.exe"; Description: "Abrir DinTube"; Flags: nowait postinstall skipifsilent
; Actualización automática (instalación silenciosa): vuelve a abrir DinTube al terminar
Filename: "{app}\DinTube.exe"; Flags: nowait; Check: WizardSilent

; Los datos (%LOCALAPPDATA%\DinTube) y los MP3 (Música\DinTube) no se borran al desinstalar.
; La primera vez Windows pregunta si DinTube puede usar la red: permitir en redes privadas (para el celu).
