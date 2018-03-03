#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 10:14:14 2018

@author: tompokerlinux
"""
import sys
import socket
from enum import Enum
import random
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
        self.cards = ""
        self.bet = []        
        
        

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
        
def decode(handState, handRound, gameDefinition, players):
    print('Inside decode. handState=', handState, ' handRound=', handRound)
    
    # The handstate that is received has the format like:
    # MATCHSTATE:1:0:c:|9hQd\r\n
    # MATCHSTATE:1:0:cc/:|9hQd/8dAs8s\r\n
    # MATCHSTATE:1:0:cc/c:|9hQd/8dAs8s\r\n
    
    # First, split the action along '\r\n'
    actionStates = handState.split('\r\n')
    
    # The handState that we need to react to is in the last element 
    actionState = actionStates[len(actionStates)-2]
    print('actionState=', actionState)
    
    splitState = actionState.split(':')
    print('splitState=', splitState)
    myPosition = int(splitState[1]) 
    
    handNumber   = int(splitState[2])
    betting      = splitState[3].split('/')
    handRound    = len(betting)-1
    cards    = splitState[4].split('|') 
                                            
    mySeatNumber = (myPosition + handNumber) % gameDefinition.numPlayers
                                               
    # Move the first to act clockwise to the right each hand.
    # The firstToActThisRoundSeat is the seatNumber that the player who is
    # first to act on this round of betting is sitting in.
    # For Texas Hold'em:
    #   On handNumber=0, on handRound=0, firstToActThisRoundSeat = 2 % 3 = 2
    #   On handNumber=1, on handRound=0, firstToActThisRoundSeat = (2+1) % 3 = 0
    #   On handNumber=2, on handRound=0, firstToActThisRoundSeat = (2+2) % 3 = 1
    #     and so on.
    firstToActThisRoundSeat = ((gameDefinition.firstToAct[handRound]) + handNumber) % gameDefinition.numPlayers
       
    print('myPosition=', myPosition,' handNumber=', handNumber,
          ' betting=',betting,' cards=', cards, 'handRound=', handRound, 
          'firstToActThisRoundSeat=', firstToActThisRoundSeat)
    
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
    print('numPlayers=', numPlayers, 'gameDefinition.numPlayers=', gameDefinition.numPlayers)
    
    # The last element of the cards array contains not only the last player's
    # hole cards, but also the betting cards. The last player's hole cards and the betting
    # cards are delimited by the / character.
    # For example,
    # on the turn we might have somthing like: |9hQd|/8s4h6d/5s
    #    cards = '', 9hQd, /8s4h6d/5s
    #  So, the last player's cards (player in position = 3) are '' (we can't see them)
    #  and the betting cards are 8s4h6d/5s
    temp = cards[numPlayers-1].split('/')
    print('temp=', temp)
    holeCards[numPlayers-1] = temp[0]
    
    # The hand round is the number of betting rounds that there are.
    # handRound is indexed starting at 0 for pre-flop.
    handRound = len(temp)-1
    print('handRound=', handRound)

    # if this is pre-flop then assign each player their 
    # cards
    if (handRound == 0):   
        for position in range (0, numPlayers):
            # Assign each player their cards
            print("Inside decode. Pre-flop play. position=", position)
            # The hole cards array is indexed by position, whereas the 
            # players are indexed by seatNumber. So, convert position 
            # into seatNumber
            seatNumber = (position + handNumber) % numPlayers
            players[seatNumber].holeCards = holeCards[position]
            print("Inside decode. players[", seatNumber, "].cards=", players[seatNumber].cards,
                  " stackSize=", players[seatNumber].stackSize)
                   
    # Parse out any betting that has happened.
    # The betting strings that are expected by this regular
    # expression are of the form:
    # r123ccfr456c
    # The regular expression that matches this is
    # (
    #  (\S) match a character
    #      (\d+)? match one or more optional digits
    #            )
 
    # First, clear out the bets currently stored in the players
    for seatNumber in range(0, gameDefinition.numPlayers):
        players[seatNumber].bet = []
        
    for handRoundCounter in range(0, handRound+1):   
        
        # a temporary variable to hold the bets 
        # for this round for a particular acting player
        betsForThisRound = []
        
        print('betting[', handRoundCounter, ']=', betting[handRoundCounter])
        matchObj = re.findall(r'((\S)(\d+)?)', betting[handRoundCounter])
        print('numberOfMatches=', len(matchObj))
#        xxx this is where things are messing up.
#        In your data file you have taken the second hand, which means that
#        the first to act has moved around one position. However, you are still
#        setting the active player based on the firstToAct of the original hand.
#        This means that you are putting the bet in the wrong spot.
#        Anyhow, find a way to fix this.
#        Okay, so you have found a way to fix this and it involves having
#        a handNumber and a firstToActThisRoundSeat. 
        
        # Original Code: actingPlayer = gameDefinition.firstToAct[handRoundCounter]
        actingPlayer = firstToActThisRoundSeat
        if (len(matchObj) > 0) :
            print('matchObj=', matchObj)
            # initialize a temporary list that will hold the bets
            # for each player
            for i in range (0, gameDefinition.numPlayers):
                betsForThisRound.append([])
                
            print('betsForThisRound=', betsForThisRound)
            for i in range (0, len(matchObj)): 
                betsForThisRound[actingPlayer].append(matchObj[i])
                print('betsForThisRound=', betsForThisRound)
                
                # if the acting player folded and the acting player
                # is the firstToAct in the next round of betting
                # then move the firstToAct over by one player
                # for all subsequent betting rounds
                print('matchObj[', i, '][0]=', matchObj[i][0])
                
                This is suspect and very likely not necessary.
                if ((matchObj[i][0] == 'f') \
                    and (handRoundCounter < (gameDefinition.numRounds-1)) \
                    and (actingPlayer == gameDefinition.firstToAct[gameDefinition+1]) \
                    ):
                    print('Player=', i, ' has folded and is the next to act in subsequent rounds')
                    print('Re-setting gameDefinition.firstToAct for all subsequent rounds')
                    for j in range (handRoundCounter+1, (gameDefinition.numRounds)):
                        print('gameDefinition.firstToAct[', j, ']=', gameDefinition.firstToAct[i], 
                              'resetting to ', gameDefinition.firstToAct[j]+1)
                        gameDefinition.firstToAct[j] = gameDefinition.firstToAct[j]+1
                    
                
                actingPlayer = (actingPlayer + 1) % numPlayers
        else:
            print('no match found for betting')

        # an optimization would be to move this to the initalization section 
        # of betsForThisRound above
        for actingPlayer in range (0, gameDefinition.numPlayers):
            print('actingPlayer=', actingPlayer, 
                  ' handRoundCounter=', handRoundCounter)
            print('betsForThisRound[', actingPlayer, ']=', betsForThisRound[actingPlayer])
#            players[actingPlayer].bet[handRoundCounter] = betsForThisRound[actingPlayer]
            players[actingPlayer].bet.insert(handRoundCounter, betsForThisRound[actingPlayer])
            print('players[', actingPlayer, '].bet[', handRoundCounter, 
                  ']=', players[actingPlayer].bet[handRoundCounter])       
    
    # Advance the handRound.
    # handRound = 0 means pre-flop
    # handRound = 1 means flop
    # handRound = 2 means turn
    # handRound = 3 means river
    #print('about to increment handRound from handRound=', handRound, 
    #      ' to handRound=' , (handRound + 1) % gameDefinition.numRounds)          
    #handRound = (handRound + 1) % gameDefinition.numRounds

    return(myPosition, flopCards, turnCard, riverCard, 
           actionState, handRound, handNumber, firstToActThisRoundSeat)
    
    

# main program starts here
print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))

if (len(sys.argv) != 4) :
    print('Error. invalid arguments')
    print('Usage: pokerBotSimple.py gameFile IP port')
    sys.exit(1)

print ('The game definition file is ', sys.argv[1])
print ('The IP address to connect to is ', sys.argv[2])
print ('The port to connect to is ', sys.argv[3])

# read in the game definition file
serverDirectory        = '/home/tompokerlinux/Documents/project_acpc_server/'
gameDefinitionFilename = sys.argv[1]
gameDefinition         = readGameDefinition(serverDirectory + gameDefinitionFilename)

#print('Inside main. gameType=', gameDefinition.gameType)
#print('Inside main. numPlayers=', gameDefinition.numPlayers)
#print('Inside main. numRounds=', gameDefinition.numRounds)
#print('Inside main. startingStack=', gameDefinition.startingStack)
#print('Inside main. blinds=', gameDefinition.blinds)
#print('Inside main. firstToAct=', gameDefinition.firstToAct)

# create the players for the game
players = list()
for i in range (0, gameDefinition.numPlayers):
    print("Inside main. creating player=", i, 
          'startingStack=', gameDefinition.startingStack[i])
    players.insert(i, Player(i, gameDefinition.startingStack[i]))
    print('players[',i,'].stackSize=', players[i].stackSize)
    
#    Once you've got that sorted out then move on to the end of hand
#    play and how you store the values of the current hand (cards, bet, stack)
#    in the historical list of values.
print ('players[0].stackSize=', players[0].stackSize)

# start communicating with the dealer
HOST = sys.argv[2]   
PORT = int(sys.argv[3]) 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
versionString = "VERSION:2.0.0\r\n"
s.send(versionString.encode('utf-8'))

# Now, start playing the game for real
handRound = 0 # 0=pre-flop, 1=flop, 2=turn, 3=river
cont= True
while (cont == True):
    print('=======================================')
    print('Inside main. Just before receiving data')
    data = ''
    data = s.recv(2048)
    dataString = data.decode('utf-8')

    print('Received dataString=', dataString)
    
    # decode the message that you received
    [myPosition, flopCards, turnCard, riverCard, actionState, handRound, handNumber, firstToActThisRoundSeat] \
        = decode(dataString, handRound, gameDefinition, players)
    
    print('Time for me to act.')
    print('myPosition=', myPosition,
          ' handRound=', handRound,
          ' handNumber=', handNumber,
          ' definition firstToAct[', handRound, ']=', gameDefinition.firstToAct[handRound],
          ' first to act this round=', firstToActThisRoundSeat)
          
          
    print(' flopCards=', flopCards,
          ' turnCard=', turnCard,
          ' riverCard=', riverCard)
    
    for i in range (0, gameDefinition.numPlayers):
        print('Inside main. player[', i, '].cards=', players[i].cards )
        
    print('Inside main. handRound=', handRound)
        
    bettingAction = 'c'
    betSize = 0
    print('Inside main. player[', myPosition, ']. actionState=', actionState,
          'bettingAction=', bettingAction,
          ' betSize=', betSize)
    
    # send the action back to the server
    #dataString = dataString + ":" + bettingAction + '\r\n'
    dataString = actionState + ":" + bettingAction + '\r\n'
    print('Inside main. dataString=', dataString)
    data=dataString.encode('utf-8')
    s.send(data)
    print('Inside main. just sent the data')
    
    # The dealer button will move in the next hand
    # This means that the player number will move to the left by
    # 1 postion.
#    for i in range (0, gameDefinition.numPlayers):
#        players[i].seatNumber = (players[i].seatNumber - 1) % gameDefinition.numPlayers

s.close()




