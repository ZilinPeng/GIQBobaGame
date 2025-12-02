import socket

HOST = "192.168.12.162"
PORT = 9000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

print("Connected!")

try:
    while True:
        data = s.recv(1024)
        if not data:
            break
        print("Received from server:", data.decode())
except:
    pass

print("Disconnected.")
s.close()