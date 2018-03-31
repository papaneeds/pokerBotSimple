#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a simple odds calculator based on pre-computed Odds.
See "preFlopHandOddsSimulations.py" for the odds simulations


Created on Sat Mar 31 15:55:37 2018

@author: tompokerlinux
"""
import numpy as np
import preFlopHandOddsSimulations

HAND_ROUND_TO_NUM_BOARD_CARDS = {
    0 : '5', # handround=0 (pre-flop) 2 hole cards and 5 board cards
    1 : '3', # handround=1 (flop) 2 hole cards and 3 board cards
    2 : '4' # handround=2 (turn) 2 hole cards and 4 board cards        
}

# This function reads in a pre-computed probability matrix 
# which was computed by "preFlopHandOddsSimulations.py" and
# returns that matrix
def getOddsMatrix(numPlayers, handRound, dataDirectory):
    
    inputFilename = dataDirectory \
        + str(numPlayers) + 'Player' \
        + HAND_ROUND_TO_NUM_BOARD_CARDS[handRound] + 'numBoardCardsProbabilityMatrix.npy'
    
    oddsMatrix = np.load(inputFilename)
    
    return oddsMatrix

# This function takes the pre-computed probability matrix, and
# given a set of hole cards in the form of a string like '2dAs'
# returns the probability that the hole cards will win
def getOdds(oddsMatrix, holeCards):
    # Find the rank and suit of the holeCards
    card1 = holeCards[0:2]
    card2 = holeCards[2:4]
    
    i = preFlopHandOddsSimulations.getIndexFromCard(card1)
    j = preFlopHandOddsSimulations.getIndexFromCard(card2)
        
    return oddsMatrix[i,j]
    
    

