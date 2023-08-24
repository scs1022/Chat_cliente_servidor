import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Constantes
HOST = '127.0.0.1'
PORT = 12345
BUFFER_SIZE = 1024

# Lista para mantener a todos los clientes conectados
clientes = []
nombres_clientes = {}

# Crear socket del servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen()

def manejar_cliente(cliente):
    nombre = nombres_clientes[cliente]
    
    while True:
        try:
            # Recibir mensaje del cliente
            mensaje = cliente.recv(BUFFER_SIZE).decode()
            
            # Enviar el mensaje a todos los clientes excepto al que envió el mensaje
            mensaje_a_enviar = f"{nombre}: {mensaje}"
            for c in clientes:
                if c != cliente:
                    c.send(mensaje_a_enviar.encode())
        
        except:
            # Eliminar cliente si hay algún problema
            clientes.remove(cliente)
            del nombres_clientes[cliente]
            cliente.close()
            agregar_al_historial(f"{nombre} se ha desconectado.")
            actualizar_interfaz()
            break

def manejar_servidor():
    while True:
        # Esperar una nueva conexión
        cliente, direccion = servidor.accept()
        
        # Recibir nombre del cliente
        nombre_cliente = cliente.recv(BUFFER_SIZE).decode()
        nombres_clientes[cliente] = nombre_cliente
        cliente.send(f"[SERVER] Bienvenido {nombre_cliente} al chat".encode())

        # Enviar a todos los clientes que alguien se ha conectado
        for c in clientes:
            c.send(f"[SERVER] {nombre_cliente} se ha conectado al chat".encode())

        clientes.append(cliente)
        agregar_al_historial(f"{nombre_cliente} se ha conectado desde {direccion}.")
        actualizar_interfaz()

        # Iniciar un nuevo hilo para manejar al cliente
        hilo = threading.Thread(target=manejar_cliente, args=(cliente,))
        hilo.start()

def cerrar_servidor():
    servidor.close()
    ventana.quit()

def actualizar_interfaz():
    texto_var.set(f"Clientes conectados: {len(clientes)}")
    if len(clientes) == 0:
        boton_cerrar.config(state=tk.NORMAL)
    else:
        boton_cerrar.config(state=tk.DISABLED)

def agregar_al_historial(mensaje):
    historial.config(state=tk.NORMAL)  # Habilita la edición solo para insertar el mensaje
    historial.insert(tk.END, mensaje + "\n")
    historial.yview(tk.END)
    historial.config(state=tk.DISABLED)  # Deshabilita la edición después de insertar

def on_closing():
    if len(clientes) > 0:
        messagebox.showwarning("Advertencia", "No se puede cerrar el servidor con clientes conectados.")
    else:
        cerrar_servidor()

# Iniciar el hilo del servidor
threading.Thread(target=manejar_servidor, daemon=True).start()

# Configuración de la ventana del servidor
ventana = tk.Tk()
ventana.title("Servidor de chat")

texto_var = tk.StringVar()
texto_var.set(f"Clientes conectados: {len(clientes)}")

etiqueta = tk.Label(ventana, textvariable=texto_var)
etiqueta.pack(pady=10)

historial = scrolledtext.ScrolledText(ventana, width=50, height=10, state=tk.DISABLED)
historial.pack(pady=10)

# Agregar mensaje inicial sobre el servidor ejecutándose
agregar_al_historial(f"Servidor ejecutándose en {HOST}:{PORT}")

boton_cerrar = tk.Button(ventana, text="Cerrar Servidor", command=on_closing, state=tk.DISABLED)
boton_cerrar.pack(pady=10)

ventana.protocol("WM_DELETE_WINDOW", on_closing)
ventana.mainloop()
