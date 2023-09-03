import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime

# Constantes
HOST = '127.0.0.1'
PORT = 9191
BUFFER_SIZE = 1024

# Lista para mantener a todos los clientes conectados
clientes = []
nombres_clientes = {}  # Diccionario para almacenar los nombres de los clientes con su socket como clave
nombres_clientes = {}

# Crear socket del servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen()

#Creación de función bitacora
def escribir_en_bitacora(mensaje):
    with open("bitacora_servidor.log", "a") as f:
        f.write(mensaje + "\n")

def formato_registro(nombre_remitente, nombre_destinatario, mensaje):
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"[{fecha_hora}] De: {nombre_remitente} - Para: {nombre_destinatario} - Mensaje: {mensaje}"

def manejar_cliente(cliente):
    nombre = nombres_clientes[cliente]
    
    while True:
        try:
            # Recibir mensaje del cliente
            mensaje = cliente.recv(BUFFER_SIZE).decode()
            
            # Handling file reception
            if mensaje.startswith('ARCHIVO:'):
                # Extracting file details from the message
                _, file_name, file_size_str = mensaje.split(':')
                file_size = int(file_size_str)
                # Preparing to receive the file
                chunks = []
                bytes_received = 0
                while bytes_received < file_size:
                    chunk = cliente.recv(min(BUFFER_SIZE, file_size - bytes_received))
                    chunks.append(chunk)
                    bytes_received += len(chunk)
                file_data = b''.join(chunks)
                # Saving the received file
                with open(f'recepcion_{file_name}', 'wb') as file:
                    file.write(file_data)
                print(f'[SERVER] Archivo {file_name} recibido.')
                
                # Enviar el mensaje a todos los clientes excepto al que envió el mensaje
                #mensaje_a_enviar = f"{nombre} ha enviado {mensaje}Bytes."
                for c in clientes:
                    if c != cliente:
                        #c.send(mensaje_a_enviar.encode())
                        c.send(f'ARCHIVO:{file_name}:{file_size}'.encode())
                        c.sendall(file_data)
                        print(f'[SERVER] Archivo {file_name} enviado.')
                        # Escribir el mensaje en la bitácora con el formato requerido
                        registro = formato_registro(nombre, nombres_clientes[c], mensaje)
                        escribir_en_bitacora(registro)
                    else:
                        registro = formato_registro(nombre, "ninguno", mensaje)
                        escribir_en_bitacora(registro)
            else:
                # Enviar el mensaje a todos los clientes excepto al que envió el mensaje
                mensaje_a_enviar = f"{nombre}: {mensaje}"
                for c in clientes:
                    if c != cliente:
                        c.send(mensaje_a_enviar.encode())
                        # Escribir el mensaje en la bitácora con el formato requerido
                        registro = formato_registro(nombre, nombres_clientes[c], mensaje)
                        escribir_en_bitacora(registro)
                    else:
                        registro = formato_registro(nombre, "ninguno", mensaje)
                        escribir_en_bitacora(registro)
        
        except:
            # Eliminar cliente si hay algún problema
            clientes.remove(cliente)
            del nombres_clientes[cliente]
            # Enviar a todos los clientes que alguien se ha conectado
            for c in clientes:
                c.send(f"[SERVER] {nombre} se ha desconectado del chat".encode())
            cliente.close()
            fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            agregar_al_historial(f"[{fecha_hora}] {nombre} se ha desconectado.")
            actualizar_interfaz()
            break

def manejar_servidor():
    while True:
        # Esperar una nueva conexión
        cliente, direccion = servidor.accept()
        
        # Recibir nombre del cliente
        nombre_cliente = cliente.recv(BUFFER_SIZE).decode()
        # Verificar si el nombre del cliente ya está en uso
        while nombre_cliente in nombres_clientes.values():
            cliente.send('[SERVER] Este nombre ya está en uso. Por favor, elige otro.'.encode())
            nombre_cliente = cliente.recv(BUFFER_SIZE).decode()
        # Una vez que tengamos un nombre único, lo agregamos al diccionario
        nombres_clientes[cliente] = nombre_cliente
        nombres_clientes[cliente] = nombre_cliente
        cliente.send(f"[SERVER] Bienvenido {nombre_cliente} al chat".encode())

        # Enviar a todos los clientes que alguien se ha conectado
        for c in clientes:
            c.send(f"[SERVER] {nombre_cliente} se ha conectado al chat".encode())

        clientes.append(cliente)
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        agregar_al_historial(f"[{fecha_hora}] {nombre_cliente} se ha conectado desde {direccion}.")
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

    # Escribir el mensaje en la bitácora
    escribir_en_bitacora(mensaje)
    
def on_closing():
    if len(clientes) > 0:
        messagebox.showwarning("Advertencia", "No se puede cerrar el servidor con clientes conectados.")
    else:
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        escribir_en_bitacora(f"[{fecha_hora}] Se ha cerrado el servidor.")
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
fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
agregar_al_historial(f"[{fecha_hora}] Servidor ejecutándose en {HOST}:{PORT}")

boton_cerrar = tk.Button(ventana, text="Cerrar Servidor", command=on_closing, state=tk.DISABLED)
boton_cerrar.pack(pady=10)

ventana.protocol("WM_DELETE_WINDOW", on_closing)
ventana.mainloop()
