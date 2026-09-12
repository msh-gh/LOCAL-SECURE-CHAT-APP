import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 5000

clients = []  # List of (conn, addr, public_key)

def handle_client(conn, addr):
    print(f"[+] New connection from {addr}")
    public_key = conn.recv(2048).decode('utf-8')
    clients.append((conn, addr, public_key))

    # Step 1: Send *existing* public keys to new client
    for c, a, pk in clients:
        if c != conn:
            try:
                conn.send(json.dumps({
                    'type': 'public_key',
                    'from': str(a),
                    'key': pk
                }).encode('utf-8'))
            except:
                pass

    # Step 2: Broadcast *new* public key to all other clients
    broadcast_key = json.dumps({
        'type': 'public_key',
        'from': str(addr),
        'key': public_key
    }).encode('utf-8')

    for c, a, pk in clients:
        if c != conn:
            try:
                c.send(broadcast_key)
            except:
                pass

    # Now handle incoming encrypted messages
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            for client, a, _ in clients:
                if client != conn:
                    try:
                        client.send(data)
                    except:
                        pass
        except:
            break

    print(f"[-] Disconnected: {addr}")
    conn.close()
    clients.remove((conn, addr, public_key))

def start_server():
    print("[*] Starting server...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[+] Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
    
