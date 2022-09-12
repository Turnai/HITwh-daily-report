@echo off
set username=
set password=
set xm=
set xueyuan=
set openid=
@REM call .\venv\Scripts\activate.bat
python main.py %username% %password% %xm% %xueyuan% %openid%
echo finish report!
pause