#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 17:22:22 2018

This is the pre-flop odds Bot.
It uses simple odds that are calculated pre-flop to see whether or 
not to stay in the hand.

It goes all in pre-flop if the probability is greater than threshold.

Otherwise, it will fold to any bet on any round.

@author: tompokerlinux
"""

import simpleOdds
import gameUtilities

class PreFlopOddsBot(object):
    # The class "constructor" - It's actually an initializer 
    def __init__(self, numPlayers, threshold, dataDirectory):
        self.numPlayers  = numPlayers 
        self.threshold = threshold
        handRound = 0 # it's pre-flop
        self.oddsMatrix = simpleOdds.getOddsMatrix(numPlayers, handRound, dataDirectory)
        self.allIn = False

    def getBettingAction(self, handRound, myPosition, firstToActPosition, players):
        bettingAction = 'c' # Default betting action
        
        # Figure out what the betting action has been on this round so far
        for position in range (firstToActPosition, myPosition):
            xxx continue here.
        
        if (handRound == 0):
            # See what the betting action is so far
            
            
            
            # This is pre-flop. Stay in this hand if the probability of 
            # you winning pre-flop are greater than threshold
            probability = simpleOdds.getOdds(self.oddsMatrix, holeCards)
            if (probability >= threshold):
                action = 'r' + str(stackSize)
        else:
            # if anyone has bet then get 
            bettingAction = 'c'
            
        return bettingAction
            
            
        
