import random
import json
import pickle

def change_config():
    """Function to change the game configuration, and then store these in config.json and data.txt."""
    print("Changing configuration...\n")

    deck_change = input("Make changes to deck? (y/n) ")
    if deck_change.lower() == 'y':
        standard_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4

        pool_multiple = int(input("Pool size (multiples of std deck) (int): "))
        deck_size = int(input("Deck size (int): "))
        is_balanced = input("Balanced deck? (y/n): ").lower() == 'y'
        print("\n")

        pool = pool_multiple * standard_deck

        custom_deck = build_deck(pool, deck_size, is_balanced)

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
        house_stand = int(input("House stands on (int, usually 17): "))
    else:
        with open("config.json", "r") as f:
            config = json.load(f)
            f.close()
        starting_bankroll = config['starting_bankroll']
        bet_size = config['bet_size']
        is_surrender = config['is_surrender']
        house_stand = config['house_stand']


    game_settings_dict = {'deck_size': len(custom_deck), 'is_balanced': is_balanced,
                          'starting_bankroll': starting_bankroll, 'bet_size': bet_size,
                          'is_surrender': is_surrender, 'house_stand': house_stand}

    data_dict = {'deck': custom_deck}

    with open("config.json", "w") as f:
        json.dump(game_settings_dict, f)
        f.close()

    with open("data.txt", "wb") as f:
        pickle.dump(data_dict, f)
        f.close()

    print("\n")
    print("Changes saved.\n")



def build_deck(pool, build_size, is_balanced):
    """Builds a deck of cards based on the chosen cards and balance preference."""
    custom_deck = [0] * build_size # Initialize empty deck
    if is_balanced:
        remaining_empty_slots = build_size # Total slots in the custom deck which is empty
        running_count = 0
        for i in range(build_size):
            random_index = random.randint(0, len(pool)-1)
            custom_deck[i] = pool[random_index]
            if pool[random_index] <= 6:
                running_count = running_count + 1
                remaining_empty_slots = remaining_empty_slots - 1
            elif pool[random_index] >= 10:
                running_count = running_count - 1
                remaining_empty_slots = remaining_empty_slots - 1
            else:
                remaining_empty_slots = remaining_empty_slots - 1 # Neutral cards

            pool.pop(random_index)  # Remove to avoid duplicates


            # Adjust the deck to be balanced
            if abs(running_count) > remaining_empty_slots:

                # Fill this 1 slot with neutral card. This ensures that the deck can be balanced (no odd numbers).
                random_index = random.randint(0, len(pool)-1)
                while pool[random_index] >= 10 or pool[random_index] <= 6: #  Avoid high and low cards 
                    random_index = random.randint(0, len(pool)-1)

                custom_deck[i] = pool[random_index]
                pool.pop(random_index)  # Remove to avoid duplicates
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
                    random_index = random.randint(0, len(pool)-1)
                custom_deck[j] = pool[random_index]
                pool.pop(random_index)  # Remove to avoid duplicates
        elif running_count > 0:
            for j in range(i_note, build_size):
                random_index = random.randint(0, len(pool)-1)
                while pool[random_index] <= 9: # Avoid low and neutral cards
                    pool.pop(random_index) # Remove unwanted cards to reduce pool size for performance
                    random_index = random.randint(0, len(pool)-1)
                custom_deck[j] = pool[random_index]
                pool.pop(random_index)  # Remove to avoid duplicates


        random.shuffle(custom_deck) # Shuffle the deck as last operation. This ensures randomness (for balanced decks)

    else:
        for i in range(build_size):
            random_index = random.randint(0, len(pool)-1)
            custom_deck[i] = pool[random_index]
            pool.pop(random_index)  # Remove to avoid duplicates


    return custom_deck


