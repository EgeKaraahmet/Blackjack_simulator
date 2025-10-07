import json
import pickle
import random
import tkinter as tk
from PIL import Image, ImageTk

class BlackjackGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Blackjack Simulator")
        self.master.geometry("400x300")

        self.menu_frame = tk.Frame(master)
        self.menu_frame.pack(expand=True)

        # Main menu buttons
        self.start_button = tk.Button(self.menu_frame, text="Start Game", width=20, 
                                    command=self.initialize_game_window, font=("Arial", 14))
        self.start_button.pack(pady=20)

        self.config_button = tk.Button(self.menu_frame, text="Change Configuration", 
                                     width=20, command=self.show_config_dialog, font=("Arial", 14))
        self.config_button.pack(pady=20)

        # Initialize game components as None
        self.game_frame = None
        self.strategy_frame = None
        self.strategy_photo = None
        self.card_images = {}
        self.card_back = None


    def initialize_game_window(self):
        # Hide menu frame
        self.menu_frame.pack_forget()
        
        # Reset window size for game
        self.master.geometry("600x800")

        # Initialize game components
        self.strategy_visible = False
        
        # Main game frame and strategy chart frame
        self.game_frame = tk.Frame(self.master)
        self.game_frame.pack(side=tk.LEFT, padx=80)

        self.strategy_frame = tk.Frame(self.master)

        # Load Strategy image
        strategy_img = Image.open("media/strategy/BJA_Basic_Strategy.jpg")
        strategy_img = strategy_img.resize((400, 600))
        self.strategy_photo = ImageTk.PhotoImage(strategy_img)

        # Load config and deck
        with open("config.json", "r") as f:
            self.config = json.load(f)
        with open("data.txt", "rb") as f:
            self.data = pickle.load(f)

        self.money = self.config['starting_bankroll']
        self.bet_size = self.config['bet_size']
        self.deck = self.data['deck'].copy()
        self.deck_visual = self.data['deck_visual'].copy()

        self.create_gui_elements()

        self.start_game()

    def create_gui_elements(self):
        # Load card back image
        self.card_back = ImageTk.PhotoImage(Image.open("media/backs/red.png").resize((100, 145)))

        # Game state
        self.player_hand = []
        self.dealer_hand = []
        self.player_turn = True


        # GUI Elements
        self.info_label = tk.Label(self.game_frame, text="", font=("Arial", 12))
        self.info_label.pack(pady=10)

        self.dealer_label = tk.Label(self.game_frame, text="", font=("Arial", 14))
        self.dealer_label.pack(pady=10)


        # Create frames for card images
        self.dealer_cards_frame = tk.Frame(self.game_frame)
        self.dealer_cards_frame.pack(pady=10)
        
        self.player_cards_frame = tk.Frame(self.game_frame)
        self.player_cards_frame.pack(pady=10)


        self.player_label = tk.Label(self.game_frame, text="", font=("Arial", 14))
        self.player_label.pack(pady=10)
        

        self.money_label = tk.Label(self.game_frame, text="", font=("Arial", 12))
        self.money_label.pack(pady=10)

        self.button_frame = tk.Frame(self.game_frame)
        self.button_frame.pack(pady=20)

        self.hit_button = tk.Button(self.button_frame, text="Hit", width=10, command=self.hit)
        self.stand_button = tk.Button(self.button_frame, text="Stand", width=10, command=self.stand)
        self.surrender_button = tk.Button(self.button_frame, text="Surrender", width=10, command=self.surrender)
        self.double_down_button = tk.Button(self.button_frame, text="Double Down", width=10, command=self.double_down)

        self.continue_button = tk.Button(self.button_frame, text="Continue", width=22, command=self.next_round)
        self.exit_button = tk.Button(self.button_frame, text="Exit", width=10, command=self.exit_game)

        # Add strategy button in a separate frame
        self.strategy_button_frame = tk.Frame(self.game_frame)
        self.strategy_button_frame.pack(pady=10)
        
        self.strategy_button = tk.Button(self.strategy_button_frame, 
                                       text="Show Strategy", 
                                       width=15, 
                                       command=self.toggle_strategy)
        self.strategy_button.pack()
        
    def start_game(self):
        text = "" # Reset message text
        if self.money < self.bet_size:
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

    def show_config_dialog(self):
        # Create configuration dialog
        config_window = tk.Toplevel(self.master)
        config_window.title("Configuration")
        config_window.geometry("400x500")

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

        # Bet size
        tk.Label(config_window, text="Bet size:", font=("Arial", 12)).pack(pady=5)
        bet_entry = tk.Entry(config_window)
        bet_entry.pack(pady=5)

        # Surrender allowed
        surrender_var = tk.BooleanVar()
        tk.Checkbutton(config_window, text="Allow surrender", variable=surrender_var, 
                      font=("Arial", 12)).pack(pady=5)

        # Double down allowed
        double_var = tk.BooleanVar()
        tk.Checkbutton(config_window, text="Allow double down", variable=double_var, 
                      font=("Arial", 12)).pack(pady=5)

        # House stand
        tk.Label(config_window, text="House stands on:", font=("Arial", 12)).pack(pady=5)
        house_entry = tk.Entry(config_window)
        house_entry.pack(pady=5)

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
                'bet_size': int(bet_entry.get()),
                'is_surrender': surrender_var.get(),
                'is_double_down': double_var.get(),
                'house_stand': int(house_entry.get())
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

        # Only show surrender button if allowed in config
        if self.config['is_surrender']:
            self.surrender_button.pack(side=tk.LEFT, padx=10)

        # Only show double down if player has enough money AND if allowed in config
        if (self.money >= 2 * self.bet_size) and (self.config['is_double_down']):
            self.double_down_button.pack(side=tk.LEFT, padx=10)

    def hide_action_buttons(self):
        self.hit_button.pack_forget()
        self.stand_button.pack_forget()
        self.surrender_button.pack_forget()
        self.double_down_button.pack_forget()

    def show_continue_button(self):
        self.continue_button.pack(side=tk.LEFT, padx=10)
        self.exit_button.pack(side=tk.LEFT, padx=10)

    def hide_continue_buttons(self):
        self.continue_button.pack_forget()
        self.exit_button.pack_forget()

    def toggle_strategy(self):
        if self.strategy_visible:
            self.strategy_frame.pack_forget()
            self.master.geometry("600x800")
            self.strategy_button.config(text="Show Strategy")
            self.strategy_visible = False
        else:
            self.strategy_frame.pack(side=tk.RIGHT, padx=10)
            strategy_label = tk.Label(self.strategy_frame, image=self.strategy_photo)
            strategy_label.pack()
            self.master.geometry("1000x800")
            self.strategy_button.config(text="Hide Strategy")
            self.strategy_visible = True
     
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

    def stand(self):
        self.hide_action_buttons()
        self.dealer_play()

    def surrender(self):
        """Player surrenders and loses half the bet."""
        self.hide_action_buttons()
        loss_amount = self.bet_size / 2
        self.money -= loss_amount
        self.update_display(reveal_dealer=True, message=f"You surrendered. Lost {loss_amount}.")
        self.show_continue_button()

    def double_down(self):
        """Player doubles the bet, gets one card, and ends turn."""
        self.hide_action_buttons()
        original_bet = self.bet_size
        # self.money -= self.bet_size  # Deduct additional bet
        self.bet_size *= 2  # Double the bet size
        self.player_hand.append(self.deck.pop(0))
        self.player_hand_visual.append(self.deck_visual.pop(0))

        if sum(self.player_hand) > 21 and 11 in self.player_hand:
            self.player_hand[self.player_hand.index(11)] = 1  # Convert Ace from 11 to 1

        if sum(self.player_hand) > 21:
            self.update_display(reveal_dealer=True, message="Over 21. You lose!")
            self.money -= self.bet_size
            self.hide_action_buttons()
            self.bet_size = original_bet  # Reset bet size for next round
            self.show_continue_button()
        else:
            self.update_display()
            self.dealer_play()
            self.bet_size = original_bet  # Reset bet size for next round

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
            house_stand = int(input("House stands on (int, usually 17): "))
        else:
            with open("config.json", "r") as f:
                config = json.load(f)
                f.close()
            starting_bankroll = config['starting_bankroll']
            bet_size = config['bet_size']
            is_surrender = config['is_surrender']
            is_double_down = config['is_double_down']
            house_stand = config['house_stand']

        game_settings_dict = {'deck_size': len(custom_deck), 'is_balanced': is_balanced,
                            'starting_bankroll': starting_bankroll, 'bet_size': bet_size,
                            'is_surrender': is_surrender, 'is_double_down': is_double_down,
                            'house_stand': house_stand}

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

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()