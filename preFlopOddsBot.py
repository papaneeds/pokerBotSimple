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
            numRaised = 0
            numFolded = 0
            folded = [False] * numPlayers # an array to keep track of who folded
            someoneWentAllIn = False
            someoneRaised = False
            position = firstToActPosition
            numPositionsExamined = 0
            #while (position != myPosition):

            
            # There could be several rounds of betting for each
            # handRound (pre-flop, flop, turn and river)
            bettingRound = numPositionsExamined // numPlayers
            
            seatNumber = gameUtilities.getSeatNumber(position, 
                                                     handNumber, 
                                                     numPlayers)
            
            numBettingRoundsForThisPlayer = len(players[seatNumber].bet[handRound])
            

 
            # Keep iterating through players until you hit your position
            # and find that you have not bet yet                       
            while (  not (
                            (position == myPosition)  
                            & (bettingRound == numBettingRoundsForThisPlayer)
                        )
                ):

                # Only consider players who have not folded
                if (not folded[seatNumber]):
                    currentBet = players[seatNumber].bet[handRound][bettingRound]
                    if (players[seatNumber].stackSize == 0):
                        # This player has gone all in. 
                        someoneWentAllIn = True
                    elif (currentBet[1] == 'r'):
                        someoneRaised = True
                        numRaised += 1
                    elif (currentBet[1] == 'c'):
                        numChecks += 1
                    elif (currentBet[1] == 'f'):
                        numFolded += 1
                        folded[seatNumber] = True
                        
                position += 1
                position = position % numPlayers
                numPositionsExamined += 1
                
                                
                bettingRound = numPositionsExamined // numPlayers
            
                seatNumber = gameUtilities.getSeatNumber(position, 
                                                         handNumber, 
                                                         numPlayers)
                
                numBettingRoundsForThisPlayer = len(players[seatNumber].bet[handRound])
                
                        
            #If anyone before you bet and you were not going all in then fold
            if (someoneRaised & (allIn == False)):
                bettingAction = 'f'
            # If someone went all in before you and you were planning on
            # going all in then call
            elif (someoneWentAllIn & allIn):
                bettingAction = 'c'
            # If no one raised before you then just call
            # (even if you were not planning on going all in). You basically
            # get free cards
            elif ((not someoneRaised) & (not allIn)):
                bettingAction = 'c'
            else:
                # Go all in
                bettingAction = 'r' + str(players[mySeatNumber].stackSize)       
               
        return bettingAction
            
            
        
