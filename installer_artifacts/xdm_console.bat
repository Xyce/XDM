rem 
rem xdm_console.bat
rem
rem This script spawns a console that has xdm on the path.
rem
START cmd /K "set PATH=%~dp0;%PATH% & cd %HOMEPATH%"

