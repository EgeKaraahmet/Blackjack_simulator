import json
import pickle
import random
import tkinter as tk
from PIL import Image, ImageTk


# TODO ADD SPLIT
# SPLIT two player hands one dealer hand, play one player hand first.

# Add preset configs and custom configs in configuration window.




class BlackjackGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Blackjack Simulator")
        self.master.geometry("300x300")

        self.menu_frame = tk.Frame(master)
        self.menu_frame.pack(expand=True)

        # Main menu buttons
        self.start_button = tk.Button(self.menu_frame, text="Start Game", width=20, 
                                    command=self.initialize_game_window, font=("Arial", 14))
        self.start_button.pack(pady=20)

        self.config_button = tk.Button(self.menu_frame, text="Change Configuration", 
                                     width=20, command=self.show_config_dialog, font=("Arial", 14))
        self.config_button.pack(pady=20)

        self.exit_desktop_button = tk.Button(self.menu_frame, text="Exit to Desktop", 
                                       width=20, command=self.master.destroy, font=("Arial", 14))
        self.exit_desktop_button.pack(pady=20)

        # Initialize game components as None
        self.game_frame = None
        self.help_frame = None
        self.help_photo = None
        self.card_images = {}
        self.card_back = None
        self.is_drawn = None

        # The game starts as ended. Start_game() runs the game.
        self.is_round_end = True

    def initialize_game_window(self):
        # Hide menu frame
        self.menu_frame.pack_forget()
        
        # Reset window size for game
        self.master.geometry("1920x1040")

        # Initialize game components
        self.help_visible = False
        
        # Main game frame and help chart frame
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=2)  # 2/3
        self.master.grid_columnconfigure(1, weight=1)  # 1/3


        # Create and configure game frame
        self.game_frame = tk.Frame(self.master, width=1280, height=1040, bg='darkgreen')  # 2/3 of 1920
        self.game_frame.grid(row=0, column=0, sticky='nsew')
        self.game_frame.pack_propagate(False)  # Prevent frame from resizing
        
        # Create and configure help frame
        self.help_frame = tk.Frame(self.master, width=640, height=1040, bg='lightblue')  # 1/3 of 1920
        self.help_frame.grid(row=0, column=1, sticky='nsew')
        self.help_frame.grid_propagate(False)  # Prevent frame from resizing

        # Load help image - resize to fit help_frame width
        help_img = Image.open("media/strategy/BJA_Basic_Strategy.jpg")
        help_img = help_img.resize((512, 630))
        self.help_photo = ImageTk.PhotoImage(help_img)

        # Help running count
        self.count_label = None

        # Remaining deck count
        self.deck_label = None

        # Optimal policy label
        self.policy_label = None

        # Load config and deck
        with open("config.json", "r") as f:
            self.config = json.load(f)
        with open("data.txt", "rb") as f:
            self.data = pickle.load(f)

        self.money = self.config['starting_bankroll']
        self.bet_size = 0
        self.deck = self.data['deck'].copy()
        self.deck_visual = self.data['deck_visual'].copy()

        # Two running counts are used. One is used mid-round.
        self.running_count_old = 0
        self.running_count = 0

        self.create_gui_elements()

        # self.start_game()
        self.show_continue_buttons()

    def create_gui_elements(self):
        # Load card back image
        self.card_back = ImageTk.PhotoImage(Image.open("media/backs/red.png").resize((100, 145)))

        # Game state
        self.player_hand = []
        self.dealer_hand = []
        self.player_turn = False


        # GUI Elements
        self.info_label = tk.Label(self.game_frame, text="", font=("Arial", 12), bg='darkgreen')
        self.info_label.pack(anchor='w', pady=10, padx=200)

        self.dealer_label = tk.Label(self.game_frame, text="", font=("Arial", 14), bg='lightgreen')
        self.dealer_label.pack(anchor='w', pady=10, padx=200)


        # Create frames for card images
        self.dealer_cards_frame = tk.Frame(self.game_frame, bg='darkgreen')
        self.dealer_cards_frame.pack(anchor='w', pady=10, padx=200)
        
        self.player_cards_frame = tk.Frame(self.game_frame, bg='darkgreen')
        self.player_cards_frame.pack(anchor='w', pady=10, padx=200)


        self.player_label = tk.Label(self.game_frame, text="", font=("Arial", 14), bg='lightgreen')
        self.player_label.pack(anchor='w', pady=10, padx=200)
        

        self.money_label = tk.Label(self.game_frame, text="", font=("Arial", 12), bg='lightgreen')
        self.money_label.pack(anchor='w', pady=10, padx=200)

        self.button_frame1 = tk.Frame(self.game_frame, bg='darkgreen')
        self.button_frame1.pack(anchor='w', pady=20, padx=200)

        self.button_frame2 = tk.Frame(self.game_frame, bg='darkgreen')
        self.button_frame2.pack(anchor='w', pady=20, padx=200)

        self.hit_button = tk.Button(self.button_frame1, text="Hit", width=10, command=self.hit)
        self.stand_button = tk.Button(self.button_frame1, text="Stand", width=10, command=self.stand)
        self.surrender_button = tk.Button(self.button_frame2, text="Surrender", width=10, command=self.surrender)
        self.double_down_button = tk.Button(self.button_frame2, text="Double Down", width=10, command=self.double_down)

        self.continue_button = tk.Button(self.button_frame1, text="Continue", width=14, command=self.next_round)
        self.exit_button = tk.Button(self.button_frame1, text="Exit", width=6, command=self.exit_game)

        # Add help button in a separate frame
        self.help_button_frame = tk.Frame(self.game_frame, bg='darkgreen')
        self.help_button_frame.pack(anchor='w', pady=10, padx=225)
        
        self.help_button = tk.Button(self.help_button_frame, 
                                       text="Toggle Help", 
                                       width=20, 
                                       command=self.toggle_help)
        self.help_button.pack(side=tk.LEFT)

        # Create chip buttons with different values and colors
        self.chip_values = {
            1: ('red', '1'),
            5: ('blue', '5'),
            25: ('green', '25'),
            100: ('black', '100')
        }
        
        # Move chips frame inside button_frame1 (next to Hit/Stand)
        self.chips_frame = tk.Frame(self.help_button_frame, bg='darkgreen')

        # Move bet display frame inside button_frame2 (next to Double/Surrender)
        self.bet_display_frame = tk.Frame(self.button_frame1, bg='white', width=150, height=100)
        
        # Label to show current bet
        self.bet_display_label = tk.Label(self.bet_display_frame, 
                                        text="Current Bet: 0",
                                        bg='white')
        
        # Frame to display chip images
        self.placed_chips_frame = tk.Frame(self.bet_display_frame, bg='white')
        
        # Move clear bet button to help_button_frame
        self.clear_bet_button = tk.Button(self.button_frame2,
                                        text="Clear Bet",
                                        command=self.clear_bet)
        
        # Initialize bet tracking
        self.current_bet = 0
        self.placed_chips = []
        
    def start_game(self):
        text = "" # Reset message text
        if self.money < 0:
            self.info_label.config(text="You don't have enough money to continue playing. Game over.")
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

            self.deck = self.from_visual_to_logic(self.deck_visual)

            self.running_count = 0 # Reset running count on reshuffle
            self.running_count_old = 0

        self.player_hand = []
        self.dealer_hand = []
        self.player_hand_visual = []
        self.dealer_hand_visual = []
        self.player_turn = True
        self.is_drawn = False
        self.is_round_end = False

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

        # Running count logic
        self.running_count = self.running_count_old # Start with prev round running count
        # Count dealer's visible cards
        if reveal_dealer:
            # Count all dealer cards if revealed
            for card in self.dealer_hand:
                if card <= 6:
                    self.running_count += 1
                elif card >= 10:
                    self.running_count -= 1
        else:
            # Count only the visible dealer card
            visible_card = self.dealer_hand[1]  # Second card is visible
            if visible_card <= 6:
                self.running_count += 1
            elif visible_card >= 10:
                self.running_count -= 1

        # Count player's cards
        for card in self.player_hand:
            if card <= 6:
                self.running_count += 1
            elif card >= 10:
                self.running_count -= 1

        # Update count labels if it exists
        if self.help_visible and self.count_label:
            for widget in self.help_frame.winfo_children():
                widget.destroy()

            optimal_move_str = self.find_optimal_move()
            if optimal_move_str == 'Hit':
                background_color_policy = 'white'
            elif optimal_move_str == 'Stand':
                background_color_policy = 'yellow1'
            elif optimal_move_str == 'Double Down':
                background_color_policy = 'forestgreen'
            elif optimal_move_str == 'Surrender':
                background_color_policy = 'darkgray'
            else: # split
                background_color_policy = 'deepskyblue3'

            if self.running_count < -5:
                background_color_running_count = 'darkgray'
            elif self.running_count > 10:
                background_color_running_count = 'lightblue'
            else:
                background_color_running_count = 'white'
            
            # Add labels at specific rows
            self.count_label = tk.Label(self.help_frame, 
                                    text=f"Running Count: {self.running_count}", 
                                    font=("Arial", 14, "bold"), bg=background_color_running_count)
            self.count_label.grid(row=0, pady=10, sticky='ew')

            self.deck_label = tk.Label(self.help_frame, 
                                    text=f"Remaining Decks: {len(self.deck) / 52:.2f}", 
                                    font=("Arial", 14, "bold"))
            self.deck_label.grid(row=1, pady=10, sticky='ew')
            
            self.policy_label = tk.Label(self.help_frame, 
                                    text=f"Optimal Move: {self.find_optimal_move()}", 
                                    font=("Arial", 14, "bold"), bg=background_color_policy)
            self.policy_label.grid(row=2, pady=10, sticky='ew')

            help_label = tk.Label(self.help_frame, image=self.help_photo)
            help_label.grid(row=3, pady=10, sticky='nsew')

            self.help_button.config(text="Hide Help")
            self.help_visible = True


            self.count_label.config(text=f"Running Count: {self.running_count}")
            self.deck_label.config(text=f"Remaining Decks: {len(self.deck) / 52:.2f}")
            self.policy_label.config(text=f"Optimal Move: {self.find_optimal_move()}")

        self.dealer_label.config(text=dealer_text)
        self.player_label.config(text=player_text)
        self.money_label.config(text=f"Money: {self.money}, Bet Size: {self.bet_size}")
        self.info_label.config(text=message)

    def show_config_dialog(self):
        # Create configuration dialog
        config_window = tk.Toplevel(self.master)
        config_window.title("Configuration")
        config_window.geometry("500x600")

        # Pool size
        tk.Label(config_window, text="Pool size (multiples of std deck):", font=("Arial", 12)).pack(pady=5)
        pool_entry = tk.Entry(config_window)
        pool_entry.pack(pady=5)

        # Deck size
        tk.Label(config_window, text="Deck size:", font=("Arial", 12)).pack(pady=5)
        deck_entry = tk.Entry(config_window)
        deck_entry.pack(pady=5)

        # Balanced deck
        balanced_var = tk.BooleanVar()
        tk.Checkbutton(config_window, text="Balanced deck", variable=balanced_var, 
                      font=("Arial", 12)).pack(pady=5)

        # Starting bankroll
        tk.Label(config_window, text="Starting bankroll:", font=("Arial", 12)).pack(pady=5)
        bankroll_entry = tk.Entry(config_window)
        bankroll_entry.pack(pady=5)

        # Surrender allowed
        surrender_var = tk.BooleanVar()
        tk.Checkbutton(config_window, text="Allow surrender", variable=surrender_var, 
                      font=("Arial", 12)).pack(pady=5)

        # Double down allowed
        double_var = tk.BooleanVar()
        tk.Checkbutton(config_window, text="Allow double down", variable=double_var, 
                      font=("Arial", 12)).pack(pady=5)

        # Replace the house stand input with a checkbox
        soft17_var = tk.BooleanVar()
        tk.Checkbutton(config_window, text="Dealer stands on soft 17?", 
                   variable=soft17_var, font=("Arial", 12)).pack(pady=5)

        def save_config():
            # Get values from entries
            pool_multiple = int(pool_entry.get())
            deck_size = int(deck_entry.get())
            is_balanced = balanced_var.get()
            
            # Create deck
            suits = ['♠', '♣', '♥', '♦']
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            standard_deck_visual = [(rank, suit) for suit in suits for rank in ranks]
            pool_visual = pool_multiple * standard_deck_visual
            custom_deck, custom_deck_visual = self.build_deck(pool_visual, deck_size, is_balanced)

            # Save configuration
            game_settings_dict = {
                'deck_size': deck_size,
                'is_balanced': is_balanced,
                'starting_bankroll': int(bankroll_entry.get()),
                'is_surrender': surrender_var.get(),
                'is_double_down': double_var.get(),
                'stands_soft17': int(soft17_var.get())
            }

            data_dict = {'deck': custom_deck, "deck_visual": custom_deck_visual}

            with open("config.json", "w") as f:
                json.dump(game_settings_dict, f)

            with open("data.txt", "wb") as f:
                pickle.dump(data_dict, f)

            config_window.destroy()

        # Save button
        tk.Button(config_window, text="Save", command=save_config, 
                 font=("Arial", 12)).pack(pady=20)

    def show_action_buttons(self):
        self.hit_button.pack(side=tk.LEFT, padx=10)
        self.stand_button.pack(side=tk.LEFT, padx=10)

        # Only show surrender button if allowed in config AND if the player has not already drawn a card this turn
        if self.config['is_surrender'] and (self.is_drawn == False):
            self.surrender_button.pack(side=tk.LEFT, padx=10)

        # Only show double down if player has enough money AND if allowed in config
        if (self.money >= 2 * self.bet_size) and (self.config['is_double_down']) and (self.is_drawn == False):
            self.double_down_button.pack(side=tk.LEFT, padx=10)

    def hide_action_buttons(self):
        self.hit_button.pack_forget()
        self.stand_button.pack_forget()
        self.surrender_button.pack_forget()
        self.double_down_button.pack_forget()

    def show_continue_buttons(self):
        self.continue_button.pack(side=tk.LEFT, padx=10)
        self.exit_button.pack(side=tk.LEFT, padx=10)

        self.chips_frame.pack(side=tk.LEFT, padx=50)  # Pack to the left with padding
        # Create chip buttons
        for value, (color, text) in self.chip_values.items():
            self.chip_button = tk.Button(self.chips_frame, 
                                text=text,
                                bg=color,
                                fg='white',
                                width=4,
                                height=2,
                                command=lambda v=value: self.add_chip(v))
            self.chip_button.pack(side=tk.LEFT, padx=5)
        self.bet_display_frame.pack(side=tk.LEFT, padx=50)  # Pack to the left with padding
        self.bet_display_frame.pack_propagate(False)
        self.bet_display_label.pack(pady=5)
        self.placed_chips_frame.pack(expand=True)
        self.clear_bet_button.pack(side=tk.RIGHT, padx= 280)  # Pack to the left of help button

    def hide_continue_buttons(self):
        self.continue_button.pack_forget()
        self.exit_button.pack_forget()

         # Clear all chip buttons
        for widget in self.chips_frame.winfo_children():
            widget.destroy()

        self.bet_display_frame.pack_forget()
        self.bet_display_label.pack_forget()
        self.placed_chips_frame.pack_forget()
        self.clear_bet_button.pack_forget()

    def toggle_help(self):
        if self.help_visible:
            for widget in self.help_frame.winfo_children():
                widget.destroy()

            self.help_button.config(text="Show help")
            self.help_visible = False
        else:

            # Clear any existing widgets
            for widget in self.help_frame.winfo_children():
                widget.destroy()

            optimal_move_str = self.find_optimal_move()
            if optimal_move_str == 'Hit':
                background_color_policy = 'white'
            elif optimal_move_str == 'Stand':
                background_color_policy = 'yellow1'
            elif optimal_move_str == 'Double Down':
                background_color_policy = 'emeraldgreen'
            elif optimal_move_str == 'Surrender':
                background_color_policy = 'darkgray'
            else: # split
                background_color_policy = 'deepskyblue3'

            if self.running_count < -5:
                background_color_running_count = 'darkgray'
            elif self.running_count > 10:
                background_color_running_count = 'lightblue'
            else:
                background_color_running_count = 'white'
            
            # Add labels at specific rows
            self.count_label = tk.Label(self.help_frame, 
                                    text=f"Running Count: {self.running_count}", 
                                    font=("Arial", 14, "bold"), bg=background_color_running_count)
            self.count_label.grid(row=0, pady=10, sticky='ew')

            self.deck_label = tk.Label(self.help_frame, 
                                    text=f"Remaining Decks: {len(self.deck) / 52:.2f}", 
                                    font=("Arial", 14, "bold"))
            self.deck_label.grid(row=1, pady=10, sticky='ew')
            
            self.policy_label = tk.Label(self.help_frame, 
                                    text=f"Optimal Move: {self.find_optimal_move()}", 
                                    font=("Arial", 14, "bold"), bg=background_color_policy)
            self.policy_label.grid(row=2, pady=10, sticky='ew')

            help_label = tk.Label(self.help_frame, image=self.help_photo)
            help_label.grid(row=3, pady=10, sticky='nsew')

            self.help_button.config(text="Hide Help")
            self.help_visible = True
  
    def exit_game(self):
        # Clear game window
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        self.game_frame.grid_forget()
        for widget in self.help_frame.winfo_children():
            widget.destroy()
        self.help_frame.grid_forget()
        
        # Reset window size
        self.master.geometry("400x300")
        
        # Show main menu again
        self.menu_frame.pack(expand=True)

    def hit(self):
        self.is_drawn = True # Flag to indicate player has drawn a card this turn

        self.player_hand.append(self.deck.pop(0))
        self.player_hand_visual.append(self.deck_visual.pop(0))

        if sum(self.player_hand) > 21 and 11 in self.player_hand:
            self.player_hand[self.player_hand.index(11)] = 1  # Convert Ace from 11 to 1

        if sum(self.player_hand) > 21:
            self.is_drawn = False
            self.player_turn = False
            self.money -= self.bet_size
            self.is_round_end = True
            self.update_display(reveal_dealer=True, message="Over 21. You lose!")
            self.hide_action_buttons()
            self.show_continue_buttons()
        else:
            # Hide and then show action buttons to refresh them, as now double down and surrender shouldnt be possible.
            self.hide_action_buttons()
            self.show_action_buttons()

            self.update_display()

    def stand(self):
        self.hide_action_buttons()
        self.dealer_play()

    def surrender(self):
        """Player surrenders and loses half the bet."""
        self.hide_action_buttons()
        loss_amount = self.bet_size / 2
        self.money -= loss_amount
        self.is_round_end = True
        self.player_turn = False
        self.update_display(reveal_dealer=True, message=f"You surrendered. Lost {loss_amount}.")
        self.show_continue_buttons()

    def double_down(self):
        """Player doubles the bet, gets one card, and ends turn."""
        self.hide_action_buttons()
        original_bet = self.bet_size
        self.bet_size *= 2  # Double the bet size
        self.player_hand.append(self.deck.pop(0))
        self.player_hand_visual.append(self.deck_visual.pop(0))
        self.is_round_end = True

        if sum(self.player_hand) > 21 and 11 in self.player_hand:
            self.player_hand[self.player_hand.index(11)] = 1  # Convert Ace from 11 to 1

        if sum(self.player_hand) > 21:
            self.update_display(reveal_dealer=True, message="Over 21. You lose!")
            self.money -= self.bet_size
            self.hide_action_buttons()
            self.bet_size = original_bet  # Reset bet size for next round
            self.show_continue_buttons()
        else:
            self.update_display()
            self.dealer_play()
            self.bet_size = original_bet  # Reset bet size for next round

    def dealer_play(self):
        # Dealer's turn


        if sum(self.dealer_hand) > 21 and 11 in self.dealer_hand: # if both aces are drawn
                self.dealer_hand[self.dealer_hand.index(11)] = 1

        if self.config['stands_soft17']: # if stands on soft 17, draw cards easy way

            while (sum(self.dealer_hand) < 17):
                self.dealer_hand.append(self.deck.pop(0))
                self.dealer_hand_visual.append(self.deck_visual.pop(0))
                if sum(self.dealer_hand) > 21 and 11 in self.dealer_hand:
                    self.dealer_hand[self.dealer_hand.index(11)] = 1
        
        else: # Still draws if A and 6 present.
            while (sum(self.dealer_hand) < 17) or (sum(self.dealer_hand) == 17 and 11 in self.dealer_hand):
                self.dealer_hand.append(self.deck.pop(0))
                self.dealer_hand_visual.append(self.deck_visual.pop(0))
                if sum(self.dealer_hand) > 21 and 11 in self.dealer_hand:
                    self.dealer_hand[self.dealer_hand.index(11)] = 1

        self.resolve_round()

    def find_optimal_move(self):

        # look at player and dealer hands, and return optimal move.
        dealer_upcard = self.dealer_hand[1]

        player_cards_total = sum(self.player_hand)
        if 11 in self.player_hand:
            is_soft = True
        else:
            is_soft = False

        if self.is_round_end: # Round ended, no need for optimal move
            return ""

        if (is_soft == False) and (player_cards_total == 16) and (dealer_upcard >= 9) and (self.config['is_surrender']) and (self.is_drawn == False):
            return "Surrender"
        elif (is_soft == False) and (player_cards_total == 15) and (dealer_upcard == 10) and (self.config['is_surrender']) and (self.is_drawn == False):
            return "Surrender"
        elif (is_soft == False) and (player_cards_total == 11) and (self.config['is_double_down']) and (self.money >= 2 * self.bet_size) and (self.is_drawn == False):
            return "Double Down"
        elif (is_soft == False) and (player_cards_total == 10) and (self.config['is_double_down']) and (self.money >= 2 * self.bet_size) and (dealer_upcard <= 9) and (self.is_drawn == False):
            return "Double Down"
        elif (is_soft == False) and (player_cards_total == 9) and (self.config['is_double_down']) and (self.money >= 2 * self.bet_size) and (dealer_upcard >= 3) and (dealer_upcard <= 6) and (self.is_drawn == False):
            return "Double Down"
        elif (is_soft == False) and (player_cards_total >= 17):
            return "Stand"
        elif (is_soft == False) and (player_cards_total >= 13) and (player_cards_total <= 16) and (dealer_upcard >= 2) and (dealer_upcard <= 6):
            return "Stand"
        elif (is_soft == False) and (player_cards_total == 12) and (dealer_upcard >= 4) and (dealer_upcard <= 6):
            return "Stand"
        elif (is_soft == True) and (player_cards_total == 19) and (dealer_upcard == 6) and (self.config['is_double_down']) and (self.money >= 2 * self.bet_size) and (self.is_drawn == False):
            return "Double Down"
        elif (is_soft == True) and (player_cards_total >= 19):
            return "Stand"
        elif (is_soft == True) and (player_cards_total == 18) and (dealer_upcard >= 2) and (dealer_upcard <= 6) and (self.config['is_double_down']) and (self.money >= 2 * self.bet_size) and (self.is_drawn == False):
            return "Double Down"
        elif (is_soft == True) and (player_cards_total == 18) and (dealer_upcard <= 8):
            return "Stand"
        else:
            return "Hit"

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

        self.is_round_end = True

        self.update_display(reveal_dealer=True, message=message)
        self.show_continue_buttons()

    def next_round(self):

        self.running_count_old = self.running_count  # Store current running count for next round
        # Update count label if it exists
        if self.help_visible and self.count_label:
            self.count_label.config(text=f"Running Count: {self.running_count_old}")

        if self.bet_size > 0:
            self.start_game()
        else:
            self.info_label.config(text="Enter a bet!")
    
    def change_config(self):
        """Function to change the game configuration, and then store these in config.json and data.txt."""
        print("Changing configuration...\n")

        deck_change = input("Make changes to deck? (y/n) ")
        if deck_change.lower() == 'y':

            suits = ['♠', '♣', '♥', '♦']
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

            standard_deck_visual = [(rank, suit) for suit in suits for rank in ranks]

            pool_multiple = int(input("Pool size (multiples of std deck) (int): "))
            deck_size = int(input("Deck size (int): "))
            is_balanced = input("Balanced deck? (y/n): ").lower() == 'y'
            print("\n")

            pool_visual = pool_multiple * standard_deck_visual

            custom_deck, custom_deck_visual = self.build_deck(pool_visual, deck_size, is_balanced)

            print(f"New deck built with a size of {len(custom_deck)}.")
            if is_balanced:
                print("The deck is balanced.")
            else:
                print("The deck is not balanced.")
        else:
            with open("data.txt", "rb") as f:
                data = pickle.load(f)
                f.close()
            custom_deck = data['deck']
            custom_deck_visual = data['deck_visual']
            with open("config.json", "r") as f:
                config = json.load(f)
                f.close()
            deck_size = len(custom_deck)
            is_balanced = config['is_balanced']
            

        print("\n")
        config_change = input("Make changes to other settings? (y/n) ")
        if config_change.lower() == 'y':
            starting_bankroll = int(input("Starting bankroll (int): "))
            bet_size = int(input("Bet size (int): "))
            is_surrender = input("Is surrender allowed? (y/n): ").lower() == 'y'
            is_double_down = input("Is double down allowed? (y/n): ").lower() == 'y'
            stands_soft17 = int(input("House stands on (int, usually 17): "))
        else:
            with open("config.json", "r") as f:
                config = json.load(f)
                f.close()
            starting_bankroll = config['starting_bankroll']
            bet_size = config['bet_size']
            is_surrender = config['is_surrender']
            is_double_down = config['is_double_down']
            stands_soft17 = config['stands_soft17']

        game_settings_dict = {'deck_size': len(custom_deck), 'is_balanced': is_balanced,
                            'starting_bankroll': starting_bankroll, 'bet_size': bet_size,
                            'is_surrender': is_surrender, 'is_double_down': is_double_down,
                            'stands_soft17': stands_soft17}

        data_dict = {'deck': custom_deck, "deck_visual": custom_deck_visual}

        with open("config.json", "w") as f:
            json.dump(game_settings_dict, f)
            f.close()

        with open("data.txt", "wb") as f:
            pickle.dump(data_dict, f)
            f.close()

        print("\n")
        print("Changes saved.\n")

    def build_deck(self, pool_visual, build_size, is_balanced):
        """Builds a deck of cards based on the chosen cards and balance preference."""
        custom_deck = [0] * build_size # Initialize empty deck
        custom_deck_visual = [0] * build_size # Initialize empty deck for visual representation

        pool = self.from_visual_to_logic(pool_visual)

        if is_balanced:
            remaining_empty_slots = build_size # Total slots in the custom deck which is empty
            running_count = 0
            for i in range(build_size):
                random_index = random.randint(0, len(pool)-1)
                custom_deck[i] = pool[random_index]
                custom_deck_visual[i] = pool_visual[random_index]
                if pool[random_index] <= 6:
                    running_count = running_count + 1
                    remaining_empty_slots = remaining_empty_slots - 1
                elif pool[random_index] >= 10:
                    running_count = running_count - 1
                    remaining_empty_slots = remaining_empty_slots - 1
                else:
                    remaining_empty_slots = remaining_empty_slots - 1 # Neutral cards

                pool.pop(random_index)  # Remove to avoid duplicates
                pool_visual.pop(random_index)


                # Adjust the deck to be balanced
                if abs(running_count) > remaining_empty_slots:

                    # Fill this 1 slot with neutral card. This ensures that the deck can be balanced (no odd numbers).
                    random_index = random.randint(0, len(pool)-1)
                    while pool[random_index] >= 10 or pool[random_index] <= 6: #  Avoid high and low cards 
                        random_index = random.randint(0, len(pool)-1)

                    custom_deck[i] = pool[random_index]
                    custom_deck_visual[i] = pool_visual[random_index]
                    pool.pop(random_index)  # Remove to avoid duplicates
                    pool_visual.pop(random_index)  # Remove to avoid duplicates
                    i_note = i + 1
                    break
                if abs(running_count) == remaining_empty_slots:
                    i_note = i + 1
                    break

            if running_count < 0: # More high cards drawn
                for j in range(i_note, build_size):
                    random_index = random.randint(0, len(pool)-1)
                    while pool[random_index] >= 7: # Avoid high and neutral cards
                        pool.pop(random_index) # Remove unwanted cards to reduce pool size for performance
                        pool_visual.pop(random_index)
                        random_index = random.randint(0, len(pool)-1)
                    custom_deck[j] = pool[random_index]
                    custom_deck_visual[j] = pool_visual[random_index]
                    pool.pop(random_index)  # Remove to avoid duplicates
                    pool_visual.pop(random_index)
            elif running_count > 0:
                for j in range(i_note, build_size):
                    random_index = random.randint(0, len(pool)-1)
                    while pool[random_index] <= 9: # Avoid low and neutral cards
                        pool.pop(random_index) # Remove unwanted cards to reduce pool size for performance
                        pool_visual.pop(random_index)
                        random_index = random.randint(0, len(pool)-1)
                    custom_deck[j] = pool[random_index]
                    custom_deck_visual[j] = pool_visual[random_index]
                    pool.pop(random_index)  # Remove to avoid duplicates
                    pool_visual.pop(random_index)


            random.shuffle(custom_deck_visual) # Shuffle the deck as last operation. This ensures randomness (for balanced decks)
            custom_deck = self.from_visual_to_logic(custom_deck_visual)

        else:
            for i in range(build_size):
                random_index = random.randint(0, len(pool)-1)
                custom_deck[i] = pool[random_index]
                custom_deck_visual[i] = pool_visual[random_index]
                pool.pop(random_index)  # Remove to avoid duplicates
                pool_visual.pop(random_index)


        return custom_deck, custom_deck_visual

    def from_visual_to_logic(self, deck_visual):
        """Converts a visually represented deck to a logically represented deck."""
        logic_deck = []
        for card in deck_visual:
            rank = card[0]
            if rank in ['J', 'Q', 'K']:
                logic_deck.append(10)
            elif rank == 'A':
                logic_deck.append(11)
            else:
                logic_deck.append(int(rank))
        return logic_deck

    def add_chip(self, value):
        """Add a chip to the current bet"""
        if self.is_round_end:  # Only allow betting before the round starts
            self.current_bet += value
            self.placed_chips.append(value)
            self.update_bet_display()
            self.bet_size = self.current_bet

    def clear_bet(self):
        """Clear all placed chips"""
        a = 5
        b = 4 # for debugging.
        if self.is_round_end:  # Only allow clearing before the round starts
            self.current_bet = 0
            self.placed_chips = []
            self.update_bet_display()
            self.bet_size = self.current_bet

    def update_bet_display(self):
        """Update the bet display with current chips"""
        # Update bet amount text
        self.bet_display_label.config(text=f"Current Bet: {self.current_bet}")
        
        # Clear existing chip displays
        for widget in self.placed_chips_frame.winfo_children():
            widget.destroy()
        
        # Show chips in rows of 4
        row = 0
        col = 0
        for chip in self.placed_chips:
            color, _ = self.chip_values[chip]
            chip_label = tk.Label(self.placed_chips_frame,
                                text=str(chip),
                                bg=color,
                                fg='white',
                                width=3,
                                height=1)
            chip_label.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col >= 4:
                col = 0
                row += 1


if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackGame(root)
    root.mainloop()