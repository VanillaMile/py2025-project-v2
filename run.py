from game import GameEngine, Player

if __name__ == "__main__":
    player1 = Player(100, 'Satori')
    player2 = Player(100, 'Koishi')

    game = GameEngine([player1, player2], start_card=7)
    game.play_round()