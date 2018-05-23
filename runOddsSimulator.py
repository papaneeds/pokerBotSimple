#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 17:02:56 2018

@author: tompokerlinux
"""

import preFlopHandOddsSimulations as ps
import numpy as np
import graphicalAnalysis as ga

# Main program
debug = False

# Create all possible pairs of hands
numIterations = 1000

MAX_NUM_PLAYERS = 10
NUM_BOARD_CARDS = [3, 4, 5]

for numPlayers in range (2, MAX_NUM_PLAYERS+1):
    for numBoardCards in NUM_BOARD_CARDS:
        print ('numPlayers=', numPlayers, ' numBoardCards=', numBoardCards)
        probabilities = ps.probabilityMatrix(numIterations, numPlayers, numBoardCards, debug)
        
        # Save the probabilities to a file 
        filename = './data/' + str(numPlayers) + 'Player' + str(numBoardCards) + 'numBoardCards' \
            + 'ProbabilityMatrix'
        np.save(filename, probabilities)

        # Display matrix
        ga.plotMatrix(probabilities)
                  
print('I am done')