import json
import pickle
from utility_funcs import change_config
import random



while True:
    print("Review game config:")

    with open("config.json", "r") as f:
        config = json.load(f)
        f.close()

    print(config)
    print("\n")

    if input("Make changes to settings? (y/n) ").lower() == 'y':
        change_config()
    else:
        break

print("Starting game...")

with open("config.json", "r") as f:
            config = json.load(f)
            f.close()
with open("data.txt", "rb") as f:
            data = pickle.load(f)
            f.close()


money = config['starting_bankroll']
custom_deck = data['deck'].copy()
bet_size = config['bet_size']
while True:
    if money < bet_size:
        print("You don't have enough money to continue playing. Game over nigga.")
        break
    if len(custom_deck) < 20:
        print("Low on cards, Reshuffling the deck...")
        custom_deck = data['deck'].copy()
        random.shuffle(custom_deck)

    player_hand = []
    dealer_hand = []

    # Give first 2 cards for both player and dealer.
    player_hand.append(custom_deck[0])
    custom_deck.pop(0)

    dealer_hand.append(custom_deck[0])
    custom_deck.pop(0)

    player_hand.append(custom_deck[0])
    custom_deck.pop(0)

    dealer_hand.append(custom_deck[0])
    custom_deck.pop(0)

    if sum(player_hand) > 21:
                if 11 in player_hand:
                    player_hand[player_hand.index(11)] = 1

                    print("Dealer hand: ")
                    print(f"[?, {', '.join(map(str, dealer_hand[1:]))}]")

                    print("\n")
                    print("\n")

                    print("Player hand: ")
                    print(player_hand)
    else:
        print("Dealer hand: ")
        print(f"[?, {', '.join(map(str, dealer_hand[1:]))}]")


        print("\n")
        print("\n")

        print("Player hand: ")
        print(player_hand)

    # This bool is checked whether the player continues hittinging or not
    player_turn = True

    while player_turn == True:
        player_move = input("Hit or Stay? (h/s): ")
        if player_move.lower() == 'h':
            player_hand.append(custom_deck[0])
            custom_deck.pop(0)

            if sum(player_hand) > 21:
                if 11 in player_hand:
                    player_hand[player_hand.index(11)] = 1

                    print("Dealer hand: ")
                    print(f"[?, {', '.join(map(str, dealer_hand[1:]))}]")

                    print("\n")
                    print("\n")

                    print("Player hand: ")
                    print(player_hand)

                else:
                    print("Dealer hand: ")
                    print(dealer_hand)

                    print("\n")
                    print("\n")

                    print("Player hand: ")
                    print(player_hand)

                    print("Over 21. You lose!")
                    money = money - bet_size
                    print("Money: " + str(money))
                    break
            else:
                print("Dealer hand: ")
                print(f"[?, {', '.join(map(str, dealer_hand[1:]))}]")

                print("\n")
                print("\n")

                print("Player hand: ")
                print(player_hand)

        elif player_move.lower() == 's':
            if sum(dealer_hand) > 21: # This can only happen when dealer gets two aces at start.
                 dealer_hand[dealer_hand.index(11)] = 1

            print("Dealer hand: ")
            print(dealer_hand)

            print("\n")
            print("\n")

            print("Player hand: ")
            print(player_hand)

            player_turn = False
    
    while player_turn == False:
        if sum(dealer_hand) < config['house_stand']:
            dealer_hand.append(custom_deck[0])
            custom_deck.pop(0)


            if sum(dealer_hand) > 21:
                if 11 in dealer_hand:
                    dealer_hand[dealer_hand.index(11)] = 1

                    print("Dealer hand: ")
                    print(dealer_hand)

                    print("\n")
                    print("\n")

                    print("Player hand: ")
                    print(player_hand)
                else:
                    print("Dealer hand: ")
                    print(dealer_hand)

                    print("\n")
                    print("\n")

                    print("Player hand: ")
                    print(player_hand)

                    print("Dealer busts. You win!")
                    money = money + bet_size
                    print("Money: " + str(money))
                    break
            else:
                print("Dealer hand: ")
                print(dealer_hand)

                print("\n")
                print("\n")

                print("Player hand: ")
                print(player_hand)
        else:
            if sum(dealer_hand) > sum(player_hand):
                print("You lose!")
                money = money - bet_size
                print("Money: " + str(money))
                break
            elif sum(dealer_hand) < sum(player_hand):
                print("You win!")
                money = money + bet_size
                print("Money: " + str(money))
                break
            elif sum(dealer_hand) == sum(player_hand):
                print("Push. No one wins.")
                print("Money: " + str(money))
                break
    
    
    
    
    continue_prompt = input("Continue playing? (y/n): ")
    if continue_prompt == 'n':
        break

print("Game finished. Money at the end: " + str(money))

