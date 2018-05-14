#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 11:02:04 2018

@author: tompokerlinux
"""

import treys
import partialDeck
import gameUtilities

# This function calculates the pre-flop odds of p1_hand having the 
# currently winning hand in a numPlayerss table after numBoardCards are dealt.
# The odds are calcualted by drawing numIterations hands.
# 
def getpreFlopOdds(p1_hand, # The hole cards
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
            
        numTies = gameUtilities.findWinners(debug,
                                            evaluator, numPlayers, hands, boardCards, winner)

    for i in range(0, numPlayers):
        winner[i] /= numIterations

    return winner


# This function calculates the expected hand strength of p1_hand having the 
# currently winning hand in a numPlayers table, with existingBoardCards dealt and
# numBoardCardsToCome more cards to come.
# The odds are calcualted by drawing numIterations hands.
# 
def getExpectedHandStrengthOdds(p1_hand, # The hole cards
                                numIterations, # The number of iterations to run the simulation for
                                numPlayers, # The number of players in the hand
                                numBoardCardsToCome, # The number of board cards still to come
                                existingBoardCards # The existing board cards
                                ):

    debug = True

    # pretend you are playing with n random players 
    # for numIterations hands with numBoardCardsToCome and existingBoardCards board cards
    evaluator = treys.Evaluator()
    winner = [0] * numPlayers
            
    for j in range (0, numIterations):
        # create the partial deck that excludes your cards and the board cards
        p1_HandAndExistingBoardCards = p1_hand + existingBoardCards
        pDeck = partialDeck.PartialDeck(p1_HandAndExistingBoardCards)
        
        # create the hands.
        # By convention your hand is in index=0
        hands = []
        hands.append(p1_hand)
        for i in range(1, numPlayers):
            hands.append(pDeck.draw(2))
            
        # Now, draw the board cards
        boardCardsToCome = pDeck.draw(numBoardCardsToCome)
        if (debug):
            print("Existing board cards=")
            treys.Card.print_pretty_cards(existingBoardCards)
            print("New board cards=")
            treys.Card.print_pretty_cards(boardCardsToCome)

        fullBoardCards = existingBoardCards + boardCardsToCome
            
        numTies = gameUtilities.findWinners(debug,
                                            evaluator, numPlayers, hands, 
                                            fullBoardCards, winner)

    for i in range(0, numPlayers):
        winner[i] /= numIterations

    return winner