# main.py  (Publisher)
import time as ti
import random as Ra
import paho.mqtt.publish as MyPub

BROKER_HOST = "127.0.0.1"     # Mosquitto local
TOP_MP = "DATA/MP"            # MP01, MP2.5, MP10
TOP_MA = "DATA/MA"            # Temperatura, HR

def get_mp():
    # Material particulado simulado (ajusta rangos si quieres)
    mp01 = Ra.randint(0, 40)      # MP 0-1um
    mp25 = Ra.randint(10, 50)     # MP 2.5um
    mp10 = Ra.randint(10, 50)     # MP 10um
    return f"{mp01},{mp25},{mp10}"

def get_ma():
    # Medio ambiente simulado
    te  = Ra.randint(10, 30)      # Temperatura
    hr  = Ra.randint(40, 90)      # Humedad Relativa
    return f"{te},{hr}"

if __name__ == "__main__":
    print("Publisher iniciado. Enviando a DATA/MP y DATA/MA cada 5s...")
    while True:
        mp_payload = get_mp()
        ma_payload = get_ma()
        # Publica a ambos tópicos
        MyPub.single(TOP_MP, mp_payload, hostname=BROKER_HOST)
        MyPub.single(TOP_MA, ma_payload, hostname=BROKER_HOST)
        print("TX:", TOP_MP, mp_payload, "|", TOP_MA, ma_payload)
        ti.sleep(5)  # cada 5 segundos
