@echo OFF
title sigma
echo Please continue to build kinito!
pause;
echo Building Kinito
pyinstaller -w -F --icon=icon.ico kinito.py
echo Please check the "dist" folder, if the exe is there, continue
pause;
xcopy /s /e /v /i "./audio" "./dist/audio"
xcopy /s /e /v /i "./gifs" "./dist/gifs"
xcopy /s /e /v /i "./other" "./dist/other"
echo Done!
pause;