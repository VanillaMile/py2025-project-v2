import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 55557
        self.addr = (self.server, self.port)
        self.id = self.connect()

    def get_id(self):
        return self.id

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode("utf-8")
        except socket.error as e:
            print(f"Connection error: {e}")
            return None
    
    def send(self, data):
        try:
            self.client.send(data.encode("utf-8"))
            if data == 'start_game':
                # ignore this response for start_game
                return self.client.recv(2048)
            return self.client.recv(2048).decode("utf-8")
        except socket.error as e:
            print(f"Send error: {e}")
            return None
        
    def send_pickle(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(f"Send pickle error: {e}")
            return None
        
    def read_broadcast(self, playerId, start=None, send_action=None, exchange=None):
        try:
            if start is not None:
                self.client.send(f'start_game'.encode("utf-8"))
            elif send_action is not None:
                self.client.send(f'action_{playerId}_{send_action}'.encode("utf-8"))
            elif exchange is not None:
                self.client.send(f'exchange_{playerId}_{exchange}'.encode("utf-8"))
            else:
                self.client.send(f'send_game_state_{playerId}'.encode("utf-8"))
            data = self.client.recv(2048)
            if not data:
                return None
            return pickle.loads(data)
        except socket.error as e:
            print(f"Read broadcast error: {e}")
            return None
