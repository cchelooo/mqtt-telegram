@echo off
cd /d %~dp0
call .venv\Scripts\activate

start cmd /k "python main.py"
start cmd /k "cd client00 && ..\.venv\Scripts\python ..\mqtt_subscriber_telegram.py"
start cmd /k "cd client01 && ..\.venv\Scripts\python ..\mqtt_subscriber_telegram.py"
start cmd /k "cd client02 && ..\.venv\Scripts\python ..\mqtt_subscriber_telegram.py"
start cmd /k "cd client03 && ..\.venv\Scripts\python ..\mqtt_subscriber_telegram.py"

echo Todos los procesos iniciados.
pause
