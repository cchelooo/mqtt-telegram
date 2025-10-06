# execute.py
import subprocess
import time

# Publicador (el del profesor)
pub = subprocess.Popen(["python", "main.py"])

# Espera un poco antes de iniciar los clientes
time.sleep(2)

# Lista de carpetas de clientes
clients = ["client00", "client01", "client02", "client03"]
processes = []

# Arranca cada cliente en una nueva ventana o pestaña (Linux/EndeavourOS)
for c in clients:
    cmd = f'konsole --new-tab -e bash -c "cd ~/mqtt_telegram/{c}; source ../.venv/bin/activate; python ../mqtt_subscriber_telegram.py; exec bash"'
    processes.append(subprocess.Popen(cmd, shell=True))
    time.sleep(0.5)

pub.wait()
