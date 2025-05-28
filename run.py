from game import GameEngine, Player
import pickle

if __name__ == "__main__":
    _input = input("Load a game? (y/n)[n]: ")
    if _input.lower() == 'y':
        game = pickle.load(open('game_save.pkl', 'rb'))
    else:
        player1 = Player(1000, 'Satori')
        player2 = Player(1000, 'Koishi')

        game = GameEngine([player1, player2], start_card=7)

    
    game.play_round()

    _input = input("Save the game? (y/n)[n]: ")
    if _input.lower() == 'y':
        with open('game_save.pkl', 'wb') as f:
            pickle.dump(game, f)
    else:
        print("Game not saved.")