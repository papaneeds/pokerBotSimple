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

    def getBettingAction(self, handNumber, handRound, myPosition, firstToActPosition, numPlayers, players):
        bettingAction = 'c' # Default betting action
        allIn = False
        
        # This is pre-flop. Stay in this hand if the probability of 
        # you winning pre-flop are greater than threshold
        mySeatNumber = gameUtilities.getSeatNumber(myPosition, handNumber, numPlayers)
        probability = simpleOdds.getOdds(self.oddsMatrix, players[mySeatNumber].holeCards)
        if (probability >= self.threshold):
            allIn = True
            
        if (myPosition == firstToActPosition):
            if (allIn):
                bettingAction = 'r' + str(players[myPosition].stackSize)
            else:
                bettingAction = 'c'
            return bettingAction
        else:         
            # Figure out what the betting action has been on this round so far
            # If anyone has gone all in, and you were planning on going all in
            #    then just call.
            # If you were planning on folding and everyone before you has just
            #    checked then you check to
            numChecks = 0
            someoneWentAllIn = False
            someoneRaised = False
            position = firstToActPosition
            while (position != myPosition):
                seatNumber = gameUtilities.getSeatNumber(position, 
                                                         handNumber, 
                                                         numPlayers)
                # At this stage of the game numBetsByThisPlayer should always be 1
                numBetsByThisPlayer = len(players[seatNumber].bet[handRound])
                if (numBetsByThisPlayer > 0):
                    if (players[seatNumber].stackSize == 0):
                        # This player has gone all in. 
                        someoneWentAllIn = True
                    elif (players[seatNumber].bet[0][1] == 'r'):
                        someoneRaised = True
                    elif (players[seatNumber].bet[0][1] == 'c'):
                        numChecks += 1
                position += 1
                position = position % numPlayers
                        
            # If everyone before you checked then just check           
            if (numChecks == (myPosition - firstToActPosition)):
                bettingAction = 'c'
            #If anyone before you bet and you were not going all in then fold
            elif (someoneRaised & (allIn == False)):
                bettingAction = 'f'
            # If someone went all in before you and you were planning on
            # going all in then call
            elif (someoneWentAllIn & allIn):
                bettingAction = 'c'
                
        return bettingAction
            
            
        
