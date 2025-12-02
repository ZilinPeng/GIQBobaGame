import socket
import threading
import tkinter as tk

HOST = "0.0.0.0"
PORT = 9000

conn = None
status = None


def start_server():
    global conn

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)



    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)


def handle_client(c, addr):
    global conn
    print(f"[SERVER] Client connected: {addr}")

    try:
        while True:
            data = c.recv(1024)
            if not data:
                break
            print("[CLIENT]", data.decode())
    except:
        pass

    print("[SERVER] Client disconnected")
    conn = None


def send_number(num):
    global conn

    if conn:
        conn.sendall(str(num).encode())
        print(f"[SERVER] Sent: {num}")
    else:
        print("[SERVER] No client connected")


def build_gui():
    global status

    root = tk.Tk()
    root.title("Socket Server")

    status = tk.StringVar(value="Starting server...")

    tk.Label(root, textvariable=status).pack(pady=10)
    tk.Label(root, text='''
                choose your event:
                1. no sugar
                2. no milk
                3. yes boba
                            ''').pack(pady=10)
    
    # Buttons sending fixed numbers
    tk.Button(root, text="Send 1", width=20, command=lambda: send_number(1)).pack(pady=5)
    tk.Button(root, text="Send 2", width=20, command=lambda: send_number(2)).pack(pady=5)
    tk.Button(root, text="Send 3", width=20, command=lambda: send_number(3)).pack(pady=5)

    root.mainloop()


# Start server thread
threading.Thread(target=start_server, daemon=True).start()

# Start GUI
build_gui()