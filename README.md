# Uno Bot

## Run the code

First, go to src/run.py. From there, you can choose what to do (play against the bot or train the bot).

## Introduction

Throughout my childhood, Uno has always been the go-to card game to play with my friends and family. Even going into my adulthood, I would occasionally play the mobile version of Uno. People always say ‘Uno is based on luck”. I agree, somewhat. However, a part of me believes that skills also matter. Sure, a lot of times you might only have one obvious play to make, and that does not require any skills. However, for times when there are multiple valid plays to choose from, I believe skills is what help you maximize your win rate. The more I ponder on this, the more I want to dive deeper into this topic. Therefore, for this project, I will be discovering an optimal strategy of playing Uno that could give you a win rate higher than 50% and to prove that Uno is in fact based on luck AND skills.

For this project, I will only be discovering an optimal strategy for playing against a player, a 1v1 Uno game. My project will consist of two parts: a game engine of the UNO card game, and using the game engine to train an agent to use an optimal strategy. For the game engine, I will be using Python to build it from scratch and use pygame to build a simple GUI. For the agent, it will be using the Q-learning algorithm to find an optimal strategy to play the game.

## Uno Game Engine

### Setup

The purpose of the game engine is so that it replicates how the actual game works and allow the agent to interact with the game like how humans do in real life. Just like the actual game, this game engine will include the same content as an actual UNO card deck would have. A card is represented as a tuple which includes the number (skip or reverse for special cards) and the color. For wild cards like Wild Change Color and Wild Draw Four, it will be represented like this: (‘Wild’, ‘Draw4’). The deck would just be a list that includes all the tuples described above.

### Rules

For simplifications, the game engine abides by the following rules:

1. Player can only play one card at a time, you cannot play multiple cards just because they have the same number
2. The reverse card is for changing the direction of the play. However, since this is a 1 versus 1, the reverse card technically does not do anything.
3. After playing Draw2 and Draw4, not only will your opponent draw the specified number of cards, their turn gets skipped as well.
4. Due to the previous rule, Draw2 and Draw4 cards cannot be stacked. They will each be registered by the game engine one by one.
5. When the player is on his/her last card, he/she does not need to call UNO.
6. If you don’t have any legal moves and draw from the deck, you cannot play the card you just drew from the deck in the same turn, even if its color or number matches the top card of the pile.

### Bot

In the game engine, I have created a bot to train the q-learning agent. For each of its turn, the bot will iterate through its hand and play the first legal move it sees. When it comes to playing wild cards and picking a color, it simply disregards its hand and randomly picks one of the four colors (i.e., red, blue, green, and yellow). If the bot does not have any legal moves to make, it will draw a card from the deck.
Interface
The game engine uses a simple and interactive text-based interface. The text-based interface shows all the essential components of the game, including whose turn it is, what card is on the top of the pile, cards remaining each turn, and the cards on the player’s hand. When a party draws from the deck, it will say so. When a party plays a special card, such as skip and draw2, it will indicate that the opposition’s turn has been skipped and/or the opposition has drawn two cards. For a wild card, such as draw4 or change color, it will indicate similar messages as the special card, and also indicate the color the player has changed to.

## State Space, Action Space, and Reward (SAR)

In the context of an UNO game, there are a couple of factors that we should capture at each state. These factors include but not limited to the number of regular cards, the number of special cards, the number of wild cards, the number of cards the player has on his hand, and the color and number of the top card of the pile. All of these factors could help the agent evaluate its current situation. However, it is not feasible to capture all the features of a player’s hand since the number of possible combination of cards in hand is immensely large. To simplify the problem and shrink the state space, I have narrowed down a couple of features that I believe are significant in assessing a state. These features include the current top card of the pile, the number of playable cards in hand, and the total number of cards in hand. To capture all this in a state, I will use a 11-tuple to represent each state like this:

State = (Color of the card, Card type (i.e., number, special, or wild), Red, Green, Blue, Yellow, Reverse, Skip, Draw2, Wild card, Total number of cards in hand)

The tuple captures the number of playable cards the player has in his hand given the current top card of the pile. This is essential to determine how favorable your hand is at this stage of the game. For example, if you don’t have a playable card given the top card, then the agent should learn that it would be a more unfavorable state. The limit the size of the state space, I have limited the highlighted part of the tuple to have a value of 0 or 1. I believe this is sufficient to capture how favorable, or unfavorable, one’s state is. To provide the agent a better understanding of the state, I have included the total number of cards in hand as the last tuple. This is crucial because ultimately, we want the agent to keep the total number of cards in hand as low as possible and eventually turn it to zero.

In terms of action space, it is straightforward. The agent can play a red card, a green card, a blue card, a yellow card, a skip card, a reverse card, a draw2 card, a draw4 card, or a change color card. Of course, we will make sure the agent acts within the rules of the game. We will discuss later how this will be done.

The goal of the game is to clear your hand as quickly as possible. In other words, we want the number of cards in hand to become zero. That said, we will initialize the reward table where states with no cards in hand (0 value in the last element of the tuple) will be given a reward of 1. This gives the q-learning agent a starting point to learn how other states compare relative to the ending states described in the reward table.

In the code, I have used external libraries like itertools and pandas to help me initialize SAR. itertools is used to initialize the state space, used for generating different combinations of 11-tuples that represent different possible states. pandas is used to create a dataframe to store the rewards of states described above. Refer to sar.py in the code for this section.

## Q-Learning Algorithm

Now that we have the state space, action space, and rewards figured out, I will be using the Q-learning algorithm to train the agent. Through Q-learning, the agent will develop a Q-table as it goes through training. The Q-table will store values in terms of state-action pairs. Specifically, it stores the q-value of different actions at different states. The purpose of the Q-table is so that the agent can exploit and pick the best action at a given state. However, it is also essential to consider when the agent should explore to find more and better exploitations. To address this, I will be using the epsilon-greedy method to determine when the agent explores and when it exploits. With epsilon probability, the agent will take a random action. On the other hand, with 1-epsilon probability, the agent will pick the action with the maximum q-value. That said, a higher epsilon probability would mean that the agent would explore more during training. When the agent explores (takes a random legal action), it will update the q-value using the Q-function.

The Q-function shows that q-values are dependent on the step-size (alpha), the reward of the next step (r), and the q-value and the next state and action (represented as s’ and a’). The alpha value controls how much the q-value increases at each iteration. A lower alpha value would allow the agent to get closer to the optimum but at a slower rate than a high alpha value.

In the code, the agent is given a state and a list of legal moves that it could make to update the Q-table and to decide what move to make. Refer to agent.py in the code for this section.
