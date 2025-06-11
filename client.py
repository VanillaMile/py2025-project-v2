import pygame
import sys
from network import Network
import pickle
import tkinter as tk
from tkinter import simpledialog

pygame.init()

class Client:
    def __init__(self):
        self.width, self.height = 1200, 800
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Client")

        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self.player_name = "test_player" 

        # Example values for demonstration
        self.current_pot = None
        self.current_bet = None
        self.your_bet = None
        self.current_player = None 
        self.is_my_turn = None
        self.pot = None 
        self.witing_for = None
        self.available_actions = None 
        self.player_infos = None 
        self.player_info = None
        self.stack = None 
        self.hand = None 
        self.bet = None 
        self.folded = None 
        self.all_in = None 
        self.checked = None 
        self.action = None
        self.cards_exchange = None
        self.next = None

        # Button setup
        self.button_width, self.button_height = 130, 50
        self.button_gap = 20
        self.button_texts = ["Call", "Check", "Raise", "All In", "Fold", "start_game"]
        self.buttons = []
        num_buttons = len(self.button_texts)
        for i in range(num_buttons):
            x = (self.width - (num_buttons * self.button_width + (num_buttons - 1) * self.button_gap)) // 2 + i * (self.button_width + self.button_gap)
            y = self.height - self.button_height - 30
            self.buttons.append(pygame.Rect(x, y, self.button_width, self.button_height))

        # Cards tab setup
        self.cards_tab_rect = pygame.Rect((self.width - 200) // 2, 80, 200, 40)

        # Chatbox (history) setup
        self.chatbox_rect = pygame.Rect(100, 150, self.width - 200, 300)
        self.chat_lines = ["Welcome to the poker!"]

        self.current_player = "Player2"

    def draw_window(self):
        self.win.fill((30, 30, 30))

        # Draw current pot (top left)
        pot_surf = self.small_font.render(f"Pot: {self.current_pot}", True, (255, 215, 0))
        self.win.blit(pot_surf, (20, 20))

        # Draw current bet and your bet (top right)
        bet_surf = self.small_font.render(f"Current Bet: {self.current_bet}", True, (173, 216, 230))
        your_bet_surf = self.small_font.render(f"Your Bet: {self.your_bet}", True, (144, 238, 144))
        money_surf = self.small_font.render(f"Money: {self.stack}", True, (255, 255, 102))
        self.win.blit(bet_surf, (self.width - bet_surf.get_width() - 20, 20))
        self.win.blit(your_bet_surf, (self.width - your_bet_surf.get_width() - 20, 20 + bet_surf.get_height() + 5))
        self.win.blit(money_surf, (self.width - money_surf.get_width() - 20, 20 + bet_surf.get_height() + your_bet_surf.get_height() + 10))

        # Draw player name at top
        name_surf = self.font.render(self.player_name, True, (255, 255, 255))
        self.win.blit(name_surf, ((self.width - name_surf.get_width()) // 2, 30))

        # Draw "Cards" tab under player name
        pygame.draw.rect(self.win, (60, 60, 60), self.cards_tab_rect)
        pygame.draw.rect(self.win, (200, 200, 200), self.cards_tab_rect, 2)
        # Render each letter of self.hand with color based on escape codes
        hand_str = str(self.hand)
        rendered_letters = []
        i = 0
        color = (255, 255, 255)
        while i < len(hand_str):
            if hand_str[i] == 'R':
                color = (255, 0, 0)  # red
                i += 1
                continue
            elif hand_str[i] == 'B':
                color = (0, 0, 0)  # black
                i += 1
                continue
            else:
                letter = hand_str[i]
                letter_surf = self.small_font.render(letter, True, color)
                rendered_letters.append(letter_surf)
                i += 1

        # Combine rendered letters horizontally
        total_width = sum(surf.get_width() for surf in rendered_letters)
        max_height = max((surf.get_height() for surf in rendered_letters), default=0)
        cards_surf = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
        x = 0
        for surf in rendered_letters:
            cards_surf.blit(surf, (x, 0))
            x += surf.get_width()
        self.win.blit(cards_surf, (self.cards_tab_rect.x + (self.cards_tab_rect.width - cards_surf.get_width()) // 2,
                            self.cards_tab_rect.y + (self.cards_tab_rect.height - cards_surf.get_height()) // 2))

        # Draw chat/history box
        pygame.draw.rect(self.win, (50, 50, 50), self.chatbox_rect)
        pygame.draw.rect(self.win, (200, 200, 200), self.chatbox_rect, 2)

        # Draw chat lines
        for i, line in enumerate(self.chat_lines[-10:]):
            line_surf = self.small_font.render(line, True, (255, 255, 255))
            self.win.blit(line_surf, (self.chatbox_rect.x + 10, self.chatbox_rect.y + 10 + i * 28))

        # Draw "Current player:" under history
        current_player_surf = self.small_font.render(f"Waiting for player to make a move: {self.witing_for}", True, (255, 255, 0))
        self.win.blit(current_player_surf, (self.chatbox_rect.x + 10, self.chatbox_rect.y + self.chatbox_rect.height + 10))

        # Draw buttons
        for i, rect in enumerate(self.buttons):
            pygame.draw.rect(self.win, (100, 100, 250), rect)
            pygame.draw.rect(self.win, (255, 255, 255), rect, 2)
            text_surf = self.small_font.render(self.button_texts[i], True, (255, 255, 255))
            self.win.blit(text_surf, (rect.x + (self.button_width - text_surf.get_width()) // 2,
                                rect.y + (self.button_height - text_surf.get_height()) // 2))

        pygame.display.update()

    def setup_buttons(self):
        # Only show action buttons if it's this player's turn
        self.buttons = []
        self.button_texts = []

        # Check if it's this player's turn
        if self.witing_for == self.player_name or self.witing_for == "Unknown":
            actions = ['call', 'check', 'raise', 'all_in', 'fold']
            visible_actions = [a for a in actions if self.available_actions and a in self.available_actions]
            num_buttons = len(visible_actions)
            for i, action in enumerate(visible_actions):
                x = (self.width - (num_buttons * self.button_width + (num_buttons - 1) * self.button_gap)) // 2 + i * (self.button_width + self.button_gap)
                y = self.height - self.button_height - 30
                rect = pygame.Rect(x, y, self.button_width, self.button_height)
                self.buttons.append(rect)
                self.button_texts.append(action.capitalize())

            if self.player_name == "Player1" and self.available_actions == []:
                x = (self.width - ((num_buttons + 1) * self.button_width + num_buttons * self.button_gap)) // 2 + num_buttons * (self.button_width + self.button_gap)
                y = self.height - self.button_height - 30
                rect = pygame.Rect(x, y, self.button_width, self.button_height)
                self.buttons.append(rect)
                self.button_texts.append("start_game")
        else:
            # No action buttons if not this player's turn
            self.buttons = []
            self.button_texts = []

    def setup_card_exchange(self, is_bad=False):
        if self.available_actions and set(self.available_actions) == set(['1', '2', '3', '4', '5', '9']) and self.witing_for == self.player_name and self.cards_exchange is None:
            root = tk.Tk()
            root.withdraw()
            if is_bad:
                user_input = simpledialog.askstring(f"{self.playerId} Card Exchange", f"{self.player_name} entered bad data, enter again (like 1 3 4) or leave empty. Keep in mind the cards are sorted so they might be arraged differently:")
            else:
                user_input = simpledialog.askstring(f"{self.playerId} Card Exchange", f"{self.player_name}, enter card indexes to exchange (like 1 3 4) or leave empty. Keep in mind the cards are sorted so they might be arraged differently:")

            input_ = user_input.strip() if user_input else ''
            inputs = input_.split()
            for i in inputs:
                if not i.isdigit() or int(i) < 1 or int(i) > 5:
                    print(f"Invalid input: {i}. Please enter numbers between 1 and 5.")
                    user_input = None
                    break

            if user_input is not None:
                self.cards_exchange = input_
            root.destroy()

    def add_chat_line(self, line):
        if not self.chat_lines or (self.chat_lines[-1] != line and line != ''):
            self.chat_lines.append(line)
        else:
            print("Duplicate chat line detected, not adding:", line)

    is_my_turn = False

    def main(self):
        clock = pygame.time.Clock()
        run = True
        n = Network()
        self.playerId = n.get_id()
        self.player_name = f"Player{self.playerId}"
        self.current_player = f"Player{self.playerId}"

        is_game_active = n.send("is_game_active")
        if is_game_active == "True":
            self.chat_lines.append("Game is already active. Leaving...")
            print("Game is already active. Leaving...")
            run = False

        while run:
            clock.tick(60)

            self.setup_buttons()
            self.setup_card_exchange()

            if self.cards_exchange is not None:
                print(f"Sending card exchange: {self.cards_exchange}")
                n.read_broadcast(self.playerId, exchange=self.cards_exchange)

            print("Waiting for broadcast...")
            data = n.read_broadcast(self.playerId)

            if self.action is not None:
                print(f"Sending action: {self.action}")
                n.read_broadcast(self.playerId, send_action=self.action)
                self.action = None

            if data:
                print("Received broadcast:", data)
                if 'error' in data:
                    self.add_chat_line(f"Error: {data['error']}")

                if 'title' in data and data['title'] == 'game_state':
                    self.current_pot = data.get('pot', 0)
                    self.current_bet = data.get('current_bet', 0)
                    self.witing_for = data.get('waiting_for', 'Unknown')
                    self.available_actions = data.get('available_actions', [])
                    self.message = data.get('message', '')
                    player_infos = data.get('players_info', [])
                    player_info = player_infos[int(self.playerId) - 1] if player_infos else {}
                    self.stack = player_info.get('stack', 0)
                    self.hand = player_info.get('hand', 'something')
                    self.your_bet = player_info.get('bet', 0)
                    self.folded = player_info.get('folded', False)
                    self.all_in = player_info.get('all_in', False)
                    self.checked = player_info.get('checked', False)

                    self.add_chat_line(f"{self.message}")

            if self.available_actions is not ['1', '2', '3', '4', '5', '9']:
                self.cards_exchange = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(self.buttons):
                        if rect.collidepoint(event.pos):
                            self.chat_lines.append(f"You pressed {self.button_texts[i]}")
                            if self.button_texts[i] == "start_game":
                                print("Starting game...")
                                n.read_broadcast(self.playerId, start=True)
                            else:
                                self.action = self.button_texts[i]

            self.draw_window()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Client = Client()
    Client.main()
