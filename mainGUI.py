import json
import pickle
import random
import tkinter as tk
from utility_funcs import change_config, from_visual_to_logic
from PIL import Image, ImageTk
import os

class BlackjackGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Blackjack Simulator")
        self.master.geometry("800x1000")

        # Load config and deck
        with open("config.json", "r") as f:
            self.config = json.load(f)
        with open("data.txt", "rb") as f:
            self.data = pickle.load(f)

        self.money = self.config['starting_bankroll']
        self.bet_size = self.config['bet_size']
        self.deck = self.data['deck'].copy()
        self.deck_visual = self.data['deck_visual'].copy()

        # Dictionary to store card images
        self.card_images = {}
        
        # Load card back image
        self.card_back = ImageTk.PhotoImage(Image.open("media/backs/red.png").resize((100, 145)))

        # Game state
        self.player_hand = []
        self.dealer_hand = []
        self.player_turn = True


        # GUI Elements
        self.info_label = tk.Label(master, text="", font=("Arial", 12))
        self.info_label.pack(pady=10)

        self.dealer_label = tk.Label(master, text="", font=("Arial", 14))
        self.dealer_label.pack(pady=10)


        # Create frames for card images
        self.dealer_cards_frame = tk.Frame(master)
        self.dealer_cards_frame.pack(pady=10)
        
        self.player_cards_frame = tk.Frame(master)
        self.player_cards_frame.pack(pady=10)


        self.player_label = tk.Label(master, text="", font=("Arial", 14))
        self.player_label.pack(pady=10)
        

        self.money_label = tk.Label(master, text="", font=("Arial", 12))
        self.money_label.pack(pady=10)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=20)

        self.hit_button = tk.Button(self.button_frame, text="Hit", width=10, command=self.hit)
        self.stay_button = tk.Button(self.button_frame, text="Stay", width=10, command=self.stay)
        self.continue_button = tk.Button(self.button_frame, text="Continue", width=22, command=self.next_round)
        self.exit_button = tk.Button(self.button_frame, text="Exit", width=10, command=self.exit_game)


        self.start_game()

    def start_game(self):
        text = "" # Reset message text
        if self.money < self.bet_size:
            self.info_label.config(text="You don't have enough money to continue playing. Game over. Broke ass boi.")
            self.hide_action_buttons()
            self.hide_continue_buttons()
            
            self.player_label.pack_forget()
            self.dealer_label.pack_forget()
            self.player_cards_frame.pack_forget()
            self.dealer_cards_frame.pack_forget()

            self.money_label.config(text=f"Money: {self.money}")
            self.exit_button.pack(side=tk.LEFT, padx=10)     
            return

        if len(self.deck) < 20:
            text="Low on cards, reshuffling the deck..."
            self.deck_visual = self.data['deck_visual'].copy()
            random.shuffle(self.deck_visual)

            self.deck = from_visual_to_logic(self.deck_visual)

        self.player_hand = []
        self.dealer_hand = []
        self.player_hand_visual = []
        self.dealer_hand_visual = []
        self.player_turn = True

        # Deal initial cards
        for _ in range(2):
            self.player_hand.append(self.deck.pop(0))
            self.dealer_hand.append(self.deck.pop(0))

            self.player_hand_visual.append(self.deck_visual.pop(0))
            self.dealer_hand_visual.append(self.deck_visual.pop(0))

        if sum(self.player_hand) > 21 and 11 in self.player_hand: # if both aces are drawn
            self.player_hand[self.player_hand.index(11)] = 1  # Convert Ace from 11 to 1


        self.update_display(message=text)
        self.show_action_buttons()
        self.hide_continue_buttons()

    def update_display(self, reveal_dealer=False, message=""):
        # Clear previous cards
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()

        if reveal_dealer:
            dealer_text = f"Dealer hand (Total: {sum(self.dealer_hand)})"
            for card in self.dealer_hand_visual:
                card_str = f"{card[0]}{card[1]}"
                if card_str not in self.card_images:
                    img = Image.open(f"media/fronts/{card_str}.png").resize((100, 145))
                    self.card_images[card_str] = ImageTk.PhotoImage(img)
                label = tk.Label(self.dealer_cards_frame, image=self.card_images[card_str])
                label.pack(side=tk.LEFT, padx=2)
        else:
            dealer_text = f"Dealer hand (Total: ?)"

             # Show card back for dealer's first card
            label = tk.Label(self.dealer_cards_frame, image=self.card_back)
            label.pack(side=tk.LEFT, padx=2)
            
            # Show remaining dealer cards
            for card in self.dealer_hand_visual[1:]:
                card_str = f"{card[0]}{card[1]}"
                if card_str not in self.card_images:
                    img = Image.open(f"media/fronts/{card_str}.png").resize((100, 145))
                    self.card_images[card_str] = ImageTk.PhotoImage(img)
                label = tk.Label(self.dealer_cards_frame, image=self.card_images[card_str])
                label.pack(side=tk.LEFT, padx=2)

        player_text = f"Player hand (Total: {sum(self.player_hand)})"

         # Display player cards
        for card in self.player_hand_visual:
            card_str = f"{card[0]}{card[1]}"
            if card_str not in self.card_images:
                img = Image.open(f"media/fronts/{card_str}.png").resize((100, 145))
                self.card_images[card_str] = ImageTk.PhotoImage(img)
            label = tk.Label(self.player_cards_frame, image=self.card_images[card_str])
            label.pack(side=tk.LEFT, padx=2)

        self.dealer_label.config(text=dealer_text)
        self.player_label.config(text=player_text)
        self.money_label.config(text=f"Money: {self.money}, Bet Size: {self.bet_size}")
        self.info_label.config(text=message)

    def show_action_buttons(self):
        self.hit_button.pack(side=tk.LEFT, padx=10)
        self.stay_button.pack(side=tk.LEFT, padx=10)

    def hide_action_buttons(self):
        self.hit_button.pack_forget()
        self.stay_button.pack_forget()

    def show_continue_button(self):
        self.continue_button.pack(side=tk.LEFT, padx=10)
        self.exit_button.pack(side=tk.LEFT, padx=10)

    def hide_continue_buttons(self):
        self.continue_button.pack_forget()
        self.exit_button.pack_forget()

    def exit_game(self):
        self.master.destroy()  # This will close the window and end the program

    def hit(self):
        self.player_hand.append(self.deck.pop(0))
        self.player_hand_visual.append(self.deck_visual.pop(0))

        if sum(self.player_hand) > 21 and 11 in self.player_hand:
            self.player_hand[self.player_hand.index(11)] = 1  # Convert Ace from 11 to 1

        if sum(self.player_hand) > 21:
            self.update_display(reveal_dealer=True, message="Over 21. You lose!")
            self.money -= self.bet_size
            self.hide_action_buttons()
            self.show_continue_button()
        else:
            self.update_display()

    def stay(self):
        self.hide_action_buttons()
        self.dealer_play()

    def dealer_play(self):
        # Dealer's turn
        if sum(self.dealer_hand) > 21 and 11 in self.dealer_hand: # if both aces are drawn
                self.dealer_hand[self.dealer_hand.index(11)] = 1


        while sum(self.dealer_hand) < self.config['house_stand']:
            self.dealer_hand.append(self.deck.pop(0))
            self.dealer_hand_visual.append(self.deck_visual.pop(0))
            if sum(self.dealer_hand) > 21 and 11 in self.dealer_hand:
                self.dealer_hand[self.dealer_hand.index(11)] = 1

        self.resolve_round()

    def resolve_round(self):
        player_total = sum(self.player_hand)
        dealer_total = sum(self.dealer_hand)
        message = ""

        if dealer_total > 21:
            message = "Dealer busts. You win!"
            self.money += self.bet_size
        elif dealer_total > player_total:
            message = "You lose!"
            self.money -= self.bet_size
        elif dealer_total < player_total:
            message = "You win!"
            self.money += self.bet_size
        else:
            message = "Push. No one wins."

        self.update_display(reveal_dealer=True, message=message)
        self.show_continue_button()

    def next_round(self):
        self.start_game()

if __name__ == "__main__":
    change_config()
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()