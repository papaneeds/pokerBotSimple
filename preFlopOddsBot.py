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

class PreFlopOddsBot(gameUtilities.PokerBot):
    # The class "constructor" - It's actually an initializer 
    def __init__(self, numPlayers, threshold, dataDirectory):
        super().__init__(numPlayers, threshold, dataDirectory)
        self.name = 'PreFlopOddsBot'
        # The following variables are set in the superclass constructor
        #self.numPlayers  = numPlayers 
        #self.threshold = threshold
        #self.allIn = False
        
        # The odds matrix for the pre-flop odds bot never changes. It is
        # always the pre-flop odds matrix. So, retrieve it once at the
        # start of time and then just leave it.
        handRound = 0 # it's pre-flop
        self.oddsMatrix = simpleOdds.getOddsMatrix(numPlayers, handRound, dataDirectory)

    def getBettingAction(self, handNumber, handRound, myPosition, firstToActPosition, numPlayers, players, blinds):
        bettingAction = 'c' # Default betting action
        allIn = False
        
        # Stay in this hand if the probability of 
        # you winning pre-flop are greater than threshold
        mySeatNumber = gameUtilities.getSeatNumber(myPosition, handNumber, numPlayers)
        probability = simpleOdds.getOdds(self.oddsMatrix, players[mySeatNumber].holeCards)
        if (probability >= self.threshold):
            allIn = True
            
     
        # Figure out what the betting action has been on this round so far
        # If anyone has gone all in, and you were planning on going all in
        #    then just call.
        # If you were planning on folding and everyone before you has just
        #    checked then you check too
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
            if (not (players[seatNumber].folded)):
                #print('Inside preFlopOddsBot. seatNumber=', seatNumber,
                #      ' folded[seatNumber]=', folded[seatNumber],
                #      ' handRound=', handRound,
                #      ' bettingRound=', bettingRound,
                #      'players[seatNumber].bet[handRound]=', players[seatNumber].bet[handRound],
                #      ' len(players[seatNumber].bet[handRound])=', len(players[seatNumber].bet[handRound]))
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
 
#           print('Inside preFlopOddsBot. position=', position, 
#                 ' myPosition=', myPosition, 
#                 '( position == myPosition)=', ( position == myPosition),
#                 'bettingRound=', bettingRound,
#                 ' numBettingRoundsForThisPlayer=', numBettingRoundsForThisPlayer,
#                 ' (bettingRound == numBettingRoundsForThisPlayer)=', 
#                  (bettingRound == numBettingRoundsForThisPlayer))
            
        # Unless this is pre-flop and
        # you are the big blind and 
        # you were not going all in and
        # everyone else has just called then
        # fold
        if ((handRound == 0) & 
        (players[mySeatNumber].blind == max(blinds)) & 
        (allIn == False) & 
        (not someoneRaised)):
            bettingAction = 'c'
            print('Inside preFlopOddsBot. probability=', probability, 
                  ' threshold=', self.threshold, 
                  ' This is pre-flop, I am the big blind, I was not planning on going all in and no one has raised. I get a free card. Returning=', bettingAction)                        
        # If this is post-flop and no one raised before you then just call
        # (even if you were not planning on going all in). You basically
        # get free cards
        elif ((handRound != 0) & (not someoneRaised) & (not allIn)):
            bettingAction = 'c'
            print('Inside preFlopOddsBot. probability=', probability, 
                  ' threshold=', self.threshold, 
                  ' This is post flop, nobody raised before me and I was not planning on going all in. I get another free card. Returning=', bettingAction)
        #If anyone before you bet and you were not going all in then fold
        elif (someoneRaised & (allIn == False)):
            bettingAction = 'f'
            print('Inside preFlopOddsBot. probability=', probability, 
                  ' threshold=', self.threshold, 
                  ' Someone raised before me and I was not planning on going all in. Returning=', bettingAction)
        # If someone went all in before you and you were planning on
        # going all in then call
        elif (someoneWentAllIn & allIn):
            bettingAction = 'c'
            print('Inside preFlopOddsBot. probability=', probability, 
                  ' threshold=', self.threshold, 
                  ' Someone went all in before me and I was planning on going all in. Returning=', bettingAction)                
        else:
            # Go all in
            bettingAction = 'r' + str(players[mySeatNumber].handStartingStackSize)
            print('Inside preFlopOddsBot. probability=', probability, 
                  ' threshold=', self.threshold, 
                  ' Going all in. Returning=', bettingAction)
            
        return bettingAction
            
            
        
