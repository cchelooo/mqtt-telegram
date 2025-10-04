import os
import time
from collections import deque
from pathlib import Path

# Evita necesitar servidor X para guardar PNG
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import paho.mqtt.client as mqtt
import requests
from dotenv import load_dotenv

# --- Carga de variables de entorno (.env) ---
# 1) Prioridad: el .env de la carpeta donde ESTÁS parado (client00/.env)
# 2) Secundario: el .env junto al script (mqtt_telegram/.env)
cwd_env = Path.cwd() / ".env"
script_env = Path(__file__).parent / ".env"

# Modo verbose para diagnosticar qué .env se cargó
def _load_envs():
    loaded = []
    if cwd_env.exists():
        load_dotenv(dotenv_path=cwd_env, override=False)
        loaded.append(str(cwd_env))
    if script_env.exists():
        load_dotenv(dotenv_path=script_env, override=False)
        loaded.append(str(script_env))
    print("Archivos .env cargados:", loaded if loaded else "ninguno (usando entorno)")
_load_envs()

# --- Configuración MQTT / Telegram ---
MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPICS = [("DATA/MP", 0), ("DATA/MA", 0)]  # (topic, QoS)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # distinto por cada instancia
CHAT_ID = os.getenv("CHAT_ID")      # distinto por cada instancia

# Históricos (10 datos)
hist_mp01 = deque(maxlen=10)
hist_mp25 = deque(maxlen=10)
hist_mp10 = deque(maxlen=10)
hist_temp = deque(maxlen=10)
hist_hr   = deque(maxlen=10)

def ready():
    """¿Tenemos 10 muestras en todas las series?"""
    lens = [len(hist_mp01), len(hist_mp25), len(hist_mp10), len(hist_temp), len(hist_hr)]
    return all(l >= 10 for l in lens)

def make_plot(path="reporte.png"):
    x = list(range(1, 11))

    fig, axes = plt.subplots(5, 1, figsize=(8, 10), sharex=True)
    fig.suptitle("Medición MP1, MP2.5, MP10 - Temp, HR")

    axes[0].plot(x, list(hist_mp01)); axes[0].set_ylabel("µg/m³"); axes[0].legend(["MP01"])
    axes[1].plot(x, list(hist_mp25)); axes[1].set_ylabel("µg/m³"); axes[1].legend(["MP2.5"])
    axes[2].plot(x, list(hist_mp10)); axes[2].set_ylabel("µg/m³"); axes[2].legend(["MP10"])
    axes[3].plot(x, list(hist_temp)); axes[3].set_ylabel("Temp");  axes[3].legend(["Temp"])
    axes[4].plot(x, list(hist_hr  )); axes[4].set_ylabel("HR(%)"); axes[4].legend(["HR"])
    axes[4].set_xlabel("10 Samples")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(path, dpi=120)
    plt.close(fig)
    return path

def send_telegram_photo(path):
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("BOT_TOKEN o CHAT_ID no configurados.")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(path, "rb") as f:
        files = {"photo": f}
        data = {"chat_id": CHAT_ID, "caption": "Reporte MQTT"}
        r = requests.post(url, data=data, files=files, timeout=15)
        r.raise_for_status()

# ---- MQTT callbacks ----
def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Conectado al broker", reason_code)
    for t, qos in MQTT_TOPICS:
        client.subscribe(t, qos=qos)
        print("Suscrito a", t)

def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors="ignore").strip()
    try:
        if msg.topic == "DATA/MP":
            # Esperado: "mp01,mp25,mp10"
            parts = [p.strip() for p in payload.split(",")]
            if len(parts) >= 3:
                mp01, mp25, mp10 = map(float, parts[:3])
                hist_mp01.append(mp01)
                hist_mp25.append(mp25)
                hist_mp10.append(mp10)

        elif msg.topic == "DATA/MA":
            # Esperado: "temp,hr"
            parts = [p.strip() for p in payload.split(",")]
            if len(parts) >= 2:
                temp, hr = map(float, parts[:2])
                hist_temp.append(temp)
                hist_hr.append(hr)

        # Cuando tengamos 10 de cada uno, graficamos y enviamos
        if ready() and BOT_TOKEN and CHAT_ID:
            path = make_plot()
            send_telegram_photo(path)
            print("Reporte enviado a Telegram.")

    except Exception as e:
        print("Error procesando mensaje:", e, "payload=", payload)

def main():
    # Mensaje claro si faltan credenciales
    if not BOT_TOKEN or not CHAT_ID:
        print("Falta BOT_TOKEN o CHAT_ID (usa .env en la carpeta del cliente).")
        print("Valor actual BOT_TOKEN:", "OK" if BOT_TOKEN else "VACÍO")
        print("Valor actual CHAT_ID  :", "OK" if CHAT_ID else "VACÍO")
        return

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
