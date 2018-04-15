#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 17:42:39 2018

@author: tompokerlinux
"""
from enum import Enum
import re

# Define an enum to hold the possible betting actions
class BettingAction(Enum):
    FOLD  = 'f'
    CALL  = 'c'
    RAISE = 'r'

# Define a Player class to store information about each player
class Player(object):

    # The class "constructor" - It's actually an initializer 
    def __init__(self, seatNumber, startingStackSize):
        self.seatNumber  = seatNumber # The seat number that this player sits in
        self.stackSize = startingStackSize # The current stack size for this player
   
        # These variables hold the historical values for each hand played
        # They are indexed by hand
        self.historicalCards     = []
        self.historicalStackSize = []
        self.historicalBet       = []               
        # These are the values during the current hand that the player
        # is participating in
        self.holeCards = ""
        self.bet = []  # The bets made during the hand, indexed by handRound
        self.folded = False # Whether the player has folded
        self.foldedHandRound = -1 # The handRound that they folded in.
     
    # This function resets all the variables for the current hand
    def resetCurrentState(self):
        self.holeCards = ""
        self.bet = []  # The bets made during the hand, indexed by handRound
        self.folded = False # Whether the player has folded
        self.foldedHandRound = -1 # The handRound that they folded in.  
        
    # This function saves historical information
    def addCurrentHandToHistoricalInfo(self):       
        self.historicalBet.append(self.bet)
        self.historicalCards.append(self.holeCards)

    # This function sets the player's stack size                
    def setStackSize(self, stackSize):
        self.stackSize = stackSize
        
    # This function writes the current hand out as a string
    def currentHandAsString(self):
        
        delimiter = '\r\n'
        outputString = 'holeCards=' + self.holeCards + delimiter
        outputString += 'bet='
        for handRoundCounter in range (0, len(self.bet)):
            if (handRoundCounter > 0):
                outputString += '/'
            for betRoundCounter in range (0, len(self.bet[handRoundCounter])):
                if (len(self.bet[handRoundCounter]) > 0):
                    outputString += self.bet[handRoundCounter][betRoundCounter][0]
        outputString += delimiter
        outputString += 'folded=' + str(self.folded) + delimiter
        outputString += 'foldedHandRound=' + str(self.foldedHandRound) + delimiter
        return outputString
        
# Define a gameDefinitionClass that will hold the game definition
class GameDefinition(object):
    gameType = "" 
    numPlayers = 0
    numRounds = 0 # The number of betting rounds per hand
    startingStack = [] # The starting stack of each player
    blinds = [] # The blinds, indexed from position=0
    
    # The first to act, indexed by handRound.
    #
    # On the first hand:
    #    The big blind is in seatNumber=0 (position=0 relative to the dealer)
    #    The small blind is in seatNumber=0 (position=1 relative to the dealer)
    # 
    # This array typically looks like 
    # [2, 0, 0 ,0] which means that the first to act
    # pre-flop = 2 (which means the player in position =2, which is the
    #               first player clockwise from the big blind)
    # flop = 0 (which means the player in position=0, the first player clockwise
    #           from the dealer)
    # turn = 0 
    # river = 0
    firstToAct = [] 
    
    def __init__(self, gameType, numPlayers, numRounds, startingStack, blinds, firstToAct):
        self.gameType = gameType
        self.numPlayers = numPlayers # This is also implicitly the number of seats
        self.numRounds = numRounds
        self.startingStack = startingStack
        self.blinds = blinds   
        self.firstToAct = firstToAct
    

# This function converts between position and seatNumber
def getSeatNumber(position, handNumber, numPlayers):
    seatNumber = (position + handNumber) % numPlayers
    return seatNumber

# This function converts between seatNumber and position
def getPosition(seatNumber, handNumber, numPlayers):
    position = (seatNumber - handNumber) % numPlayers
    return position


def readGameDefinition(gameDefinitionFile):
    with open(gameDefinitionFile) as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content] 
        print('Inside readGameDefinition. Game Definition =', content)
        for x in content[:]:
            print(x)
        
        gameType = content[1]
        print('gameType=', gameType)
        
        numPlayersString=content[2].split('=')
        numPlayers=int(numPlayersString[1].strip())
        print('numPlayers=', numPlayers)
        
        numRoundsString = content[3].split('=')
        numRounds = int(numRoundsString[1].strip())
        print('numRounds=', numRounds)
        
        stackString=content[4].split('=')
        startingStackString=stackString[1].split(' ')
        startingStack = list()
        for i in range (0, len(startingStackString)-1):
            startingStack.insert(i,int(startingStackString[i+1]))
            
        print('startingsStack=', startingStack)
        
        blindString=content[5].split('=')
        blinds=blindString[1].split()
        blinds[0]=int(blinds[0])
        blinds[1]=int(blinds[1])
        print('smallBlind=', blinds[0], 'bigBlind=', blinds[1])
        
        # This next section indicates which player acts first during the
        # various stages of play (pre-flop, flop, turn, river)
        # The value indicates the position relative to the dealer.
        # A value of 0 indicates the first position to the right of the dealer
        # (which is the small blind). A value of 1 indicates the big blind.
        # A value of 2 indicates the first non-blinded position.
        # The game definition file gives these values indexed from "1", whereas
        # we want them indexed from 0 (so we subtract 1 off of each value)
        firstToActLongString = content[6].split('=')
        firstToActString = firstToActLongString[1].split()
        firstToAct = list()
        for i in range (0, len(firstToActString)):
            firstToAct.insert(i,int(firstToActString[i])-1)
            print('firstToAct[', i, ']=', firstToAct[i])
        
        return GameDefinition(gameType, numPlayers, numRounds, startingStack, blinds, firstToAct)
        
# This function parses the handNumber out of the handState
def getHandNumber(handState):
        # First, split the action along '\r\n'
    actionStates = handState.split('\r\n')
    
    # The handState that we need to react to is in the last element 
    actionState = actionStates[len(actionStates)-2]
    #print('actionState=', actionState)
    
    splitState = actionState.split(':')
    #print('splitState=', splitState)
    
    handNumber   = int(splitState[2])

    return handNumber
    
# This function returns the last action in the previous hand
# It assumes a handState like:
# MATCHSTATE:1:0:r11374r20000f:|9hQd|
# MATCHSTATE:1:0:r11374r20000fc///:5d5c|9hQd|8dAs/8s4h6d/5s/Js
# MATCHSTATE:0:1::Ks6h||
# MATCHSTATE:0:1:c:Ks6h||   
def lastActionInPreviousHand(handState):
    #print('Inside lastActionInPreviousHand. handState=', handState) 
     
    # First, split the action along '\r\n'
    actionStates = handState.split('\r\n')
    
    # Now, cycle through the handState until  you find the boundary
    # between hand numbers
    for i in range (0, len(actionStates)-1):
#        print('In lastActionInPreviousHand. i=', i)
#        print('actionStates[i]=', actionStates[i])
#        print('actionStates[i].split(:)=', actionStates[i].split(':'))
        currentHandNumber = int(actionStates[i].split(':')[2])
        nextHandNumber    = int(actionStates[i+1].split(':')[2])
         
        if (currentHandNumber != nextHandNumber):
            return actionStates[i]
         
    return 'Error! The boundary between handNumbers was not found!'
     

# This function returns the last action in a handState
def lastAction(handState):
    #print('Inside lastAction. handState=', handState)
    
    # The handstate that is received has the format like:
    # MATCHSTATE:1:0:c:|9hQd\r\n
    # MATCHSTATE:1:0:cc/:|9hQd/8dAs8s\r\n
    # MATCHSTATE:1:0:cc/c:|9hQd/8dAs8s\r\n
    
    # First, split the action along '\r\n'
    actionStates = handState.split('\r\n')
    
    # The handState that we need to react to is in the last element 
    lastActionState = actionStates[len(actionStates)-2]
    print('lastActionState=', lastActionState)
    
    return lastActionState


# This function parses all the information out of the handState.
# Parameters: 
#     actionState : Input = a string that contains the action as sent to you by the poker server.
#     ie 'MATCHSTATE:2:38:ccc/cr11052fc/cr17065c/cr18088r19194r20000f:||5d4d/9cTc8c/Kh/2c'
# 
#     gameDefintion : Input - the GameDefinition object
# 
#     players : Input/Output - the players
# 
#     checkForPositionValidity - Input - boolean - check to see whether the 
#         actionState that you got is consistent with your current position
#         Set this to False if you are evaluating a previous hand
#         Set this to True if you are evaluating the validity of an actionState
#           i.e. whether the actionState that you got is consistent with your current 
#                position.

def decode(actionState, gameDefinition, players, checkForPositionValidity):
    print('Inside decode. actionState=', actionState)
    
    splitState = actionState.split(':')
    #print('splitState=', splitState)
    myPosition = int(splitState[1]) 
    
    handNumber   = int(splitState[2])
    betting      = splitState[3].split('/')
    handRound    = len(betting)-1
    cards    = splitState[4].split('|') 

    # A variable to hold the board cards
    # This is indexed by handRound
    boardCards = list()
                                            
    mySeatNumber = getSeatNumber(myPosition, handNumber, gameDefinition.numPlayers)
                                               
    # Move the first to act clockwise to the right each hand.
    # The firstToActThisRoundSeat is the seatNumber that the player who is
    # first to act on this round of betting is sitting in.
    # For Texas Hold'em:
    #   On handNumber=0, on handRound=0, firstToActThisRoundSeat = 2 % 3 = 2
    #   On handNumber=1, on handRound=0, firstToActThisRoundSeat = (2+1) % 3 = 0
    #   On handNumber=2, on handRound=0, firstToActThisRoundSeat = (2+2) % 3 = 1
    #     and so on.
    firstToActThisRoundSeat = ((gameDefinition.firstToAct[handRound]) + handNumber) % gameDefinition.numPlayers
       
    #print('myPosition=', myPosition,' handNumber=', handNumber,
    #      ' betting=',betting,' handRound=', handRound, ' cards=', cards, 
    #      ' firstToActThisRoundSeat=', firstToActThisRoundSeat,
    #      ' mySeatNumber=', mySeatNumber)
    
    # The hole cards are everything that appears before the first /
    # the flop, turn and river are everything that appears after the first /
    # parse these all out separately
    # Pre-flop we might have something like: |9hQd| 
    #    cards = '', 9hQd, ''
    # on the flop we might have something like: |9hQd|/8s4h6d
    #    cards = '', 9hQd, /8s4h6d
    # on the turn we might have somthing like: |9hQd|/8s4h6d/5s
    #    cards = '', 9hQd, /8s4h6d/5s
    # on the river we might have something like: |9hQd|/8s4h6d/5s/6s
    #    cards = '', 9hQd, /8s4h6d/5s/6s
    #
    numPlayers=len(cards)
    #print('numPlayers=', numPlayers, 'gameDefinition.numPlayers=', gameDefinition.numPlayers)
    if ( numPlayers != gameDefinition.numPlayers):
        print('ERROR!. numPlayers should be the same as gameDefinition.numPlayers!')
    
    # The hole cards of numPlayers-1 are in the first numPlayers-1 elements
    # of the cards array
    holeCards = []
    for position in range (0, numPlayers-1):
        holeCards.append(cards[position])
    
    # The last element of the cards array contains not only the last player's
    # hole cards, but also the betting cards. The last player's hole cards and the betting
    # cards are delimited by the / character.
    # For example,
    # on the turn we might have somthing like: |9hQd|/8s4h6d/5s
    #    cards = '', 9hQd, /8s4h6d/5s
    #  So, the last player's cards (player in position = 3) are '' (we can't see them)
    #  and the betting cards are 8s4h6d/5s
    temp = cards[numPlayers-1].split('/')
    #print('temp=', temp)
    holeCards.append(temp[0])
    
    # The hand round is the number of betting rounds that there are.
    # handRound is indexed starting at 0 for pre-flop.
    handRound = len(temp)-1
    #print('handRound=', handRound)
    
    # Assign the board cards
    # Board cards are indexed by hand round.
    # Since there are no board cards on handRound=0 (pre-flop) simply
    # always assign the pre-flop board cards to be ''
    boardCards.insert(0, '')
    if (handRound > 0):
        for handRoundCounter in range (1, handRound+1):
            boardCards.insert(handRoundCounter, temp[handRoundCounter])
            
    # Reset the values for this hand
    for seatNumberCounter in range (0, gameDefinition.numPlayers):
        players[seatNumberCounter].resetCurrentState()

    # assign each player their hole cards 
    for position in range (0, numPlayers):
        # Assign each player their cards
        #print("Inside decode. position=", position)
        # The hole cards array is indexed by position, whereas the 
        # players are indexed by seatNumber. So, convert position 
        # into seatNumber
        seatNumber = getSeatNumber(position, handNumber, numPlayers)
        players[seatNumber].holeCards = holeCards[position]
        #print('Inside decode. position=', position, 
        #      ' seatNumber=', seatNumber, 
        #      ' players[', seatNumber, '].holeCards=', players[seatNumber].holeCards,
        #      ' stackSize=', players[seatNumber].stackSize)
                   
    # Parse out any betting that has happened.
    # The betting strings that are expected by this regular
    # expression are of the form:
    # r123ccfr456c
    # The regular expression that matches this is
    # (
    #  (\S) match a character
    #      (\d+)? match one or more optional digits
    #            )        

    # Cycle through all the bets for the various hand rounds
    for handRoundCounter in range(0, handRound+1):   
        
        # a temporary variable to hold the bets 
        # for this round for each player. Indexed by seatNumber
        betsForThisHandRound = []
        for seatNumberCounter in range (0, gameDefinition.numPlayers):
            betsForThisHandRound.append([])
        
        #print('betting[', handRoundCounter, ']=', betting[handRoundCounter])
        matchObj = re.findall(r'((\S)(\d+)?)', betting[handRoundCounter])
        #print('numberOfMatches=', len(matchObj))
        #for i in range (0, len(matchObj)):
        #   print ('i=', i, ' matchObj[', i, ']=', matchObj[i])
        
        # Find out which position acts first on this hand round
        actingPlayerPosition = gameDefinition.firstToAct[handRoundCounter]
        

        
        #print('The player acting first in this hand round is actingPlayerPosition=', actingPlayerPosition, 
        #      ' actingPlayerSeat=', actingPlayerSeat)
        
        if (len(matchObj) > 0) :
            # You are not first to act on this hand round
            # Someone has bet before you.
            #print('Someone has bet before me. matchObj=', matchObj)
                
            #print('betsForThisHandRound=', betsForThisHandRound)
            
            # A variable to index the bets
            betCounter = 0;

            while (betCounter < len(matchObj)) :
                
                actingPlayerSeat = getSeatNumber(actingPlayerPosition, handNumber, 
                                                 gameDefinition.numPlayers)
 
                # Cycle through all the positions, starting at the actingPlayerPosition
                # and assign their bets
                
                # If the actingPlayerPosition has currently folded then increment the
                # actingPlayerPosition until you hit a position that hasn't folded
                #print('players[', actingPlayerSeat, '].folded=', players[actingPlayerSeat].folded)
                while (players[actingPlayerSeat].folded):
                #    print('actingPlayerPosition=', actingPlayerPosition, 
                #         ' actingPlayerSeat=', actingPlayerSeat, 
                #          ' has previously folded. Continuing to the next position')
                    actingPlayerPosition = (actingPlayerPosition + 1) % gameDefinition.numPlayers
                    actingPlayerSeat = getSeatNumber(actingPlayerPosition, handNumber, 
                                                     gameDefinition.numPlayers)
           
                # Assign the bet for the player in this position
                bet = matchObj[betCounter]
                
                actingPlayerSeat = getSeatNumber(actingPlayerPosition, handNumber, 
                                                 gameDefinition.numPlayers)
                
                #print('Assigning a bet to actingPlayerPosition=', actingPlayerPosition,
                #      ' actingPlayerSeat=', actingPlayerSeat,
                #      ' bet=', bet) 
                betsForThisHandRound[actingPlayerSeat].append(bet)
                #print('betsForThisHandRound=', betsForThisHandRound)
                if (bet[1] =='f'):
                    players[actingPlayerSeat].folded = True
                    players[actingPlayerSeat].foldedHandRound = handRoundCounter
                elif (bet[1] == 'r'):
                    # Decrease this player's stack size by the amount that they bet
                    players[actingPlayerSeat].stackSize = gameDefinition.startingStack[actingPlayerSeat] - int(bet[2])
                
                # Move the betCounter over by one and move the actingPlayerPosition over by one
                betCounter = betCounter + 1
                actingPlayerPosition = (actingPlayerPosition + 1) % gameDefinition.numPlayers


        # Assign all the bets for this hand round to the players
        for actingPlayerSeatCounter in range (0, gameDefinition.numPlayers):
#            print('actingPlayerSeatCounter=', actingPlayerSeatCounter)
#            print('handRoundCounter=', handRoundCounter)
#            print('betsForThisHandRound=', betsForThisHandRound)
#            print('betsForThisHandRound[', actingPlayerSeatCounter,']=', betsForThisHandRound[actingPlayerSeatCounter])
            players[actingPlayerSeatCounter].bet.insert(handRoundCounter, betsForThisHandRound[actingPlayerSeatCounter])

    # Check to make sure that you are the next player to act
    if (checkForPositionValidity):
        print('checking for position validity. handRound=', handRoundCounter,
              ' actingPlayerPosition=', actingPlayerPosition, 
              ' myPosition=', myPosition)
        
        actingPlayerSeat = getSeatNumber(actingPlayerPosition, handNumber, 
                                 gameDefinition.numPlayers)
                
        while (players[actingPlayerSeat].folded):
            actingPlayerPosition = (actingPlayerPosition + 1) % gameDefinition.numPlayers
            actingPlayerSeat = getSeatNumber(actingPlayerPosition, handNumber, 
                                             gameDefinition.numPlayers)
        
        if (actingPlayerPosition != myPosition):
            print('It is not my turn to act')
            return(myPosition, boardCards, actionState, handRound, handNumber, 
                   firstToActThisRoundSeat, True)
        else:
            print('Everything is okay. It is my turn to act')    
            
    return(myPosition, boardCards, 
           actionState, handRound, handNumber, firstToActThisRoundSeat, False)

# Given an actionState, determine if it is your turn to act.
def isItMyTurnToAct(actionState, gameDefinition, players):
    print('Inside isItMyTurnToAct. actionState=', actionState)
    
    splitState = actionState.split(':')
    myPosition = int(splitState[1]) 
    
    handNumber   = int(splitState[2])
    betting      = splitState[3].split('/')
    handRound    = len(betting)-1
    
    numPlayers = gameDefinition.numPlayers
    
    myPreviousBets = ''
    
    # Set an array which tells you which positions have folded
    # This array is indexed by position (not by seatNumber)
    folded = [False] * numPlayers
                   
    # Parse out any betting that has happened.
    # The betting strings that are expected by this regular
    # expression are of the form:
    # r123ccfr456c
    # The regular expression that matches this is
    # (
    #  (\S) match a character
    #      (\d+)? match one or more optional digits
    #            )
        
    # Cycle through all the bets for the various hand rounds
    for handRoundCounter in range(0, handRound+1):   
        
        matchObj = re.findall(r'((\S)(\d+)?)', betting[handRoundCounter])
#        print('numberOfMatches=', len(matchObj))
#        for i in range (0, len(matchObj)):
#           print ('i=', i, ' matchObj[', i, ']=', matchObj[i])
        
        # Find out which position acts first on this hand round
        actingPlayerPosition = gameDefinition.firstToAct[handRoundCounter]
        
        # Find out how many bets there are before you
        numberOfBets = len(matchObj)
        
        # If you are first to act and the number of matches is 0 then
        # this it is your turn to act
        if (len(matchObj) == 0):
            return True        
        else:
            # You are not first to act on this hand round
            # Someone has bet before you.
            #print('Someone has bet before me. matchObj=', matchObj)

            # A variable to index the bets
            betCounter = 0;
            
            # A variable to index the betting rounds
            # Each handRound (pre-flop, flop, turn, river) can contain one 
            # or more betting rounds.
            # The betting round increments when more than one round of the 
            # table is made in this handRound of betting.
            # For example, if it is pre-flop, with 3 players then the bets
            # might look like this:
            # cr1cr2r3fr4r5r6c
            # which would indicate that in bettingRound = 0 cr1c
            #                              bettingRound = 1 r2r3f
            #                              bettingRound = 2 r4r5
            #                              bettingRound = 3 r6c
            bettingRound = 0
            
            # keep track of the number of folds, checks/calls and raises
            numFolds = 0
            numChecks = 0
            numRaises = 0
            numPositionsExamined = 0

            while (betCounter < numberOfBets) :
                
                # Cycle through all the positions, starting at the actingPlayerPosition
                # and assign their bets
                
                # If the actingPlayerPosition has currently folded then increment the
                # actingPlayerPosition until you hit a position that hasn't folded
                while (folded[actingPlayerPosition]):
                    numPositionsExamined += 1
                    numFolds += 1
                    actingPlayerPosition = (actingPlayerPosition + 1) % numPlayers
           
                # Assign the bet for the player in this position
                bet = matchObj[betCounter]
                
                if (actingPlayerPosition == myPosition):
                    myPreviousBets = myPreviousBets + bet[0]
                
                if (bet[1] =='f'):
                    folded[actingPlayerPosition] = True
                    numFolds += 1
                elif (bet[1] == 'r'):
                    numRaises += 1
                else:
                    numChecks += 1
                
                # Move the betCounter over by one and move the actingPlayerPosition over by one
                betCounter = betCounter + 1
                numPositionsExamined += 1
                actingPlayerPosition = (actingPlayerPosition + 1) % gameDefinition.numPlayers
                
                # The bettingRound is the number of times the bet has cirlced the table.
                bettingRound = numPositionsExamined // numPlayers
                
        # If this is your valid turn to act then the number of people before you 
        # should be:    
        if (handRoundCounter == 0):
            # pre-flop
            # numberOfPeopleBeforeMe = (myPosition + numPlayers) - firstToActPosition 
            #                           + bettingRound * numPlayers
            expectedNumberOfPeopleBeforeMe = (myPosition + numPlayers) - gameDefinition.firstToAct[handRoundCounter] \
            + bettingRound * numPlayers
        else:
            # post-flop
            # numberOfPeopleBeforeMe = (myPosition + numPlayers) - firstToActPosition 
            #                           + bettingRound * numPlayers
            expectedNumberOfPeopleBeforeMe = (myPosition + 0) - gameDefinition.firstToAct[handRoundCounter] \
            + bettingRound * numPlayers            
            
        actualNumberOfPeopleBeforeMe = numPositionsExamined
        
        if (expectedNumberOfPeopleBeforeMe != actualNumberOfPeopleBeforeMe):
            return False    
            
    return True
    