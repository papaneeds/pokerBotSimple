#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 24 06:07:00 2018

@author: tompokerlinux

This is the expected value Bot.
It uses the expected value (calculated from the pot odds) to see whether or 
not to stay in the hand.

It checks, raises or folds if the probability is greater than threshold.

@author: tompokerlinux
"""

import simpleOdds
import gameUtilities

class ExpectedValueBot(gameUtilities.PokerBot):
    # The class "constructor" - It's actually an initializer 
    def __init__(self, numPlayers, threshold, dataDirectory):
        super().__init__(numPlayers, threshold, dataDirectory)
        self.name = 'ExpectedValueBot'
        # The following variables are set in the surperclass constructor
        #self.numPlayers  = numPlayers 
        #self.threshold = threshold
        #handRound = 0 # it's pre-flop
        #self.allIn = False
        #self.dataDirectory = dataDirectory
        #self.oddsMatrix = None


    def getBettingAction(self, handNumber, handRound, myPosition, firstToActPosition, numPlayers, players, blinds):
        bettingAction = 'c' # Default betting action
        allIn = False
        
        mySeatNumber = gameUtilities.getSeatNumber(myPosition, handNumber, numPlayers)

        self.oddsMatrix = simpleOdds.getOddsMatrix(numPlayers, handRound, self.dataDirectory)

        probability = simpleOdds.getOdds(self.oddsMatrix, players[mySeatNumber].holeCards)

        # Figure out if you should bet, raise or call based on the expected value
        
        # Figure out what the betting action has been on this round so far.
        # To calculate your pot odds and possible bet you need to know:
        # 1. The size of the last raise L_R
        # 2. The size of the last bet L_B
        # 3. Your current commitment to the pot C_B(position)
        # 
        
        # If this is pre-flop then there are forced small blind and big blinds
        # In this case the last bet is the BB and the last raise is the BB
        if (handRound == 0):
            position = 1
            L_R = blinds[position]
            L_B = L_R
        else:
            # For all other hand rounds the last bet and last raise are zero
            # initially
            L_R = 0
            L_B = 0
        
        numChecks = 0
        numRaised = 0
        numFolded = 0
        folded = [False] * numPlayers # an array to keep track of who folded
        someoneWentAllIn = False
        someoneRaised = False
        raisedTo = 0
        position = firstToActPosition
        numPositionsExamined = 0

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
                    raisedTo = currentBet[2:end] xxx keep going from here.
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
          
        
        
        
        
        
        
        # The code below this line is the original code
        
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
            
            
        
