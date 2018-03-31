import treys
import partialDeck
import operator

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
                
        # Now, figure out who has the best hand
        rankedHands = {}
        for i in range(0, numPlayers):
            if (debug):
                print("Player %d cards=" % (i))
                treys.Card.print_pretty_cards(hands[i])
            rank_score = evaluator.evaluate(hands[i], boardCards)
            rank_class = evaluator.get_rank_class(rank_score)
            if (debug):
                print("Player %d hand rank = %d (%s)\n" % (i, rank_score, evaluator.class_to_string(rank_class)))
            rankedHands[i]=rank_score
                
        # Now, sort the rankedHands based on rank score
        sortedRankedHands = sorted(rankedHands.items(), 
                                   key=operator.itemgetter(1))
                        
        # Print out who won
        if (debug):
            print("Player=", sortedRankedHands[0][0], " wins")
                            
        # There could be a tie amongst one or more players. In that
        # case they all get a win
        tie = False  
        numTies = 0
        for i in range(1, numPlayers):
            if (sortedRankedHands[i][1] == sortedRankedHands[0][1]):
                # we have a tie
                winner[sortedRankedHands[i][0]] += 1
                tie = True
                numTies += 1
                    
        if(numTies > 0):
            if (debug):
                print('We have a ', numTies + 1, ' way tie! sortedRankedHands=', sortedRankedHands)
                            
        if (debug):
            if (tie):        
                print("Board cards=")
                treys.Card.print_pretty_cards(boardCards)
                for i in range(0, numPlayers):
                    print("Player %d cards=" % (i))
                    treys.Card.print_pretty_cards(hands[i]) 
                    rank_score = evaluator.evaluate(hands[i], boardCards)
                    rank_class = evaluator.get_rank_class(rank_score)
                    print("Player %d hand rank = %d (%s)\n" % (i, rank_score, evaluator.class_to_string(rank_class)))              
        
        # and finally, place a win in the bin of the winning player(s)
        # In the case of one or more ties split the pot equally amongst the
        # players who tied
        splitPotFactor = 1.0/(numTies + 1.0)
        winner[sortedRankedHands[0][0]] += splitPotFactor
        for i in range(1, numTies+1):
            winner[sortedRankedHands[i][0]] += splitPotFactor      

    for i in range(0, numPlayers):
        winner[i] /= numIterations

    return winner
 
        
    
