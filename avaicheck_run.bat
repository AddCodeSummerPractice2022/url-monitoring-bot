@echo off

call %~dp0AvaiCheck_Bot\venv\Scripts\activate

cd %~dp0AvaiCheck_bot

set TOKEN=

python avaicheck_bot_tg.py

pause