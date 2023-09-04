import socket
import threading
import tkinter as tk
from tkinter import Button
import os
from tkinter import simpledialog, scrolledtext

HOST = '127.0.0.1'
PORT = 9191
BUFFER_SIZE = 1024

# Crear ventana principal
root = tk.Tk()
root.title("Cliente de chat")

chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15)
chat_box.config(state=tk.DISABLED)
chat_box.pack(pady=20)

entry_msg = tk.Entry(root, width=40)
entry_msg.pack(pady=20)

def send_message(event=None):
    msg = entry_msg.get()
    if msg:
        client.send(msg.encode())
        insert_message(f"Yo: {msg}", "right")

def insert_message(msg, alignment):
    chat_box.config(state=tk.NORMAL)
    if alignment == "right":
        chat_box.tag_configure("right", justify="right")
        chat_box.insert(tk.END, msg + "\n", "right")
    else:
        chat_box.tag_configure("left", justify="left")
        chat_box.insert(tk.END, msg + "\n", "left")
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)
    entry_msg.delete(0, tk.END)

def receive_messages():
    while True:
        try:
            msg = client.recv(BUFFER_SIZE).decode()
            # Handling file reception
            if msg.startswith('ARCHIVO:'):
                # Extract the file name and file size
                file_info = msg.split(':')[1:3]
                file_name = file_info[0]
                file_size = int(file_info[1])

                # Receive the file content and save it
                with open(file_name, 'wb') as f:
                    bytes_received = 0
                    while bytes_received < file_size:
                        bytes_to_receive = min(BUFFER_SIZE, file_size - bytes_received)
                        file_data = client.recv(bytes_to_receive)
                        f.write(file_data)
                        bytes_received += len(file_data)

                # Insert a message in the chat indicating the file has been received
                insert_message(f'Archivo {file_name} recibido y guardado.', 'left')
                
                # # Preparing to receive the file
                # chunks = []
                # bytes_received = 0
                # while bytes_received < file_size:
                #     chunk = client.recv(min(BUFFER_SIZE, file_size - bytes_received))
                #     chunks.append(chunk)
                #     bytes_received += len(chunk)
                # file_data = b''.join(chunks)
                # # Saving the received file
                # with open(f'recepcion_{file_name}', 'wb') as file:
                #     file.write(file_data)
                # print(f'[CLIENTE] Archivo {file_name} recibido.')
                
            if not msg.startswith("Yo:"):  # No mostrar mensajes propios recibidos del servidor
                insert_message(msg, "left")
        except:
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

name = simpledialog.askstring("Nombre", "Por favor ingresa tu nombre:", parent=root)
client.send(name.encode())
welcome_msg = client.recv(BUFFER_SIZE).decode()
# Manejar la respuesta del servidor si el nombre ya está en uso
while welcome_msg.startswith('[SERVER] Este nombre ya está en uso.'):
    name = simpledialog.askstring('Nombre en uso', 'El nombre ya está en uso. Por favor, elige otro.', parent=root)
    client.send(name.encode())
    welcome_msg = client.recv(BUFFER_SIZE).decode()
insert_message(welcome_msg, "left")

# Iniciar el hilo para recibir mensajes
threading.Thread(target=receive_messages, daemon=True).start()

entry_msg.bind("<Return>", send_message)
btn_send = tk.Button(root, text="Enviar", command=send_message)
btn_send.pack()

from tkinter.filedialog import askopenfilename

def send_file():
    file_path = askopenfilename()  # Open file dialog for user to select a file
    if file_path:
        with open(file_path, 'rb') as file:
            file_data = file.read()  # Read the file data
            file_name = os.path.basename(file_path)  # Get the file name
            file_size = os.path.getsize(file_path)  # Get the file size
            # Sending initial message with file details
            client.send(f'ARCHIVO:{file_name}:{file_size}'.encode())
            # Sending file data
            client.sendall(file_data)
            print(f'[CLIENTE] Archivo {file_name} enviado.')
        insert_message(f"Yo: {file_name}:{file_size}Bytes enviado.", "right")

# Add a button to the GUI for sending files
file_button = Button(root, text='Enviar Archivo', command=send_file)
file_button.pack(pady=20)

root.mainloop()
