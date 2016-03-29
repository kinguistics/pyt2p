import socket

HOST = 'localhost'
PORT = 50000

def request_pronunciation(word):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    s.sendall(word)
    data = s.recv(1024)
    
    s.close()
    return eval(data)