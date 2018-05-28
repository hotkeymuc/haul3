@ECHO OFF
python test_ide.py
IF ERRORLEVEL 1 GOTO:ERROR
GOTO:END

:ERROR
ECHO ERROR has happened - pausing...
PAUSE

:END
ECHO End.
