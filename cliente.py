import socket
import threading
import tkinter as tk
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

root.mainloop()
