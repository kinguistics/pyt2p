import socket
import pickle
import re

import classifier.classify as pronun # come up with a better name

HOST = ''
PORT = 48999

CMUDICT = None
CMUDICT_FNAME = 'cmudict.pickle'

def initialize_cmudict():
    global CMUDICT
    
    with open(CMUDICT_FNAME) as f:
        CMUDICT = pickle.load(f)


if __name__ == "__main__":
    hostname = socket.gethostname(); print hostname
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    
    initialize_cmudict()
    # classify something just to force the classifier to initialize
    phones = pronun.classify('a')
    print phones
    
    while True:
        s.listen(1)
        conn, addr = s.accept()
        
        while True:
            data = conn.recv(1024)
            if not data: break
            print data
            
            if data in CMUDICT:
                phones = CMUDICT[data][0]
                phones = [re.sub('\d','',p) for p in phones]
            
            else:
                try:
                    phones = pronun.classify(data)
                except:
                    # this sometimes breaks for no reason; don't let it crash the entire server
                    phones = []
                
            conn.sendall(repr(phones))
        
        conn.close()
