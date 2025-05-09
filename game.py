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
        return self.__hand_
    
    def print_hand(self):
        return_string = ''
        for card in self.__hand_:
            return_string += str(card) + ' '
        return return_string
    
    def clear_hand(self):
        self.__hand_ = []
    
    def get_player_name(self):
        return self.__name_

    def cards_to_str(self):
        return_string = 'Player: ' + self.__name_ + '\n'
        return_string += 'Stack: ' + str(self.__stack_) + '\n'
        return_string += 'Hand: '
        for card in self.__hand_:
            return_string += str(card) + ' '
        return return_string + '\n'
    
    def take_money(self, amount):
        if amount > self.__stack_:
            raise ValueError("Nie masz wystarczająco pieniędzy")
        self.__stack_ -= amount

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
        
    def get_value(self) -> tuple:
        """Zwraca krotkę z wartością karty (ranga, kolor)"""
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
        return return_string
    
    def shuffle(self):
        random.shuffle(self.__deck_)

    def deal(self, players):
        try:
            for i in range(5):
                for player in players:
                    player.take_card(self.__deck_.pop(0))
        except IndexError:
            raise ValueError("Nie ma wystarczająco kart w talii")
        
    
    def reset_deck(self, shuffle=True):
        self.__deck_ = [Card(rank, suit) for rank in range(2, 15) for suit in ['s', 'h', 'd', 'c']]
        if shuffle:
            self.shuffle()

    def collect_cards(self, cards):
        """Zbiera karty z ręki gracza i wkłada je na spód talii."""
        for card in cards:
            self.__deck_.append(card)

    def fill_hands(self, players):
        for player in players:
            for i in range(5 - len(player.get_player_hand())):
                player.take_card(self.__deck_.pop(0))

class GameEngine:
    def __init__(self, players: List[Player], deck: Deck,
                small_blind: int = 25, big_blind: int = 50):
        """Inicjalizuje graczy, talię, blindy i pulę."""
        self.__players_ = players
        self.__big_blind = big_blind
        self.__small_blind = small_blind
        self.__deck_ = deck
        self.__current_big_blind = self.__players_[0]
        self.__current_small_blind = self.__players_[1]
        self.__pot = 0
        self.__current_bet = 0
        self.__current_player = 0
        self.__players_states = dict()
        for player in self.__players_:
            self.__players_states[player] = {
                'bet': 0,
                'folded': False,
                'all_in': False
            }
        self.__raise_amount = 10
    
    def play_round(self) -> None:
        """Przeprowadza jedną rundę:
        1. Pobiera blindy
        2. Rozdaje karty
        3. Rundę zakładów
        4. Wymianę kart
        5. Showdown i przyznanie puli
        """
        self.__deck_.reset_deck(shuffle=True)
        self.__deck_.deal(self.__players_)

        for player in self.__players_:
            self.__players_states[player]['bet'] = 0
            self.__players_states[player]['folded'] = False
            self.__players_states[player]['all_in'] = False
            player.clear_hand()
        
        # Pobieranie blindów
        if self.__current_big_blind.get_stack_amount() < self.__big_blind:
            raise ValueError("Gracz nie ma wystarczająco pieniędzy na big blind")
        self.__pot += self.__big_blind
        self.__current_big_blind.take_money(self.__big_blind)

        if self.__current_small_blind.get_stack_amount() < self.__small_blind:
            raise ValueError("Gracz nie ma wystarczająco pieniędzy na small blind")
        self.__pot += self.__small_blind
        self.__current_small_blind.take_money(self.__small_blind)

        # Rozdanie kart
        deck.deal(self.__players_)

        while True:
            #TODO: Dodaj kończenie gry przez fold
            state = 'check'
            for player in self.__players_:
                if self.__players_states[player]['folded']:
                    continue
                if self.__players_states[player]['all_in']:
                    continue
                action, bet = self.prompt_bet(player, self.__current_bet)
                if action != 'check':
                    state = action
            if state == 'check':
                break

        # Wymiana kart
        self.exchange_cards()

        # Showdown
        winner = self.showdown()
        print(f"Wygrał {winner.get_player_name()} z {winner.print_hand()}")
        #TODO: Dodaj dzielenie nagrody w przypadku remisu

    def get_indecies(self, player: Player, redemption_chances: int = 3) -> List[int]:
        """Zwraca listę indeksów kart do wymiany."""
        indecies = []
        print(player.cards_to_str())
        print('Wybierz karty do wymiany (1-5) lub 9 aby zachować wszystkie np.(1 2 4):')
        input_ = input()
        for i in input_.split():
            try:
                if int(i) < 1 or int(i) > 5:
                    raise ValueError()
                indecies.append(int(i) - 1)
            except ValueError:
                print(f"Niepoprawny indeks: {i}")
                if redemption_chances == 0:
                    print("Podano zbyt wiele błędów. Wymiana kart zakończona. Wszystkie karty zostaną zachowane.")
                    return self.get_indecies(player, redemption_chances=redemption_chances - 1)
                return self.get_indecies(player, redemption_chances=redemption_chances - 1)
        return indecies
    
    def prompt_bet(self, player: Player, current_bet: int) -> tuple:
        """Pobiera akcję od gracza (human lub bot) — check/call/raise/fold."""
        print(player.cards_to_str())
        if self.__players_states[player]['bet'] < current_bet:
            print(f"{player.__name_} musi sprawdzić {current_bet - self.__players_states[player]['bet']}")
            print('Wybierz akcję:')
            print('1. Fold')
            print('2. All in')
        if current_bet - self.__players_states[player]["bet"] > player.get_stack_amount():
            print('3. Call all in')
        else:
            print(f'3. Call {current_bet - self.__players_states[player]["bet"]}')
        print(f'4. Raise {current_bet - self.__players_states[player]["bet"] + self.__raise_amount}')
        print(f'5. Raise {current_bet - self.__players_states[player]["bet"] + self.__raise_amount * 2}')
        print(f'6. Raise {current_bet - self.__players_states[player]["bet"] + self.__raise_amount * 3}')
        print('7. Check')

        input_ = input('Wybierz akcję: ')
        return_string = ''
        if input_ == '1':
            return_string = 'fold'
            self.__players_states[player]['folded'] = True
        elif input_ == '2':
            return_string = 'all_in'
            self.__players_states[player]['all_in'] = True
        elif input_ == '3':
            return_string = 'call'
            self.__players_states[player]['bet'] += current_bet - self.__players_states[player]['bet']
        elif input_ == '4':
            return_string = 'raise'
            self.__players_states[player]['bet'] += current_bet - self.__players_states[player]['bet'] + self.__raise_amount
        elif input_ == '5':
            return_string = 'raise'
            self.__players_states[player]['bet'] += current_bet - self.__players_states[player]['bet'] + self.__raise_amount * 2
        elif input_ == '6':
            return_string = 'raise'
            self.__players_states[player]['bet'] += current_bet - self.__players_states[player]['bet'] + self.__raise_amount * 3
        elif input_ == '7':
            return_string = 'check'

        return return_string, self.__players_states[player]['bet']
    
    def exchange_cards(self):
        """Wymienia wskazane karty z ręki gracza, wkłada stare na spód talii."""
        for player in self.__players_:
            if self.__players_states[player]['folded']:
                continue
            indecies = self.get_indecies(player)
            if indecies[0] == 9:
                continue
            cards = []
            for i in indecies:
                cards.append(player.get_player_hand()[i])

            remaining_cards = []
            for i in range(5):
                if i not in indecies:
                    remaining_cards.append(player.get_player_hand()[i])
            
            player.clear_hand()
            player.__hand_ = remaining_cards

            self.__deck_.collect_cards(cards)

        self.__deck_.fill_hands(self.__players_)
    
    def showdown(self) -> Player:
        """Porównuje układy pozostałych graczy i zwraca zwycięzcę."""
        for player in self.__players_:
            print(player.cards_to_str())
        best_hand = 0
        winner = self.__players_[0]
        for player in self.__players_:
            if self.__players_states[player]['folded']:
                continue
            hand_strength = self.calculate_hand_strength(player)
            if hand_strength > best_hand:
                best_hand = hand_strength
                winner = player
        return winner

    def calculate_hand_strength(self, player: Player) -> int:
        """Oblicza siłę układu gracza."""
        hand = player.get_player_hand()
        hand.sort(key=lambda x: x.get_value()[0], reverse=True)
        hand_strength = 0
        # 1 Royal Flush
        if self.is_royal_flush(hand):
            hand_strength = 100
        # 2 Straight Flush
        if self.is_straight_flush(hand):
            hand_strength = 90

        #TODO: Dodaj inne układy pokerowe i ich siłę

        return hand_strength
    
    def is_royal_flush(self, hand: List[Card]) -> bool:
        """Sprawdza, czy układ to Royal Flush."""
        suit = hand[0].get_value()[1]
        for card in hand:
            if card.get_value()[1] != suit:
                return False
        if hand[0].get_value()[0] == 14 and hand[1].get_value()[0] == 13 and hand[2].get_value()[0] == 12 and hand[3].get_value()[0] == 11 and hand[4].get_value()[0] == 10:
            return True
        return False
    
    def is_straight_flush(self, hand: List[Card]) -> bool:
        """Sprawdza, czy układ to Straight Flush."""
        suit = hand[0].get_value()[1]
        for card in hand:
            if card.get_value()[1] != suit:
                return False
        current_card_value = hand[0].get_value()[0]
        for card in hand[1:]:
            if card.get_value()[0] != current_card_value - 1:
                if card.get_value()[0] == 14 and current_card_value == 2:
                    # as w ręce i 2 poprzednia
                    continue
                else:
                    return False
            current_card_value -= 1
        return True

if __name__ == "__main__":
    deck = Deck(start_card=7)
    print(deck)

    player1 = Player(100, 'Player1')
    player2 = Player(100, 'Player2')

    deck.deal([player1, player2])
    print(player1.cards_to_str())
    print(player2.cards_to_str())

    print(deck)

    game = GameEngine([player1, player2], deck)
    game.play_round()

