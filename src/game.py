import random
import numpy as np
import pandas as pd

import agent as qlearning
import sar


class UnoGameEngine:

    def __init__(self, numPlayers=2):
        # this project focuses on an optimal strategy against one player
        self.numPlayers = numPlayers
        self.deck = []
        self.pile = []
        self.playerHand = []
        self.botHand = []
        self.turn = 0  # player plays on odd number, bot plays on even number
        self.color = None  # for wild cards (draw4 and change color)
        self.realPlayer = False
        q_table = pd.read_csv('csv/q-values.csv')
        self.q_table = q_table.copy()

    # start the game
    def reset(self):
        self.deck = []
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
        special_cards = [('Red', 'Skip'), ('Red', 'Reverse'), ('Red', 'Draw2'),
                         ('Blue', 'Skip'), ('Blue', 'Reverse'), ('Blue', 'Draw2'),
                         ('Green', 'Skip'), ('Green',
                                             'Reverse'), ('Green', 'Draw2'),
                         ('Yellow', 'Skip'), ('Yellow', 'Reverse'), ('Yellow', 'Draw2')] * 2

        # Wild cards (including Wild and Wild Draw Four)
        wild_cards = [('Wild', 'Cc'), ('Wild', 'Draw4',)] * 4

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

    # functions to check game state
    def legal_action(self, card_played):
        # it is a legal action if the card played matches the color or number/special action of the top card of the pile, or if it is a wild card
        return self.color == card_played[0] or self.pile[-1][1] == card_played[1] or card_played[0] == 'Wild'

    def hasWon(self, hand):
        return len(hand) == 0

    # functions for the agent to learn
    def currentState(self, hand):
        s_color = self.color
        if self.pile[-1][0] == 'Wild':
            s_type = 'Wild'
        elif self.pile[-1][1] == 'Skip' or self.pile[-1][1] == 'Reverse':
            s_type = 'Special'
        else:
            s_type = 'Number'
        r_playable = 0
        g_playable = 0
        b_playable = 0
        y_playable = 0
        sk_playable = 0
        rev_playable = 0
        d2_playable = 0
        w_playable = 0
        total = 0
        for c in hand:
            if self.legal_action(c):
                if c[0] == 'Red':
                    r_playable = 1
                elif c[0] == 'Green':
                    g_playable = 1
                elif c[0] == 'Blue':
                    b_playable = 1
                elif c[0] == 'Yellow':
                    y_playable = 1
                elif c[1] == 'Skip':
                    sk_playable = 1
                elif c[1] == 'Reverse':
                    rev_playable = 1
                elif c[1] == 'Draw2':
                    d2_playable = 1
                elif c[0] == 'Wild':
                    w_playable = 1
                else:
                    print('should not get here!')
                if total < 7:
                    total += 1
            else:
                if total < 7:
                    total += 1
        return (s_color, s_type, r_playable, g_playable, b_playable, y_playable, sk_playable, rev_playable, d2_playable, w_playable, total)

    def actionsForAgent(self, hand):
        actions = []
        for c in hand:
            if self.legal_action(c):
                # type actions
                if c[1] == "Cc":
                    actions.append(c[1])
                elif c[1] == 'Draw4':
                    actions.append('Draw4')
                elif c[1] == 'Draw2':
                    actions.append('Draw2')
                elif c[1] == 'Reverse':
                    actions.append('Reverse')
                elif c[1] == 'Skip':
                    actions.append('Skip')
                else:
                    pass

                # color actions
                if c[0] == 'Red':
                    actions.append('Red')
                elif c[0] == 'Green':
                    actions.append('Green')
                elif c[0] == 'Blue':
                    actions.append('Blue')
                elif c[0] == 'Yellow':
                    actions.append('Yellow')
        return actions

    def play_agent(self, card_played, player):
        r = 0
        g = 0
        b = 0
        y = 0
        changeTo = None
        if self.legal_action(card_played):
            if player == 'Player':
                self.playerHand.remove(card_played)
            else:
                self.botHand.remove(card_played)
            self.pile.append(card_played)
            # switch cases of all the possible special cards played
            if card_played[1] == 'Skip':
                self.skipTurn()
                self.color = card_played[0]
            elif card_played[1] == 'Draw2':
                if len(self.deck) > 2:
                    # player played the card
                    if self.turn % 2 == 0:
                        self.drawTwo('Bot')
                        self.color = card_played[0]
                    else:  # bot played the card
                        self.drawTwo('Player')
                        self.color = card_played[0]
                else:
                    self.deck.clear()
            elif card_played[1] == 'Draw4':
                if len(self.deck) > 4:
                    hand = self.playerHand
                    if player == 'ai':
                        hand = self.botHand
                    for c in hand:
                        if c[0] == 'Red':
                            r += 1
                        elif c[0] == 'Blue':
                            b += 1
                        elif c[0] == 'Green':
                            g += 1
                        elif c[0] == "Yellow":
                            y += 1
                    if r == max(r, g, b, y):
                        changeTo = 'Red'
                    elif g == max(r, g, b, y):
                        changeTo = 'Green'
                    elif y == max(r, g, b, y):
                        changeTo = 'Yellow'
                    elif b == max(r, g, b, y):
                        changeTo = 'Blue'
                    if self.realPlayer:
                        self.drawFour('Player', changeTo)
                        self.color = changeTo
                    else:
                        self.drawFour('bot', changeTo)
                        self.color = changeTo
                else:
                    self.deck.clear()
            elif card_played[1] == 'Cc':
                hand = self.playerHand
                if player == 'ai':
                    hand = self.botHand
                for c in hand:
                    if c[0] == 'Red':
                        r += 1
                    elif c[0] == 'Blue':
                        b += 1
                    elif c[0] == 'Green':
                        g += 1
                    elif c[0] == "Yellow":
                        y += 1
                if r == max(r, g, b, y):
                    changeTo = 'Red'
                elif g == max(r, g, b, y):
                    changeTo = 'Green'
                elif y == max(r, g, b, y):
                    changeTo = 'Yellow'
                elif b == max(r, g, b, y):
                    changeTo = 'Blue'

                self.changeColor(changeTo)
                self.color = changeTo
            else:
                self.color = card_played[0]
            return True

    # action functions
    def draw(self, player):
        if player == 'Player':
            random_card = random.choice(self.deck)
            # Remove the drawn card from the deck
            self.deck.remove(random_card)
            self.playerHand.append(random_card)
        else:
            random_card = random.choice(self.deck)
            # Remove the drawn card from the deck
            self.deck.remove(random_card)
            self.botHand.append(random_card)

    def play(self, card_played, player):
        if self.legal_action(card_played):
            if player == 'Player':
                self.playerHand.remove(card_played)
            else:
                self.botHand.remove(card_played)
            self.pile.append(card_played)
            self.color = card_played[0]
            # switch cases of all the possible special cards played
            if card_played[1] == 'Skip':
                self.skipTurn()
            elif card_played[1] == 'Draw2':
                if len(self.deck) > 2:
                    # player played the card
                    if self.turn % 2 == 0:
                        self.drawTwo('Bot')
                    else:  # bot played the card
                        self.drawTwo('Player')
                else:
                    self.deck.clear()
            elif card_played[1] == 'Draw4':
                if len(self.deck) > 4:
                    # player played the card
                    if self.turn % 2 == 0:
                        changeTo = input(
                            "Pick a color (Red, Green, Blue or Yellow): ")
                        self.drawFour('Bot', changeTo)
                    else:  # bot played the card
                        # change to random for dummy bot
                        colors = ["Red", "Blue", "Yellow", "Green"]
                        self.drawFour('Player', random.choice(colors))
                else:
                    self.deck.clear()
            elif card_played[1] == 'Cc':
                if self.turn % 2 == 0:
                    changeTo = input(
                        "Pick a color (Red, Green, Blue or Yellow): ")
                    self.changeColor(changeTo)
                else:
                    # change to random color for dummy bot
                    colors = ["Red", "Blue", "Yellow", "Green"]
                    self.changeColor(random.choice(colors))
            return True

        else:
            print("Not a legal move, try again!")
            action = input(
                "What are you going to play (Please type your card in the format of Color Number): ")
            if action == 'D' or action == 'd' or action == 'Draw' or action == 'draw':
                self.draw("player")
            else:
                newAction = action.split(" ")

                if len(newAction) == 2:
                    self.play((newAction[0].capitalize(),
                               newAction[1].capitalize()), 'Player')
                else:
                    self.play((newAction[0].capitalize(), ), 'Player')

    # special card effects - draw2, skip ,draw4, and cc. reverse is neglected because it doesn't do anything in a 1v1 game
    def drawTwo(self, player):
        if self.realPlayer:
            print(f"{player} draw two cards and skip a turn!")
        self.draw(player)
        self.draw(player)
        self.turn += 1

    def drawFour(self, player, color):
        if color.capitalize() in ['Red', 'Yellow', 'Green', 'Blue']:
            if self.realPlayer:
                print(f"{player} draw 4 cards and skip a turn")
            self.draw(player)
            self.draw(player)
            self.draw(player)
            self.draw(player)
            self.turn += 1
            self.color = color.capitalize()
            if self.realPlayer:
                print("Color changed to: ", self.color)
        else:
            newColor = input(
                "Invalid color, try again (Pick either Red, Yellow, Green, or Blue): ")
            self.drawFour(player, newColor)

    def changeColor(self, color):
        if color.capitalize() in ['Red', 'Yellow', 'Green', 'Blue']:
            self.color = color.capitalize()
            if self.realPlayer:
                print("Color changed to: ", self.color)
        else:
            newColor = input(
                "Invalid color, try again (Pick either Red, Yellow, Green, or Blue): ")
            self.changeColor(newColor)

    def skipTurn(self):
        if self.realPlayer:
            print("Skipped!")
        self.turn += 1

    # dummy bot, play randomly
    def botPlay(self):
        hasPlayed = False
        for c in self.botHand:
            if self.legal_action(c):
                self.play(c, 'Bot')
                hasPlayed = True
                break

        # went through the entire hand and has no possible legal action
        if not hasPlayed:
            self.draw('Bot')
            if self.realPlayer:
                print("Bot has drawn")
            hasPlayed = True

    # run game function (real player)
    def run_player(self):
        self.realPlayer = True
        ended = False
        players = ['player', 'bot']
        # for displaying the actual number of turns (self.turn is used to track whose turn it is, not the actual number of turns)
        currentTurn = 0
        whoStarts = random.choice(players)
        if whoStarts == 'bot':
            currentTurn = 1
            self.turn = 1
        self.reset()
        startingCard = random.choice(self.deck)
        self.deck.remove(startingCard)
        self.pile.append(startingCard)
        print("Starting Card: ", startingCard)
        while startingCard[0] == 'Wild':
            startingCard = random.choice(self.deck)
            self.deck.remove(startingCard)
            self.pile.append(startingCard)
            print("Starting Card: ", startingCard)

        self.color = startingCard[0]
        print()

        while not ended:
            # player's turn to play
            if self.turn % 2 == 0:
                print(f"{currentTurn}: Player's Turn")
                print("Player's Hand: ", self.playerHand)
                action = input(
                    "What are you going to play (Please type it in this format: Color Number): ")

                if action == 'D' or action == 'd' or action == 'Draw' or action == 'draw':
                    self.draw("Player")
                    print(f"Cards remaining: {len(self.playerHand)}")
                    currentTurn += 1
                    self.turn += 1
                    print()
                else:
                    card_played = action.split(' ')
                    if len(card_played) == 2:
                        self.play(
                            (card_played[0].capitalize(), card_played[1].capitalize()), "Player")
                        print(f"Cards remaining: {len(self.playerHand)}")
                        print("Top card of the pile: ", self.pile[-1])
                        print()
                        currentTurn += 1
                        self.turn += 1
                    else:
                        self.play((card_played[0].capitalize(), ), "Player")
                        print(f"Cards remaining: {len(self.playerHand)}")
                        print("Top card of the pile: ", self.pile[-1])
                        print()
                        currentTurn += 1
                        self.turn += 1
                    if self.hasWon(self.playerHand):
                        print('Player has won!')
                        ended = True
            # bot's turn to play
            else:
                print(f"{currentTurn}: Bot's turn")
                self.botPlay()
                currentTurn += 1
                self.turn += 1
                print(f"Cards remaining: {len(self.botHand)}")
                print("Top card of the pile: ", self.pile[-1])
                print()
                if self.hasWon(self.botHand):
                    print('Bot has won!')
                    ended = True

            if len(self.deck) == 0:
                print("Game ended with a tie")
                ended = True

    # run game function (agent training)
    def run_agent(self, iterations):
        agent = qlearning.QLearningAgent()
        players = ['ai', 'bot']

        for i in range(iterations):
            print(i)
            ended = False
            # for displaying the actual number of turns (self.turn is used to track whose turn it is, not the actual number of turns)
            currentTurn = 0
            whoStarts = random.choice(players)
            if whoStarts == 'bot':
                currentTurn = 1
                self.turn = 1
            self.reset()
            startingCard = random.choice(self.deck)
            self.deck.remove(startingCard)
            self.pile.append(startingCard)
            print("Starting Card: ", startingCard)
            while startingCard[0] == 'Wild':
                startingCard = random.choice(self.deck)
                self.deck.remove(startingCard)
                self.pile.append(startingCard)
                print("Starting Card: ", startingCard)

            self.color = startingCard[0]
            print()
            while not ended:
                # ai's turn to play
                if self.turn % 2 == 0:
                    print(f"{currentTurn}: Agent's Turn")
                    print("Agent's Hand: ", self.playerHand)
                    print(f"Cards remaining: {len(self.playerHand)}")
                    actions = self.actionsForAgent(
                        self.playerHand)  # all possible legal moves
                    state = self.currentState(self.playerHand)
                    if len(actions) == 0:
                        self.draw("Player")
                        currentTurn += 1
                        self.turn += 1
                        print()
                    else:
                        action = agent.choose_action(state, actions)
                        card_played = None

                        if len(action) > 1:
                            action = random.choice(actions)  # explore
                            for c in self.playerHand:
                                if action == 'Red' or action == 'Green' or action == 'Blue' or action == 'Yellow':
                                    if self.legal_action(c) and c[0] == action:
                                        card_played = c
                                else:
                                    if self.legal_action(c) and c[1] == action:
                                        card_played = c
                        else:
                            for c in self.playerHand:
                                if action == 'Red' or action == 'Green' or action == 'Blue' or action == 'Yellow':
                                    if self.legal_action(c) and c[0] == action:
                                        card_played = c
                                else:
                                    if self.legal_action(c) and c[1] == action:
                                        card_played = c

                        if len(card_played) == 2:
                            self.play_agent(
                                (card_played[0].capitalize(), card_played[1].capitalize()), "Player")
                            print("Top card of the pile: ", self.pile[-1])
                            print()
                            agent.update_q_table(state, action)
                            currentTurn += 1
                            self.turn += 1
                        else:
                            self.play_agent(
                                (card_played[0].capitalize(), ), "Player")
                            print("Top card of the pile: ", self.pile[-1])
                            print()
                            agent.update_q_table(state, action)
                            currentTurn += 1
                            self.turn += 1
                        if self.hasWon(self.playerHand):
                            print('Agent has won!')
                            ended = True
                # bot's turn to play
                else:
                    print(f"{currentTurn}: Bot's turn")
                    print("Bot's Hand: ", self.botHand)
                    print(f"Cards remaining: {len(self.botHand)}")
                    self.botPlay()
                    currentTurn += 1
                    self.turn += 1
                    print(f"Cards remaining after play: {len(self.botHand)}")
                    print("Top card of the pile: ", self.pile[-1])
                    print()
                    if self.hasWon(self.botHand):
                        print('Bot has won!')
                        ended = True

                if len(self.deck) == 0:
                    print("Game ended with a tie")
                    ended = True

        print(agent.q_table)
        agent.q_table.to_csv("csv/q-values.csv", index=True)

    # run game function (agent training without print statements)
    def run_agent_train(self, iterations):
        results = []
        ai = 0
        bot = 0
        agent = qlearning.QLearningAgent()
        players = ['ai', 'bot']

        for i in range(iterations):
            if i % 100 == 0:
                print(i)

            result = []
            ended = False
            # for displaying the actual number of turns (self.turn is used to track whose turn it is, not the actual number of turns)
            currentTurn = 0
            whoStarts = random.choice(players)
            if whoStarts == 'bot':
                currentTurn = 1
                self.turn = 1
            self.reset()
            startingCard = random.choice(self.deck)
            self.deck.remove(startingCard)
            self.pile.append(startingCard)

            while startingCard[0] == 'Wild':
                startingCard = random.choice(self.deck)
                self.deck.remove(startingCard)
                self.pile.append(startingCard)

            self.color = startingCard[0]
            while not ended:
                # ai's turn to play
                if self.turn % 2 == 0:
                    actions = self.actionsForAgent(
                        self.playerHand)  # all possible legal moves
                    stateForAction = self.currentState(self.playerHand)
                    if len(actions) == 0:
                        self.draw("Player")
                        currentTurn += 1
                        self.turn += 1
                    else:
                        action = agent.choose_action(stateForAction, actions)
                        card_played = None

                        for c in self.playerHand:
                            if action == 'Red' or action == 'Green' or action == 'Blue' or action == 'Yellow':
                                if self.legal_action(c) and c[0] == action:
                                    card_played = c
                            else:
                                if self.legal_action(c) and c[1] == action:
                                    card_played = c

                        if len(card_played) == 2:
                            self.play_agent(
                                (card_played[0].capitalize(), card_played[1].capitalize()), "Player")
                            state = self.currentState(self.playerHand)
                            agent.update_q_table(state, action)
                            currentTurn += 1
                            self.turn += 1
                        else:
                            self.play_agent(
                                (card_played[0].capitalize(), ), "Player")
                            state = self.currentState(self.playerHand)
                            agent.update_q_table(state, action)
                            currentTurn += 1
                            self.turn += 1
                        if self.hasWon(self.playerHand):
                            ai += 1
                            result.append('AI')
                            result.append(currentTurn)
                            result.append(ai/(i + 1))
                            ended = True
                # bot's turn to play
                else:
                    self.botPlay()
                    currentTurn += 1
                    self.turn += 1
                    if self.hasWon(self.botHand):
                        bot += 1
                        result.append('Bot')
                        result.append(currentTurn)
                        result.append(bot/(i + 1))
                        ended = True

                if len(self.deck) == 0:
                    ended = True

            results.append(result)

        agent.q_table.to_csv("csv/q-values.csv", index=True)
        record = pd.DataFrame(results, columns=['Winner', 'Turns', 'Win_Rate'])
        record.to_csv("csv/records.csv", index=True)

    def run_AI(self):
        self.realPlayer = True
        agent = qlearning.QLearningAgent()
        ended = False
        players = ['player', 'ai']
        # for displaying the actual number of turns (self.turn is used to track whose turn it is, not the actual number of turns)
        currentTurn = 0
        whoStarts = random.choice(players)
        if whoStarts == 'ai':
            currentTurn = 1
            self.turn = 1
        self.reset()
        startingCard = random.choice(self.deck)
        self.deck.remove(startingCard)
        self.pile.append(startingCard)
        print("Starting Card: ", startingCard)
        while startingCard[0] == 'Wild':
            startingCard = random.choice(self.deck)
            self.deck.remove(startingCard)
            self.pile.append(startingCard)
            print("Starting Card: ", startingCard)

        self.color = startingCard[0]
        print()

        while not ended:
            # player's turn to play
            if self.turn % 2 == 0:
                print(f"{currentTurn}: Player's Turn")
                print("Player's Hand: ", self.playerHand)
                action = input(
                    "What are you going to play (Please type it in this format: Color Number): ")

                if action == 'D' or action == 'd' or action == 'Draw' or action == 'draw':
                    self.draw("Player")
                    print("Top card of the pile: ", self.pile[-1])
                    print(f"Cards remaining: {len(self.playerHand)}")
                    currentTurn += 1
                    self.turn += 1
                    print()
                else:
                    card_played = action.split(' ')
                    if len(card_played) == 2:
                        self.play(
                            (card_played[0].capitalize(), card_played[1].capitalize()), "Player")
                        print("Top card of the pile: ", self.pile[-1])
                        print(f"Cards remaining: {len(self.playerHand)}")
                        print()
                        currentTurn += 1
                        self.turn += 1
                    else:
                        self.play((card_played[0].capitalize(), ), "Player")
                        print("Top card of the pile: ", self.pile[-1])
                        print(f"Cards remaining: {len(self.playerHand)}")
                        print()
                        currentTurn += 1
                        self.turn += 1
                    if self.hasWon(self.playerHand):
                        print('Player has won!')
                        ended = True
            # ai's turn to play
            else:
                print(f"{currentTurn}: Agent's Turn")
                actions = self.actionsForAgent(
                    self.botHand)  # all possible legal moves
                state = self.currentState(self.botHand)
                if len(actions) == 0:
                    self.draw("ai")
                    print('AI has drawn')
                    print("Top card of the pile: ", self.pile[-1])
                    print(f"Cards remaining: {len(self.botHand)}")
                    currentTurn += 1
                    self.turn += 1
                    print()
                else:
                    action = agent.choose_action(state, actions)
                    card_played = None

                    for c in self.botHand:
                        if action == 'Red' or action == 'Green' or action == 'Blue' or action == 'Yellow':
                            if self.legal_action(c) and c[0] == action:
                                card_played = c
                        else:
                            if self.legal_action(c) and c[1] == action:
                                card_played = c

                    if len(card_played) == 2:
                        self.play_agent(
                            (card_played[0].capitalize(), card_played[1].capitalize()), "ai")
                        print("Top card of the pile: ", self.pile[-1])
                        print(f"Cards remaining: {len(self.botHand)}")
                        print()
                        agent.update_q_table(state, action)
                        currentTurn += 1
                        self.turn += 1
                    else:
                        self.play_agent(
                            (card_played[0].capitalize(), ), "ai")
                        print("Top card of the pile: ", self.pile[-1])
                        print(f"Cards remaining: {len(self.botHand)}")
                        print()
                        agent.update_q_table(state, action)
                        currentTurn += 1
                        self.turn += 1
                    if self.hasWon(self.botHand):
                        print('Agent has won!')
                        ended = True

            if len(self.deck) == 0:
                print("Game ended with a tie")
                ended = True
