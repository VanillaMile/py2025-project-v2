import random
from typing import List

class Player():

    def __init__(self, money, name="anonymous"):
        self.__stack_ = money
        self.__name_ = name
        self.__hand_ = []

    def take_card(self, card):
        self.__hand_.append(card)

    def get_stack_amount(self):
        return self.__stack_

    def change_card(self, card, idx):
        temp = self.__hand_[idx]
        self.__hand_[idx] = card
        return temp
    
    def put_back_card(self, idx):
        return self.__hand_.pop(idx)

    def get_player_hand(self):
        return tuple(self.__hand_)
    
    def clear_hand(self):
        self.__hand_ = []

    def cards_to_str(self):
        return_string = 'Player: ' + self.__name_ + '\n'
        return_string += 'Stack: ' + str(self.__stack_) + '\n'
        return_string += 'Hand: '
        for card in self.__hand_:
            return_string += str(card) + ' '
        return return_string + '\n'

class Card:
    # słownik symboli unicode
    unicode_dict = {'s': '\u2660', 'h': '\u2665', 'd': '\u2666', 'c': '\u2663', 'red': '\033[0;31m', 'black': '\033[0;30m', 'reset': '\033[0m'}
       
    def __init__(self, rank, suit):
        # kolor: s, h, d, c (spade, heart, diamond, club)
        # kolor: red, black (kolor karty)
        # ranga: 2-14 (2-10, J=11, Q=12, K=13, A=14)

        self.__rank_ = rank
        self.__suit_ = suit
        self.__color_ = 'red' if suit in ['h', 'd'] else 'black'
        
    def get_value(self):
        return (self.__rank_, self.__suit_)

    def __str__(self):
        if self.__rank_ > 10:
            rank_str = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}[self.__rank_]
        else:
            rank_str = str(self.__rank_)
        
        return_string = self.unicode_dict[self.__color_] + self.unicode_dict[self.__suit_] + str(rank_str) + self.unicode_dict['reset']
        return return_string

class Deck():
    
    def __init__(self, start_card = 2, shuffle=True):
        if start_card < 2 or start_card > 14:
            raise ValueError("start_card must be between 2 and 14")

        self.__deck_ = [Card(rank, suit) for rank in range(start_card, 15) for suit in ['s', 'h', 'd', 'c']]

        if shuffle:
            self.shuffle()
        pass
    def __str__(self):
        return_string = 'Deck:\n'
        for card in self.__deck_:
            return_string += str(card) + ' '
        return return_string + '\n'
    def shuffle(self):
        random.shuffle(self.__deck_)

    def deal(self, players):
        for i in range(5):
            for player in players:
                player.take_card(self.__deck_.pop(0))
    
    def reset_deck(self, shuffle=True):
        self.__deck_ = [Card(rank, suit) for rank in range(2, 15) for suit in ['s', 'h', 'd', 'c']]
        if shuffle:
            self.shuffle()
        

if __name__ == "__main__":
    deck = Deck(start_card=7)
    print(deck)

    player1 = Player(100, 'Player1')
    player2 = Player(100, 'Player2')

    deck.deal([player1, player2])
    print(player1.cards_to_str())
    print(player2.cards_to_str())

    print(deck)

