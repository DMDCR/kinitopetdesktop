@echo OFF
title KinitoPET Desktop Pet Builder
echo This project requires Python 3.10+, please make sure you have a 3.10+ version of Python, then continue!
echo Please continue to build Kinito!
pause;
echo Continuing will Download PyInstaller and the requirements for running the project, are you sure?
echo Please exit Command Prompt/Terminal if you do not want to continue, if you still want to continue, press any key.
pause;
pip install pyinstaller
pip install pillow
pip install pygame
pip install pystray
pip install requests
echo Building Kinito
pyinstaller -w -F --clean --icon=icon.ico --additional-hooks-dir=hooks --hidden-import=requests kinito.py
echo Please check the "dist" folder, if the exe is there, continue
pause;
xcopy /s /e /v /i "./models" "./dist/models"
xcopy /s /e /v /i "./other" "./dist/other"
xcopy /s /e /v /i "./cmd" "./dist/cmd"
echo Done!
pause;
