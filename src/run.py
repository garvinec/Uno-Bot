import game


def main():
    run = game.UnoGameEngine()
    # run.run_AI()  # play against trained agent
    # run.run_player()  # play against dummy bot
    run.run_agent_train(3000)
    # run.run_agent(200)  # includes text ui while training. recommend run_agent_train for high number of simulations


main()
