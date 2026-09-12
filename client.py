import socket
import threading
import json
from encryption import RSAEncryption
import tkinter as tk
from tkinter import messagebox, simpledialog

rsa = RSAEncryption()
public_keys = {}
client = None
connected = False

# === GUI Setup ===
window = tk.Tk()
window.title("Secure Chat (End-to-End Encrypted)")
window.geometry("700x580")
window.configure(bg="#F0F2F5")

# === Fonts & Colors ===
FONT = ("Segoe UI", 11)
BG_COLOR = "#F0F2F5"
SEND_COLOR = "#DCF8C6"
RECEIVE_COLOR = "#E8E8E8"
ENTRY_BG = "#FFFFFF"
BTN_COLOR = "#0078D7"
TEXT_COLOR = "#000000"

# === Chat Canvas with Scrollable Frame ===
chat_canvas = tk.Canvas(window, bg=BG_COLOR, bd=0, highlightthickness=0)
chat_frame = tk.Frame(chat_canvas, bg=BG_COLOR)
scrollbar = tk.Scrollbar(window, orient="vertical", command=chat_canvas.yview)
chat_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
chat_canvas.pack(side="top", fill="both", expand=True)
chat_canvas.create_window((0, 0), window=chat_frame, anchor="nw")

def on_frame_configure(event):
    chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))

chat_frame.bind("<Configure>", on_frame_configure)

# === Display Message ===
def display_message(msg, sender="You"):
    bubble_color = SEND_COLOR if sender == "You" else RECEIVE_COLOR
    anchor_side = "e" if sender == "You" else "w"

    msg_label = tk.Label(chat_frame,
                         text=msg,
                         bg=bubble_color,
                         fg=TEXT_COLOR,
                         font=FONT,
                         wraplength=500,
                         justify="left",
                         padx=10, pady=6,
                         bd=0,
                         relief="flat")
    msg_label.pack(anchor=anchor_side, pady=4, padx=12, ipadx=6, ipady=2)
    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1.0)

# === Receive Thread ===
def receive_messages():
    global connected
    while connected:
        try:
            data = client.recv(4096)
            if not data:
                break

            try:
                message = json.loads(data.decode('utf-8'))
                if message['type'] == 'public_key':
                    sender = message['from']
                    key = message['key'].encode('utf-8')
                    public_keys[sender] = key
                    display_message(f"[Public key received from {sender}]", "System")
            except:
                try:
                    decrypted = rsa.decrypt_message(data.decode('utf-8'))
                    display_message(decrypted, sender="Friend")
                except:
                    display_message("[Error decrypting message]", "System")
        except Exception as e:
            display_message(f"[!] Connection Error: {e}", "System")
            break

# === Connect to Server ===
def connect_to_server(host, port):
    global client, connected
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        client.send(rsa.get_public_key())
        connected = True
        display_message(f"[Connected to {host}:{port}]", "System")
        threading.Thread(target=receive_messages, daemon=True).start()
    except Exception as e:
        connected = False
        messagebox.showerror("Connection Failed", f"Could not connect: {e}")

# === Settings Dialog ===
def open_settings():
    host = simpledialog.askstring("Server IP", "Enter Server IP:", initialvalue="127.0.0.1")
    port = simpledialog.askinteger("Port", "Enter Port:", initialvalue=5000)
    if host and port:
        connect_to_server(host, port)

# === Send Message ===
def send_message():
    msg = msg_entry.get().strip()
    if msg == "":
        return
    if not connected or not public_keys:
        display_message("[!] No recipients available. Click ⚙ to connect.", "System")
        return

    recipient_key = list(public_keys.values())[0]
    encrypted = rsa.encrypt_message(msg, recipient_key)
    client.send(encrypted.encode('utf-8'))
    display_message(msg, sender="You")
    msg_entry.delete(0, tk.END)

# === Top Settings Frame ===
settings_frame = tk.Frame(window, bg=BG_COLOR)
settings_frame.pack(fill="x", pady=(6, 0), padx=10)

settings_btn = tk.Button(settings_frame,
                         text="⚙ Settings",
                         font=("Segoe UI", 10),
                         bg=BTN_COLOR,
                         fg="white",
                         relief="flat",
                         command=open_settings)
settings_btn.pack(side="right")

# === Bottom Entry Frame ===
entry_frame = tk.Frame(window, bg=BG_COLOR)
entry_frame.pack(side="bottom", fill="x", pady=10, padx=10)

msg_entry = tk.Entry(entry_frame,
                     font=FONT,
                     bg=ENTRY_BG,
                     fg=TEXT_COLOR,
                     insertbackground=TEXT_COLOR,
                     relief="solid",
                     bd=1)
msg_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))

send_btn = tk.Button(entry_frame,
                     text="Send",
                     font=("Segoe UI", 11, "bold"),
                     bg=BTN_COLOR,
                     fg="white",
                     activebackground="#005BA1",
                     relief="flat",
                     command=send_message,
                     padx=20, pady=8)
send_btn.pack(side="right")

window.mainloop()
