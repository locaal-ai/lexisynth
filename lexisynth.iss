[Setup]
AppName=LexiSynth
AppVersion=0.0.1-beta1
DefaultDirName={pf}\LexiSynth
DefaultGroupName=LexiSynth
OutputDir=.\dist
OutputBaseFilename=lexisynth-setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\lexisynth\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\LexiSynth"; Filename: "{app}\lexisynth.exe"

[Run]
Filename: "{app}\lexisynth.exe"; Description: "Launch LexiSynth"; Flags: nowait postinstall skipifsilent
