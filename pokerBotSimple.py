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
    def __init__(self, position, startingStackSize):
        self.position  = position # The seat number that this player sits in
        self.stackSize = startingStackSize
        print('Inside __init__. position=', self.position, 
              'stackSize=', self.stackSize)        
        # These variables hold the historical values for each game played
        self.historicalCards     = []
        self.historicalStackSize = []
        self.historicalBet       = []               
        # These are the values during the current game that the player
        # is participating in
        self.cards = ""
        self.stackSize = 0
        self.bet = []        
        print('Again, Inside __init__. position=', self.position, 
              'stackSize=', self.stackSize)
        
        

# Define a gameDefinitionClass that will hold the game definition
class GameDefinition(object):
    gameType = "" 
    numPlayers = 0
    numRounds = 0
    startingStack = []
    blinds = []
    firstToAct = []
    
    def __init__(self, gameType, numPlayers, numRounds, startingStack, blinds, firstToAct):
        self.gameType = gameType
        self.numPlayers = numPlayers
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
        
def decode(gameState, gameRound, gameDefinition, players):
    print('Inside decode. gameState=', gameState, ' gameRound=', gameRound)
    
    flopCards =''
    turnCard =''
    riverCard = ''
    
    # The gamestate that is received has the format like:
    # MATCHSTATE:1:0:c:|9hQd\r\n
    # MATCHSTATE:1:0:cc/:|9hQd/8dAs8s\r\n
    # MATCHSTATE:1:0:cc/c:|9hQd/8dAs8s\r\n
    
    # First, split the action along '\r\n'
    actionStates = gameState.split('\r\n')
    
    # The gameState that we need to react to is in the last element 
    actionState = actionStates[len(actionStates)-2]
    print('actionState=', actionState)
    
    splitState = actionState.split(':')
    print('splitState=', splitState)
    mySeatNumber = int(splitState[1])
    gameNumber   = splitState[2]
    betting      = splitState[3].split('/')
    gameRound    = len(betting)-1
    cards    = splitState[4].split('|')
    print('mySeatNumber=', mySeatNumber,' gameNumber=',gameNumber,
          ' betting=',betting,' cards=',cards, 'gameRound=', gameRound)
    
    # The last player's hole cards, 
    # the flop, turn and river are in the last element of cards
    # parse these all out separately
    # Pre-flop we might have something like: cards = |9hQd|
    # on the flop we might have something like: cards = |9hQd|/8s4h6d
    # on the turn we might have somthing like: cards = |9hQd|/8s4h6d/5s
    # on the river we might have something like: cards = |9hQd|/8s4h6d/5s/6s
    numPlayers=len(cards)
    print('numPlayers=', numPlayers)
    temp = cards[numPlayers-1].split('/')
    print('temp=', temp)
    cards[numPlayers-1] = temp[0]
    
    # The game round is the number of betting rounds that there are.
    # gameRound is indexed starting at 0 for pre-flop.
    #gameRound = len(betting)-1
    gameRound = len(temp)-1
    print('gameRound=', gameRound)

    # if this is pre-flop then assign each player their 
    # cards
    if (gameRound == 0):   
        for i in range (0, numPlayers):
            # Assign each player their cards
            print("Inside decode. Pre-flop play. i=", i)
            players[i].cards = cards[i]
            print("Inside decode. players[", i, "].cards=", players[i].cards,
                  " stackSize=", players[i].stackSize)
            
        
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
    for playerCounter in range(0, gameDefinition.numPlayers):
        players[playerCounter].bet = []
        
    for gameRoundCounter in range(0, gameRound+1):   
        
        # a temporary variable to hold the bets 
        # for this round for a particular acting player
        betsForThisRound = []
        
        print('betting[', gameRoundCounter, ']=', betting[gameRoundCounter])
        matchObj = re.findall(r'((\S)(\d+)?)', betting[gameRoundCounter])
        print('numberOfMatches=', len(matchObj))
        actingPlayer = gameDefinition.firstToAct[gameRoundCounter]
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
                if ((matchObj[i][0] == 'f') \
                    and (gameRoundCounter < (gameDefinition.numRounds-1)) \
                    and (actingPlayer == gameDefinition.firstToAct[gameDefinition+1]) \
                    ):
                    print('Player=', i, ' has folded and is the next to act in subsequent rounds')
                    print('Re-setting gameDefinition.firstToAct for all subsequent rounds')
                    for j in range (gameRoundCounter+1, (gameDefinition.numRounds)):
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
                  ' gameRoundCounter=', gameRoundCounter)
            print('betsForThisRound[', actingPlayer, ']=', betsForThisRound[actingPlayer])
#            players[actingPlayer].bet[gameRoundCounter] = betsForThisRound[actingPlayer]
            players[actingPlayer].bet.insert(gameRoundCounter, betsForThisRound[actingPlayer])
            print('players[', actingPlayer, '].bet[', gameRoundCounter, 
                  ']=', players[actingPlayer].bet[gameRoundCounter])       
    
    # Advance the gameRound.
    # gameRound = 0 means pre-flop
    # gameRound = 1 means flop
    # gameRound = 2 means turn
    # gameRound = 3 means river
    #print('about to increment gameRound from gameRound=', gameRound, 
    #      ' to gameRound=' , (gameRound + 1) % gameDefinition.numRounds)          
    #gameRound = (gameRound + 1) % gameDefinition.numRounds

    return(mySeatNumber, flopCards, turnCard, riverCard, actionState, gameRound)
    
    

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
serverDirectory='/home/tompokerlinux/Documents/project_acpc_server/'
gameDefinitionFilename=sys.argv[1]
gameDefinition=readGameDefinition(serverDirectory + gameDefinitionFilename)

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
    
#    xxx start here. For some reason the startingStack is not being held
#    in the instance variables in the Player object. 
#    Once you've got that sorted out then move on to the end of hand
#    play and how you store the values of the current hand (cards, bet, stack)
#    in the historical list of values.
print ('players[0].stackSize=', players[0].stackSize)
    
# Pay the small and big blinds
# player 0 is the small blind
# player 0 is the big blind
players[0].stackSize = players[0].stackSize - gameDefinition.blinds[0]
players[1].stackSize = players[1].stackSize - gameDefinition.blinds[1]

# start communicating with the dealer
HOST = sys.argv[2]   
PORT = int(sys.argv[3]) 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
versionString = "VERSION:2.0.0\r\n"
s.send(versionString.encode('utf-8'))

# Now, start playing the game for real
gameRound = 0 # 0=pre-flop, 1=flop, 2=turn, 3=river
cont= True
while (cont == True):
    print('=======================================')
    print('Inside main. Just before receiving data')
    data = ''
    data = s.recv(2048)
    dataString = data.decode('utf-8')
    print('Time for me to act.')
    print(' firstToAct[', gameRound, ']=', gameDefinition.firstToAct[gameRound])
    print('Received dataString=', dataString)
    
    # decode the message that you received
    [mySeatNumber, flopCards, turnCard, riverCard, actionState, gameRound] \
        = decode(dataString, gameRound, gameDefinition, players)
    
    print('Inside Main. mySeatNumber=', mySeatNumber,
          ' gameRound=', gameRound,
          ' firstToAct[', gameRound, ']=', gameDefinition.firstToAct[gameRound],
          ' flopCards=', flopCards,
          ' turnCard=', turnCard,
          ' riverCard=', riverCard)
    
    for i in range (0, gameDefinition.numPlayers):
        print('Inside main. player[', i, '].cards=', players[i].cards )
        
    print('Inside main. gameRound=', gameRound)
        
    bettingAction = 'c'
    betSize = 0
    print('Inside main. player[', mySeatNumber, ']. actionState=', actionState,
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
#        players[i].position = (players[i].position - 1) % gameDefinition.numPlayers

s.close()




