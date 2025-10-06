import time as ti
import random as Ra
import paho.mqtt.publish as MyPub

# URL del broker MQTT (Mosquitto local)
MQTT_HOST = '127.0.0.1'

# Topicos usados por los clientes suscriptores
TOPICS = ['DATA/MP', 'DATA/MA']  # MP = Material Particulado / MA = Medio Ambiente

# -------------------------------------------------------------
# Funciones de generacion de datos simulados
# -------------------------------------------------------------
def Get_MP():
    """Material particulado (3 valores)"""
    nMP01 = Ra.randint(0, 10)   # MP 01 um
    nMP25 = Ra.randint(10, 50)  # MP 25 um
    nMP10 = Ra.randint(10, 50)  # MP 10 um
    return f"{nMP01},{nMP25},{nMP10}"

def Get_MA():
    """Medio ambiente (2 valores)"""
    nTe  = Ra.randint(10, 22)   # Temperatura °C
    nHr  = Ra.randint(60, 85)   # Humedad relativa %
    return f"{nTe},{nHr}"

# -------------------------------------------------------------
# Bucle principal de publicacion
# -------------------------------------------------------------
if __name__ == "__main__":
    while True:
        # Mensajes generados
        msg_mp = Get_MP()
        msg_ma = Get_MA()

        # Publicacion a ambos topicos (para acelerar pruebas)
        MyPub.single(TOPICS[0], msg_mp, hostname=MQTT_HOST)
        MyPub.single(TOPICS[1], msg_ma, hostname=MQTT_HOST)

        # Mostrar por consola
        print(f"TX: {TOPICS[0]} {msg_mp} | {TOPICS[1]} {msg_ma}")

        ti.sleep(5)  # Publica cada 5 segundos
