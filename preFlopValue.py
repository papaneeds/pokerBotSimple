import treys
import partialDeck

# This function calculates the pre-flop odds of p1_hand having the 
# currently winning hand in a numPlayerss table after numBoardCards are dealt.
# The odds are calcualted by drawing numIterations hands.
# 
def getOdds(p1_hand, # The hole cards
            numIterations, # The number of iterations to run the simulation for
            numPlayers, # The number of players in the hand
            numBoardCards # The number of board cards 
            ):

    debug = False

    # pretend you are playing with n random players 
    # for numIterations hands with numBoardCards
    evaluator = treys.Evaluator()
    winner = [0] * numPlayers
    for j in range (0, numIterations):
        # create the partial deck that excludes your cards
        pDeck = partialDeck.PartialDeck(p1_hand)
        
        # create the hands.
        # By convention your hand is in index=0
        hands = []
        hands.append(p1_hand)
        for i in range(1, numPlayers):
            hands.append(pDeck.draw(2))
            
        # Now, draw the board cards
        boardCards = pDeck.draw(numBoardCards)
        if (debug):
            print("Board cards=")
            treys.Card.print_pretty_cards(boardCards)
            
        numTies = findWinners(debug,
                              evaluator, numPlayers, hands, boardCards, winner)

    for i in range(0, numPlayers):
        winner[i] /= numIterations

    return winner
