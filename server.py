import socket
from _thread import *
import pickle
import sys
from game import GameEngine
from game import Player

class Server:
    def __init__(self, host='127.0.0.1', port=55557):

        self.current_player = 1
        self.current_players = 1
        self.player_turn = 'Player1'

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind((host, port))
        except socket.error as e:
            print(str(e))
            sys.exit()

        s.listen()
        print(f"Server started on {host}:{port}")

        self.is_game_active = False
        self.game = None
        self.players = []
        self.game_state = {}

        while True:
            conn, addr = s.accept()
            print(f"Connected to {addr}")
            
            start_new_thread(self.threaded_client, (conn, addr, self.current_player))
            if self.current_player == 1:
                start_new_thread(self.start_game, ())
            self.current_player += 1
            self.current_players += 1

    def get_game_state(self, playerId=None):
        if self.game is not None:
            self.game_state = self.game.online_game_state(for_player=f'player{playerId}')
            try:
                self.game_state['title'] = 'game_state'
                self.game_state['current_player'] = self.player_turn
                self.game_state['destined_for'] = self.players[playerId-1].get_player_name()
            except Exception as e:
                print(f"Error broadcasting to {self.players[playerId-1].get_player_name()}: {e}")
        else:
            self.game_state = {
                'title': 'game_state',
                'error': "Game not started yet."
            }
        return self.game_state

    def start_game(self):
        while not self.is_game_active:
            continue
        print("Starting game...")
        
        for i in range(self.current_players-1):
            player = Player(1000, "Player" + str(i+1))
            self.players.append(player)
        
        self.game = GameEngine(self.players)
        self.is_game_active = True
        print("Game started with players:", self.players)
        self.game.play_round()

    def threaded_client(self, conn, addr, current_player):
        print(f"New connection from {addr}, player number: {current_player}")
        conn.send(str(current_player).encode("utf-8"))
        reply = "Welcome"
        while True:
            try:
                data = conn.recv(2048)
                decoded_data = data.decode("utf-8")

                print(f"is_game_active: {self.is_game_active}")
                
                if decoded_data.startswith('action_'):
                    action_data = decoded_data.split('_')
                    player_id = action_data[1]
                    action = action_data[2]
                    print(f"Received action from {addr}: {player_id} performed action '{action}'")
                    
                    self.game.selected_choice = str(action)

                if decoded_data.startswith('exchange_'):
                    exchange_data = decoded_data.split('_')
                    player_id = exchange_data[1]
                    exchange = exchange_data[2]
                    print(f"Received exchange from {addr}: {player_id} exchanged '{exchange}'")
                    
                    self.game.selected_choice = str(exchange)

                if decoded_data == "start_game":
                    print(f"Player {current_player} requested to start the game")
                    if self.current_players < 2:
                        reply = f"Not enough players to start the game. {self.current_players} player(s) connected. Which is {self.current_players < 2}"
                    else:
                        self.is_game_active = True
                        print("Game started successfully")

                if decoded_data.startswith('send_game_state_'):
                    print(f"Recived game state request from {addr}: {decoded_data}")
                    reply = self.get_game_state(int(decoded_data.split('_')[3]))

                if decoded_data == "is_game_active":
                    reply = str(self.is_game_active)

                if not data:
                    print(f"Connection closed by {addr}")
                    break
                else:
                    print(f"Received from {addr}: {reply}")

                if isinstance(reply, dict):
                    reply = pickle.dumps(reply)
                elif isinstance(reply, str):
                    reply = reply.encode("utf-8")
                conn.sendall(reply)
            except Exception as e:
                print(f"Error with {addr}: {e}")
                break
        
        print(f"Closing connection with {addr}")
        conn.close()

if __name__ == "__main__":
    server = Server()
    