import random
from typing import List
import pandas as pd

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

    def cards_to_str(self, with_name: bool = False) -> str:
        return_string = ''
        if with_name:
            return_string = 'Player: ' + self.__name_ + '\n'
        return_string += 'Money: ' + str(self.__stack_) + '\n'
        return_string += 'Hand: '
        for card in self.__hand_:
            return_string += str(card) + ' '
        return return_string + '\n'
    
    def take_money(self, amount):
        if amount > self.__stack_:
            raise ValueError("Not enough funds")
        self.__stack_ -= amount

    def add_money(self, amount):
        if amount < 0:
            raise ValueError("Cannot add negative amount")
        self.__stack_ += amount

class Card:
    unicode_dict = {'s': '\u2660', 'h': '\u2665', 'd': '\u2666', 'c': '\u2663', 'red': '\033[0;31m', 'black': '\033[0;30m', 'reset': '\033[0m'}
       
    def __init__(self, rank, suit):
        # color: s, h, d, c (spade, heart, diamond, club)
        # color: red, black (card color)
        # rang: 2-14 (2-10, J=11, Q=12, K=13, A=14)

        self.__rank_ = rank
        self.__suit_ = suit
        self.__color_ = 'red' if suit in ['h', 'd'] else 'black'
        
    def get_value(self) -> tuple:
        """returns rank and suit of the card"""
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
        self.__start_card_ = start_card

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
            raise ValueError("not enough cards in the deck")
        
    
    def reset_deck(self, shuffle=True):
        self.__deck_ = [Card(rank, suit) for rank in range(self.__start_card_, 15) for suit in ['s', 'h', 'd', 'c']]
        if shuffle:
            self.shuffle()

    def collect_cards(self, cards):
        """Takes cards from player and puts them back to the deck."""
        for card in cards:
            self.__deck_.append(card)

    def fill_hands(self, players):
        for player in players:
            for i in range(5 - len(player.get_player_hand())):
                player.take_card(self.__deck_.pop(0))

class GameEngine:
    def __init__(self, players: List[Player], deck: Deck = None,
                small_blind: int = 25, big_blind: int = 50, raise_amount: int = 10, start_card: int = 2):
        if deck is None:
            self.__deck_ = Deck(start_card=start_card)
        else:
            self.__deck_ = deck
        self.__players_ = players
        self.__big_blind = big_blind
        self.__small_blind = small_blind
        self.__current_big_blind = self.__players_[0]
        self.__current_small_blind = self.__players_[1]
        self.__pot = 0
        self.__current_bet = 0
        self.__players_states = dict()
        self.__red = '\033[0;31m'
        self.__purple = '\033[0;35m'
        self.__clear = '\033[0m'
        self.__blue = '\033[0;34m'
        self.history = []
        self.round_history = []
        for player in self.__players_:
            self.__players_states[player] = {
                'bet': 0,
                'folded': False,
                'all_in': False,
                'checked': False
            }
        self.__raise_amount = raise_amount

    def save_game_logs(self):
        """Saves game logs to file."""
        date_now_str = pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')
        with open(f'game_logs_{date_now_str}.csv', 'w') as f:
            for i in range(len(self.history)):
                for action in self.history[i]:
                    action = action.replace(f'{self.__blue}', '')
                    action = action.replace(f'{self.__red}', '')
                    action = action.replace(f'{self.__purple}', '')
                    action = action.replace(f'{self.__clear}', '')
                    action = action.replace('\033[0;30m', '')
                    action = action.replace(',', '')

                    f.write(f'{i},{action}\n')
        print(f'Game logs saved to game_logs_{date_now_str}.csv')
        f.close()
        

    def play_round(self) -> None:
        """
        Handles the game round.
        1. Collects blinds
        2. Deals cards
        3. Betting round
        4. Card exchange
        5. Showdown
        """
        self.__deck_.reset_deck(shuffle=True)
        self.round_history = []
        self.__pot = 0
        self.__current_bet = 0

        for player in self.__players_:
            self.__players_states[player]['bet'] = 0
            self.__players_states[player]['folded'] = False
            self.__players_states[player]['all_in'] = False
            self.__players_states[player]['checked'] = False
            player.clear_hand()
        
        # Collecting blinds
        if self.__current_big_blind.get_stack_amount() < self.__big_blind:
            raise ValueError("Not enough funds for big blind")
        self.__pot += self.__big_blind
        self.__current_big_blind.take_money(self.__big_blind)
        self.__players_states[self.__current_big_blind]['bet'] = self.__big_blind


        if self.__current_small_blind.get_stack_amount() < self.__small_blind:
            raise ValueError("Not enough funds for small blind")
        self.__pot += self.__small_blind
        self.__current_small_blind.take_money(self.__small_blind)
        self.__players_states[self.__current_small_blind]['bet'] = self.__small_blind

        self.__current_bet = self.__big_blind

        self.print_table_info()

        # Dealing cards
        self.__deck_.deal(self.__players_)
        for player in self.__players_:
            self._sort_cards(player)

        active = 0
        while True:
            state = 'check'
            active = 0
            for player in self.__players_:
                if self.__players_states[player]['folded']:
                    continue
                active += 1

            if active == 1:
                # Covers fold
                break

            for player in self.__players_:
                if self.__players_states[player]['folded']:
                    continue
                if self.__players_states[player]['all_in']:
                    continue
                if self.__players_states[player]['checked'] and self.__players_states[player]['bet'] == self.__current_bet:
                    continue
                else:
                    self.__players_states[player]['checked'] = False

                player_action = self.prompt_bet(player)
                action = self._apply_bet(player, player_action)

                if action == 'fold':
                    self.__players_states[player]['folded'] = True
                elif action == 'all_in':
                    self.__players_states[player]['all_in'] = True
                    
                if action != 'check':
                    state = action
            if state == 'check':
                break

        # Exchange cards
        if active != 1:
            self.exchange_cards()

        # Showdown
        self.clear_view()
        self.print_table_info()
        winner = self._showdown()
        hand_name, _ = self._calculate_hand_strength(winner.get_player_hand())
        text = f"{self.__purple}{winner.get_player_name()}{self.__clear} wins with {winner.print_hand()} ({hand_name}) bet = {self.__players_states[winner]['bet']}. Pot: {self.__pot}"
        print(text)
        winner.add_money(self.__pot)
        self.round_history.append(text)
        print(f'Other players:')
        for player in self.__players_:
            if player == winner:
                continue
            hand_name, _ = self._calculate_hand_strength(player.get_player_hand())
            if self.__players_states[player]["folded"]:
                folded = 'folded'
            else:
                folded = ''
            print(f'{player.get_player_name()} with {player.print_hand()} ({hand_name}) bet = {self.__players_states[player]["bet"]}, {folded}')
        #TODO: Devide pot in case of draw

        self.history.append(self.round_history)

        print('Play next round? (y/n) [n]')
        input_ = input()
        if input_.lower() == 'y':
            self.play_round()
        else:
            self.save_game_logs()
            print('Game ended')
            return

    def clear_view(self):
        """Clears view."""
        for i in range(100):
            print()

    def print_table_info(self, confidential: bool = False):
        print(f'Pot: {self.__purple}{self.__pot}{self.__clear}')
        print(f'Current bet: {self.__purple}{self.__current_bet}{self.__clear}')

        if len(self.round_history) > 0:
            print(f'{self.__blue}Round history:{self.__clear}')
            for action in self.round_history:
                if 'CONFIDENTIAL' in action and not confidential:
                    continue
                print(f'{self.__blue}{action}{self.__clear}')
    
    def prompt_bet(self, player: Player, wrong_choice: bool = False) -> tuple:
        """Gets player action call/raise/check/all_in."""
        self.clear_view()
        self.print_table_info()
        if wrong_choice:
            print(f"{self.__red}Wrong choice. Choose again.{self.__clear}")
        allowed_choices = []
        print(f'Player: {self.__purple}{player.get_player_name()}{self.__clear}')
        print(player.cards_to_str())
        if self.__players_states[player]['bet'] == self.__current_bet:
            print('You can check or raise')
            if player.get_stack_amount() >= self.__raise_amount:
                print(f'4. Raise to {self.__current_bet + self.__raise_amount}')
                allowed_choices.append('4')
            print('7. Check')
            allowed_choices.append('7')
        else:
            if self.__players_states[player]['bet'] < self.__current_bet:
                print(f"{self.__red}{player.get_player_name()} must call {self.__current_bet - self.__players_states[player]['bet']}{self.__clear}")
                print('Choose action:')
                print('1. Fold')
                print('2. All in')
                allowed_choices.append('1')
                allowed_choices.append('2')
            if self.__current_bet - self.__players_states[player]["bet"] > player.get_stack_amount():
                print('3. Call all in')
                allowed_choices.append('3')
            else:
                if self.__current_bet - self.__players_states[player]["bet"] > 0:
                    print(f'3. Call {self.__current_bet - self.__players_states[player]["bet"]}')
                    allowed_choices.append('3')
            if player.get_stack_amount() > self.__raise_amount:
                print(f'4. Raise to {self.__current_bet + self.__raise_amount}')
                allowed_choices.append('4')
            if not self.__players_states[player]['bet'] < self.__current_bet:
                print('7. Check')
                allowed_choices.append('7')
            print('9. Go all in')
            allowed_choices.append('9')

        
        input_ = input('Choose action: ')
        if input_ not in allowed_choices:
            return self.prompt_bet(player, wrong_choice=True)
        return input_

    def _apply_bet(self, player: Player, input_: str = '') -> str:
        added = 0
        return_string = ''
        if input_ == '1':
            return_string = 'fold'
            self.__players_states[player]['folded'] = True
            self.round_history.append(f'{player.get_player_name()} folded, bet = {self.__players_states[player]["bet"]}, pot = {self.__pot}')

        elif input_ == '3':
            return_string = 'call'
            added = self.__current_bet - self.__players_states[player]['bet']
            self.__players_states[player]['bet'] += added
            self.__players_states[player]['checked'] = True
            self.round_history.append(f'{player.get_player_name()} called {added}, bet = {self.__players_states[player]["bet"]}, pot = {self.__pot}')
            
        elif input_ == '4':
            return_string = 'raise'
            added = self.__current_bet - self.__players_states[player]['bet'] + self.__raise_amount
            self.__players_states[player]['bet'] += added
            self.__current_bet = self.__players_states[player]['bet']
            self.round_history.append(f'{player.get_player_name()} raised {added}, bet = {self.__players_states[player]["bet"]}, pot = {self.__pot}')
        elif input_ == '9' or input_ == '2':
            return_string = 'all_in'
            self.__players_states[player]['all_in'] = True
            self.__players_states[player]['bet'] = self.__players_states[player]['bet'] + player.get_stack_amount()
            if self.__players_states[player]['bet'] > self.__current_bet:
                self.__pot += self.__players_states[player]['bet'] - self.__current_bet
                self.__current_bet = self.__players_states[player]['bet']
            else:
                self.__pot += player.get_stack_amount()
            player.take_money(player.get_stack_amount())
            self.round_history.append(f'{player.get_player_name()} went all in {self.__players_states[player]["bet"]}, bet = {self.__players_states[player]["bet"]}, pot = {self.__pot}')

        elif input_ == '7':
            return_string = 'check'
            self.__players_states[player]['checked'] = True
            self.round_history.append(f'{player.get_player_name()} checked, bet = {self.__players_states[player]["bet"]}, pot = {self.__pot}')
        
        player.take_money(added)
        self.__pot += added

        return return_string
    
    def _sort_cards(self, player: Player) -> None:
        """Sorts player cards."""
        player.get_player_hand().sort(key=lambda x: x.get_value()[0], reverse=True)
    
    def get_indecies(self, player: Player, redemption_chances: int = 3) -> List[int]:
        """Returns list of cards to exchange."""
        indecies = []
        self.clear_view()
        print(f'Action of {self.__purple}{player.get_player_name()}{self.__clear}')
        print(player.cards_to_str())
        print('Select cards to exchange (1-5) or nothing to skip(like: 1 2 4):')
        input_ = input()
        for i in input_.split():
            try:
                if int(i) < 1 or int(i) > 5:
                    raise ValueError()
                indecies.append(int(i) - 1)
            except ValueError:
                print(f"Wrong index: {i}")
                if redemption_chances == 0:
                    print("Too many errors. No cards exchanged.")
                    return []
                return self.get_indecies(player, redemption_chances=redemption_chances - 1)
        return indecies
    
    def exchange_cards(self):
        """Exchange cards, puts exchanged cards into deck."""
        for player in self.__players_:
            if self.__players_states[player]['folded']:
                continue
            indecies = self.get_indecies(player)
            if len(indecies) == 0:
                continue
            if indecies[0] == 9:
                continue
            cards = []
            for i in indecies:
                cards.append(player.get_player_hand()[i])
            cards_put_back_str = ''
            for card in cards:
                cards_put_back_str += str(card) + ' '

            kept_cards = []
            for i in range(5):
                if i not in indecies:
                    kept_cards.append(player.get_player_hand()[i])
            
            previous_cards = ''
            for card in player.get_player_hand():
                previous_cards += str(card) + ' '

            player.clear_hand()
            for card in kept_cards:
                player.take_card(card)

            self.__deck_.collect_cards(cards)

            self.__deck_.fill_hands([player])
            current_cards = ''
            for card in player.get_player_hand():
                current_cards += str(card) + ' '
            self.round_history.append(f'CONFIDENTIAL: {player.get_player_name()} exchanged from hand {previous_cards}: {cards_put_back_str}for {current_cards}')
            self._sort_cards(player)
    
    def _showdown(self) -> Player:
        """Compare hands and find winner."""
        best_hand = 0
        winner = self.__players_[0]
        for player in self.__players_:
            if self.__players_states[player]['folded']:
                continue
            _, hand_strength = self._calculate_hand_strength(player.get_player_hand())
            if hand_strength > best_hand:
                best_hand = hand_strength
                winner = player
        return winner

    def _calculate_hand_strength(self, hand: list = []) -> tuple:
        """Calculates hand strenght."""
        hand = hand
        hand.sort(key=lambda x: x.get_value()[0], reverse=True)
        hand_strength = 0
        # 1 Royal Flush
        if self._is_royal_flush(hand):
            hand_strength = 100
            name = 'Royal Flush'
        # 2 Straight Flush
        elif self._is_straight_flush(hand):
            hand_strength = 90
            name = 'Straight Flush'
        # 3 Four of a Kind
        elif self._is_four_of_a_kind(hand):
            hand_strength = 80
            name = 'Four of a Kind'
        # 4 Full House
        elif self._is_full_house(hand):
            hand_strength = 70
            name = 'Full House'
        # 5 Flush
        elif self._is_flush(hand):
            hand_strength = 60
            name = 'Flush'
        # 6 Straight
        elif self._is_straight(hand):
            hand_strength = 50
            name = 'Straight'
        # 7 Three of a Kind
        elif self._is_three_of_a_kind(hand):
            hand_strength = 40
            name = 'Three of a Kind'
        # 8 Two Pair
        elif self._is_two_pair(hand):
            hand_strength = 30
            name = 'Two Pair'
        # 9 Pair
        elif self._is_pair(hand):
            hand_strength = 20
            name = 'Pair'
        # 10 High Card
        if hand_strength == 0:
            hand_strength = self._is_high_card(hand)
            name = 'High Card'

        return name, hand_strength
    
    def _is_royal_flush(self, hand: List[Card]) -> bool:
        suit = hand[0].get_value()[1]
        for card in hand:
            if card.get_value()[1] != suit:
                return False
        if hand[0].get_value()[0] == 14 and hand[1].get_value()[0] == 13 and hand[2].get_value()[0] == 12 and hand[3].get_value()[0] == 11 and hand[4].get_value()[0] == 10:
            return True
        return False
    
    def _is_straight_flush(self, hand: List[Card]) -> bool:
        suit = hand[0].get_value()[1]
        for card in hand:
            if card.get_value()[1] != suit:
                return False
        return self._is_straight(hand)
    
    def _is_four_of_a_kind(self, hand: List[Card]) -> bool:
        ranks = [card.get_value()[0] for card in hand]
        for rank in ranks:
            if ranks.count(rank) == 4:
                return True
        return False
    
    def _is_full_house(self, hand: List[Card]) -> bool:
        ranks = [card.get_value()[0] for card in hand]
        for rank in ranks:
            if ranks.count(rank) == 3:
                for rank2 in ranks:
                    if rank2 != rank and ranks.count(rank2) == 2:
                        return True
        return False
    
    def _is_flush(self, hand: List[Card]) -> bool:
        suit = hand[0].get_value()[1]
        for card in hand:
            if card.get_value()[1] != suit:
                return False
        return True
    
    def _is_straight(self, hand: List[Card]) -> bool:
        current_card_value = hand[0].get_value()[0]
        if current_card_value == 14 and hand[1].get_value()[0] != 13:
            # ace in hand
            current_card_value = hand[1].get_value()[0]
            hand_zero = hand[0].get_value()
            hand.remove(hand[0])
            hand.append(Card(14, hand_zero[1]))
        for card in hand[1:]:
            if card.get_value()[0] == (current_card_value - 1):
                current_card_value -= 1
            else:
                if card.get_value()[0] == 14 and current_card_value == 2:
                    # ace in hand and 2 in hand
                    continue
                return False
        return True
    
    def _is_three_of_a_kind(self, hand: List[Card]) -> bool:
        ranks = [card.get_value()[0] for card in hand]
        for rank in ranks:
            if ranks.count(rank) == 3:
                return True
        return False
    
    def _is_two_pair(self, hand: List[Card]) -> bool:
        ranks = [card.get_value()[0] for card in hand]
        pairs = 0
        for rank in ranks:
            if ranks.count(rank) == 2:
                pairs += 1
                ranks.remove(rank)
        if pairs == 2:
            return True
        return False
    
    def _is_pair(self, hand: List[Card]) -> bool:
        ranks = [card.get_value()[0] for card in hand]
        for rank in ranks:
            if ranks.count(rank) == 2:
                return True
        return False
    
    def _is_high_card(self, hand: List[Card]) -> int:
        ranks = [card.get_value()[0] for card in hand]
        ranks.sort(reverse=True)
        return ranks[0]

if __name__ == "__main__":
    game = GameEngine([Player(100, 'Satori'), Player(100, 'Koishi')], start_card=7)

    royal_flush = [Card(14, 's'), Card(13, 's'), Card(12, 's'), Card(11, 's'), Card(10, 's')]
    straight_flush = [Card(13, 's'), Card(12, 's'), Card(11, 's'), Card(10, 's'), Card(9, 's')]
    four_of_a_kind = [Card(14, 's'), Card(14, 'h'), Card(14, 'd'), Card(14, 'c'), Card(10, 's')]
    full_house = [Card(14, 's'), Card(14, 'h'), Card(14, 'd'), Card(10, 'c'), Card(10, 's')]
    flush = [Card(14, 's'), Card(13, 's'), Card(12, 's'), Card(11, 's'), Card(9, 's')]
    straight = [Card(14, 's'), Card(13, 'h'), Card(12, 'd'), Card(11, 'c'), Card(10, 's')]
    three_of_a_kind = [Card(14, 's'), Card(14, 'h'), Card(14, 'd'), Card(10, 'c'), Card(9, 's')]
    two_pair = [Card(14, 's'), Card(14, 'h'), Card(10, 'd'), Card(10, 'c'), Card(9, 's')]
    pair = [Card(14, 's'), Card(14, 'h'), Card(10, 'd'), Card(9, 'c'), Card(8, 's')]
    high_card = [Card(14, 's'), Card(13, 'h'), Card(10, 'd'), Card(9, 'c'), Card(8, 's')]

    all_cards = [royal_flush, straight_flush, four_of_a_kind, full_house, flush, straight, three_of_a_kind, two_pair, pair, high_card]

    for cards in all_cards:
        for card in cards:
            print(str(card), end=' ')
        name, strength = game._calculate_hand_strength(cards)
        print(f'Hand: {name}, Strength: {strength}')
        print()

