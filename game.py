import random
import numpy as np


class UnoGameEngine:

    def __init__(self, numPlayers=2):
        # this project focuses on an optimal strategy against one player
        self.numPlayers = numPlayers
        self.deck = []
        self.pile = []
        self.playerHand = []
        self.botHand = []

    # start the game
    def reset(self):
        # Normal number cards in each color (0-9)
        number_cards = [('Red', '1'), ('Red', '2'), ('Red', '3'), ('Red', '4'), ('Red', '5'), ('Red', '6'), ('Red', '7'), ('Red', '8'), ('Red', '9'),
                        ('Blue', '1'), ('Blue', '2'), ('Blue', '3'), ('Blue',
                                                                      '4'), ('Blue', '5'), ('Blue', '6'), ('Blue', '7'), ('Blue', '8'), ('Blue', '9'),
                        ('Green', '1'), ('Green', '2'), ('Green', '3'), ('Green',
                                                                         '4'), ('Green', '5'), ('Green', '6'), ('Green', '7'), ('Green', '8'), ('Green', '9'),
                        ('Yellow', '1'), ('Yellow', '2'), ('Yellow', '3'), ('Yellow', '4'), ('Yellow', '5'), ('Yellow', '6'), ('Yellow', '7'), ('Yellow', '8'), ('Yellow', '9')] * 2
        number_cards = number_cards + \
            [('Red', '0')] + [('Blue', '0')] + \
            [('Green', '0')] + [('Yellow', '0')]

        # Special action cards in each color
        special_cards = [('Red', 'Skip'), ('Red', 'Reverse'), ('Red', 'Draw Two'),
                         ('Blue', 'Skip'), ('Blue', 'Reverse'), ('Blue', 'Draw Two'),
                         ('Green', 'Skip'), ('Green',
                                             'Reverse'), ('Green', 'Draw Two'),
                         ('Yellow', 'Skip'), ('Yellow', 'Reverse'), ('Yellow', 'Draw Two')] * 2

        # Wild cards (including Wild and Wild Draw Four)
        wild_cards = [('Wild',), ('Wild Draw Four',)] * 4

        self.deck = number_cards + special_cards + wild_cards

        # initial draw for each players
        for _ in range(7):
            random_card = random.choice(self.deck)
            # Remove the randomly picked card from the deck
            self.deck.remove(random_card)
            self.playerHand.append(random_card)
            random_card1 = random.choice(self.deck)
            # Remove the randomly picked card from the deck
            self.deck.remove(random_card1)
            self.botHand.append(random_card1)

        # start the game by drawing a random card from the deck to the pile
        starting_card = random.choice(self.deck)
        # Remove the randomly picked card from the deck
        self.deck.remove(starting_card)
        self.pile.append(starting_card)

    def legal_action(self, card_played):
        # it is a legal action if the card played matches the color or number/special action of the top card of the pile, or if it is a wild card
        return self.pile[-1][0] == card_played[0] or self.pile[-1][1] == card_played[1] or card_played[0] == 'Wild' or card_played[0] == 'Wild Draw Four'

    def draw(self, player):
        if player == 'player':
            random_card = random.choice(self.deck)
            # Remove the drawn card from the deck
            self.deck.remove(random_card)
            self.playerHand.append(random_card)
        else:
            random_card = random.choice(self.deck)
            # Remove the drawn card from the deck
            self.deck.remove(random_card)
            self.botHand.append(random_card)

    def play(self, card_played):
        if self.legal_action(card_played):
            self.playerHand.remove(card_played)
            self.pile.append(card_played)
            return True

        else:
            print("Not a legal move, try again!")
            action = input(
                "What are you going to play (Please type your card in the format of (Color, Number)): ")
            self.play(tuple(action))

    def hasWon(self, hand):
        return len(hand) == 0

    # dummy bot, play randomly

    def botPlay(self):
        hasPlayed = False
        for c in self.botHand:
            if self.legal_action(c):
                self.botHand.remove(c)
                self.pile.append(c)
                hasPlayed = True
                break

        # went through the entire hand and has no possible legal action
        if not hasPlayed:
            self.draw('bot')
            hasPlayed = True

    def currentInfo(self):
        print("Player's Hand: ", self.playerHand)
        print(f"Cards remaining: {len(self.playerHand)}")
        print("Top card of the pile: ", self.pile[-1])

    def run(self):
        ended = False
        players = ['player', 'bot']
        turn = 0
        whoStarts = random.choice(players)
        if whoStarts == 'player':
            turn = 0
        else:
            turn = 1
        self.reset()

        while not ended:
            # player's turn to play
            if turn % 2 == 0:
                print(f"{turn}: Player's Turn")
                self.currentInfo()
                action = input(
                    "What are you going to play (Please type it in this format: Color Number): ")
                turn += 1
                if action == 'D' or action == 'd' or action == 'Draw' or action == 'draw':
                    self.draw("player")
                else:
                    card_played = action.split(' ')
                    self.play((card_played[0], card_played[1]))
                    if self.hasWon(self.playerHand):
                        print('Player has won!')
                        ended = True
            # bot's turn to play
            else:
                print(f"{turn}: Bot's turn")
                self.botPlay()
                turn += 1
                print(f"Cards remaining: {len(self.botHand)}")
                print("Top card of the pile: ", self.pile[-1])
                if self.hasWon(self.playerHand):
                    print('Bot has won!')
                    ended = True


game = UnoGameEngine()
game.run()
