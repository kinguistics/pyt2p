import socket

import classifier.classify as pronun # come up with a better name

HOST = 'localhost'
PORT = 50000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

while True:
    s.listen(1)
    conn, addr = s.accept()
    
    while True:
        data = conn.recv(1024)
        if not data: break
        
        phones = pronun.classify(data)
        conn.sendall(repr(phones))
    
    conn.close()