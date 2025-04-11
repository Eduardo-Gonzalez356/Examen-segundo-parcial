# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 14:28:49 2025
@author: usuario
"""

import tkinter as tk
from PIL import Image, ImageTk
import requests
from pyfirmata import Arduino, util
import threading
import time

# Dirección IP de la Raspberry Pi Pico W
pico_ip = "192.168.1.110"  # Cambia esta IP por la de tu Pico W

# Configuración de Arduino
arduino_port = "COM4"  # Cambia este puerto según tu configuración
joystick_activo = False
tecla_presionada = False  # NUEVO: bandera para evitar interferencia del joystick

try:
    board = Arduino(arduino_port)
    it = util.Iterator(board)
    it.start()

    # Pines del joystick
    x_pin = board.get_pin('a:3:i')  # Eje X
    y_pin = board.get_pin('a:2:i')  # Eje Y
    x_pin.enable_reporting()
    y_pin.enable_reporting()
    joystick_activo = True
    print("Joystick conectado correctamente")
except Exception as e:
    print(f"Error al conectar con Arduino: {e}")
    joystick_activo = False

ultimo_comando = None
zona_muerta = 0.3
umbral_mov = 0.4  # Ajuste del umbral para mayor precisión en el movimiento

def enviar_comando(comando):
    global ultimo_comando
    if comando != ultimo_comando:
        try:
            url = f"http://{pico_ip}/{comando}"
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print(f"Comando {comando} enviado con éxito")
                actualizar_estado(comando)
            else:
                print(f"Error al enviar {comando}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            estado.config(text="Error de conexión", fg="red")
        ultimo_comando = comando

def actualizar_estado(comando):
    estados = {
        "adelante": "Adelante (W/↑)",
        "atras": "Atrás (S/↓)",
        "girar_derecha": "Derecha (D/→)",
        "girar_izquierda": "Izquierda (A/←)",
        "detener": "Detenido (Espacio)"
    }
    estado.config(text=f"Estado: {estados.get(comando, comando)}", fg="green")

def manejar_tecla(event):
    global tecla_presionada
    tecla = event.keysym.lower()
    tecla_presionada = True  # NUEVO: se activa cuando se presiona una tecla

    if tecla == 'w' or event.keysym == "Up":
        enviar_comando("adelante")
    elif tecla == 's' or event.keysym == "Down":
        enviar_comando("atras")
    elif tecla == 'd' or event.keysym == "Right":
        enviar_comando("girar_derecha")
    elif tecla == 'a' or event.keysym == "Left":
        enviar_comando("girar_izquierda")
    elif event.keysym == "space":
        enviar_comando("detener")

def soltar_tecla(event):
    global tecla_presionada
    tecla = event.keysym.lower()
    if tecla in ['w', 'a', 's', 'd'] or event.keysym in ["Up", "Down", "Left", "Right"]:
        estado.config(text="Estado: Esperando comando...")
        tecla_presionada = False  # NUEVO: se desactiva al soltar la tecla

def actualizar_joystick():
    try:
        x_val = x_pin.read()
        y_val = y_pin.read()

        if x_val is not None and y_val is not None:
            x = x_val * 2 - 1
            y = y_val * 2 - 1

            if abs(x) < zona_muerta and abs(y) < zona_muerta:
                enviar_comando("detener")
            else:
                if abs(y) > abs(x):
                    if y > umbral_mov:
                        enviar_comando("adelante")
                    elif y < -umbral_mov:
                        enviar_comando("atras")
                else:
                    if abs(x) > umbral_mov:  # Asegurando que cualquier cambio en X sea detectado
                        if x > 0:
                            enviar_comando("girar_derecha")
                        elif x < 0:
                            enviar_comando("girar_izquierda")
    except Exception as e:
        print(f"Error leyendo joystick: {e}")

def leer_joystick():
    while joystick_activo:
        if not tecla_presionada:  # NUEVO: solo lee joystick si no hay tecla presionada
            actualizar_joystick()
        time.sleep(0.1)

def cerrar():
    if joystick_activo:
        board.exit()
    root.destroy()

root = tk.Tk()
root.title("Control de Carro - Teclas y Joystick")
root.geometry("600x700")
root.configure(bg='#f0f0f0')
font_style = ('Arial', 12)

# Instrucciones
instrucciones = tk.Label(root, text="Controles:\nW/Flecha Arriba - Adelante\nS/Flecha Abajo - Atrás\nA/Flecha Izquierda - Izquierda\nD/Flecha Derecha - Derecha\nEspacio - Detener", font=font_style, bg='#f0f0f0')
instrucciones.pack(pady=20)

estado = tk.Label(root, text="Estado: Esperando comando...", font=('Arial', 14, 'bold'), bg='#f0f0f0')
estado.pack(pady=10)

# Imágenes
ruta_flecha_arriba = r"C:\Users\usuario\Documents\Mis programas\Imagenes\up.png"
ruta_flecha_abajo = r"C:\Users\usuario\Documents\Mis programas\Imagenes\down.png"
ruta_flecha_derecha = r"C:\Users\usuario\Documents\Mis programas\Imagenes\rigth.png"
ruta_flecha_izquierda = r"C:\Users\usuario\Documents\Mis programas\Imagenes\left.png"
ruta_detener = r"C:\Users\usuario\Documents\Mis programas\Imagenes\Stop.png"

try:
    flecha_arriba = ImageTk.PhotoImage(Image.open(ruta_flecha_arriba).resize((100, 100)))
    flecha_abajo = ImageTk.PhotoImage(Image.open(ruta_flecha_abajo).resize((100, 100)))
    flecha_derecha = ImageTk.PhotoImage(Image.open(ruta_flecha_derecha).resize((100, 100)))
    flecha_izquierda = ImageTk.PhotoImage(Image.open(ruta_flecha_izquierda).resize((100, 100)))
    imagen_detener = ImageTk.PhotoImage(Image.open(ruta_detener).resize((400, 100)))

    marco_controles = tk.Frame(root, bg='#f0f0f0')
    marco_controles.pack(pady=20)

    tk.Button(marco_controles, image=flecha_arriba, command=lambda: enviar_comando("adelante")).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(marco_controles, text="W/↑", font=font_style, bg='#f0f0f0').grid(row=1, column=1)

    tk.Button(marco_controles, image=flecha_izquierda, command=lambda: enviar_comando("girar_izquierda")).grid(row=1, column=0, padx=5, pady=5)
    tk.Label(marco_controles, text="A/←", font=font_style, bg='#f0f0f0').grid(row=2, column=0)

    tk.Button(marco_controles, image=flecha_derecha, command=lambda: enviar_comando("girar_derecha")).grid(row=1, column=2, padx=5, pady=5)
    tk.Label(marco_controles, text="D/→", font=font_style, bg='#f0f0f0').grid(row=2, column=2)

    tk.Button(marco_controles, image=flecha_abajo, command=lambda: enviar_comando("atras")).grid(row=2, column=1, padx=5, pady=5)
    tk.Label(marco_controles, text="S/↓", font=font_style, bg='#f0f0f0').grid(row=3, column=1)

    tk.Button(root, image=imagen_detener, command=lambda: enviar_comando("detener")).pack(pady=20)
    tk.Label(root, text="ESPACIO", font=font_style, bg='#f0f0f0').pack()

except FileNotFoundError as e:
    print(f"Error al cargar imágenes: {e}")
    tk.Button(root, text="W/↑ - Adelante", command=lambda: enviar_comando("adelante")).pack(pady=5)
    tk.Button(root, text="S/↓ - Atrás", command=lambda: enviar_comando("atras")).pack(pady=5)
    tk.Button(root, text="A/← - Izquierda", command=lambda: enviar_comando("girar_izquierda")).pack(pady=5)
    tk.Button(root, text="D/→ - Derecha", command=lambda: enviar_comando("girar_derecha")).pack(pady=5)
    tk.Button(root, text="ESPACIO - Detener", command=lambda: enviar_comando("detener")).pack(pady=20)

# Eventos de teclado
root.bind("<KeyPress>", manejar_tecla)
root.bind("<KeyRelease>", soltar_tecla)

# Hilo del joystick
if joystick_activo:
    joystick_thread = threading.Thread(target=leer_joystick, daemon=True)
    joystick_thread.start()

root.protocol("WM_DELETE_WINDOW", cerrar)
root.focus_set()
root.mainloop()

