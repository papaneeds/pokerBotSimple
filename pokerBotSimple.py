#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 10:14:14 2018

@author: tompokerlinux
"""

import gameUtilities 
import preFlopOddsBot
import os  
import socket
import sys

# main program starts here

# Turning socketComms = False allows you to define input strings for debugging
socketComms = True

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
gameDefinition         = gameUtilities.readGameDefinition(serverDirectory + gameDefinitionFilename)

# open a file to save the historical hands to
historicalHandsFilename = '/home/tompokerlinux/Documents/pokerBot/pokerBotSimple.txt'
historicalHandsFile = open(historicalHandsFilename, 'w')

#print('Inside main. gameType=', gameDefinition.gameType)
#print('Inside main. numPlayers=', gameDefinition.numPlayers)
#print('Inside main. numRounds=', gameDefinition.numRounds)
#print('Inside main. startingStack=', gameDefinition.startingStack)
#print('Inside main. blinds=', gameDefinition.blinds)
#print('Inside main. firstToAct=', gameDefinition.firstToAct)

# create the bot for the game
threshold = (1.1/gameDefinition.numPlayers) # fold all hands than a random chance + 0.1 of winning
#cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))
dataDirectory = dir_path + '/data/' # This is where the pre-computed probability files are
bot = preFlopOddsBot.PreFlopOddsBot(gameDefinition.numPlayers, 
                                    threshold, 
                                    dataDirectory)
# create the players for the game
players = list()
for i in range (0, gameDefinition.numPlayers):
    print("Inside main. creating player=", i, 
          'startingStack=', gameDefinition.startingStack[i])
    players.insert(i, gameUtilities.Player(i, gameDefinition.startingStack[i]))
    print('players[',i,'].stackSize=', players[i].stackSize)
    
#    Once you've got that sorted out then move on to the end of hand
#    play and how you store the values of the current hand (cards, bet, stack)
#    in the historical list of values.
print ('players[0].stackSize=', players[0].stackSize)

# start communicating with the dealer
HOST = sys.argv[2]   
PORT = int(sys.argv[3]) 
if (socketComms):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    versionString = "VERSION:2.0.0\r\n"
    s.send(versionString.encode('utf-8'))
   
#firstHandNumber = -1
#previousHandNumber = firstHandNumber
previousHandNumber = -1
    
cont= True
dataIn = ''
handString = ''

while (cont == True):

    print('=======================================')
    print('Inside main. Just before receiving data')

    if (socketComms):
        dataIn = s.recv(4096)
        dataString = dataIn.decode('utf-8')
        if (len(dataString) == 0):
            print(' Received zero length dataString from socked. Game is over')
            break
    else:
        # example for debugging dataString='MATCHSTATE:0:1:r11189cc/:Ks6h||/Ah3dTd'
        # example for debugging handString = 'MATCHSTATE:0:0:cr23r45fr67c/cr89c/r57r9r11r12r15c/r6r7c:Ks6h|Qs5d|Tc4d/Ah3dTd/8c/Qd'
        # example for debugging dataString = 'MATCHSTATE:0:0:c:Ks6h||'
        # example for debugging dataString = 'MATCHSTATE:2:1:r11189cc/:||Tc4d/Ah3dTd'
        # dataString = 'MATCHSTATE:0:0:cr23r45fr67c/cr89c/r57r9r11r12r15c/r6r7c:Ks6h|Qs5d|Tc4d/Ah3dTd/8c/Qd'
        # dataString = 'MATCHSTATE:2:0::||AdAs'
        # hand=0, you are position=0, position=2 has raised r1400 dataString = 'MATCHSTATE:0:0:r1400:5d5c||'
        # dataString = 'MATCHSTATE:0:0:ccr1c:AdAc||'
        # dataString = 'MATCHSTATE:0:0:ccfccf:5d5c||'
        # dataString='MATCHSTATE:1:0:r9990cf/cr11588c/cc/r16910r20000:|9hQd|/8s4h6d/5s/Js\r\nMATCHSTATE:1:0:r9990cf/cr11588c/cc/r16910r20000c:5d5c|9hQd|8dAs/8s4h6d/5s/Js\r\nMATCHSTATE:0:1::Ks6h||\r\nMATCHSTATE:0:1:c:Ks6h||\r\n'
        # dataString ='MATCHSTATE:1:0:cr1cr2r3fr4r5r6c/r7r8c/r9r10r11c/r12r13r14r15c:|9hQd|/8s4h6d/5s/Js'
        # dataString = 'MATCHSTATE:2:38:ccc/cr11052fc/cr17065c/cr18088r19194r20000f:||5d4d/9cTc8c/Kh/2c\r\nMATCHSTATE:1:39::|5h2s|\r\nMATCHSTATE:1:39:r19887:|5h2s|\r\n'
        # dataString = 'MATCHSTATE:2:11:cr2863cc/:||8h7d/2s6sQd\r\nMATCHSTATE:2:11:cr2863cc/r15333:||8h7d/2s6sQd\r\nMATCHSTATE:2:11:cr2863cc/r15333r20000:||8h7d/2s6sQd\r\n'
        #dataString = 'MATCHSTATE:0:34:fcc/cc/c:3d5c||/Js7c4s/5h\r\nMATCHSTATE:0:34:fcc/cc/cr16908:3d5c||/Js7c4s/5h\r\n'
        #dataString = 'MATCHSTATE:1:0:r12797ff:|9hQd|MATCHSTATE:0:1::Ks6h||\r\nMATCHSTATE:0:1:r1485:Ks6h||\r\n'
        dataString = 'MATCHSTATE:1:123:cr16943fc/cc/r17077r18184f:|4cQc|/Ts3c8s/Kc\r\nMATCHSTATE:0:124::3h4c||\r\nMATCHSTATE:0:124:c:3h4c||\r\n'
        previousHandNumber = 92

    print('Received numBytes=', len(dataString), '\r\ndataString=', dataString)
    handString = handString + dataString
    print('         handString=', handString)

    handNumber = gameUtilities.getHandNumber(handString)
    print('handNumber =', handNumber, ' previousHandNumber=', previousHandNumber)
    
    # If the hand has incremented then reset the variables that are used
    # to keep track of this hand
    if ((previousHandNumber != handNumber) & (handNumber > 0)):        
        lastActionInPreviousHand = gameUtilities.lastActionInPreviousHand(handString)
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        print('There is a new hand. previousHandNumber=', previousHandNumber,
              ' currentHandNumber=', handNumber, 
              ' lastActionInPreviousHand=', lastActionInPreviousHand)
        previousHandNumber = handNumber
        
        # decode anything that happened in the last hand
        print('Decoding lastActionInPreviousHand')
        [myPosition, boardCards, actionState, \
         handRound, handNumber, firstToActThisRoundSeat, Error] \
         = gameUtilities.decode(lastActionInPreviousHand, 
                                gameDefinition, players, False)

        # Figure out who won the hand
            
                       
        # Save the historical values from this hand inside the player's
        # historical data
        historicalHandsFile.write('============================================\n')
        historicalHandsFile.write('Finished handNumber=' + str(previousHandNumber) + '\n')
        outputString = 'myPosition=' + str(myPosition) + '\n'
        outputString = 'mySeatNumber=' + str(gameUtilities.getSeatNumber(myPosition, previousHandNumber, gameDefinition.numPlayers)) + '\n'
        #+ ' boardCards=' + boardCards + '\n'
        for seatNumberCounter in range (0, gameDefinition.numPlayers):
            players[seatNumberCounter].addCurrentHandToHistoricalInfo()
            historicalHandsFile.write('*******Data for player in seatNumber=' + str(seatNumberCounter) + ':\n')
            historicalHandsFile.write(players[seatNumberCounter].currentHandAsString())

            # The computer poker competition plays by "Doyle's Rule", which is
            # that the stacks are reset after every hand
            players[seatNumberCounter].setStackSize(gameDefinition.startingStack[seatNumberCounter])
        
        handString = gameUtilities.lastAction(handString) + '\r\n'
        

    # Reset the values for this hand
    for seatNumberCounter in range (0, gameDefinition.numPlayers):
        players[seatNumberCounter].resetCurrentState()
    
    # decode the message that you received
    lastActionState = gameUtilities.lastAction(handString)
    
    # gameUtilities.isItMyTurnToAct(lastActionState, gameDefinition, players)
    
    [myPosition, boardCards, actionState, \
     handRound, handNumber, firstToActThisRoundSeat, Error] \
        = gameUtilities.decode(lastActionState, gameDefinition, players, True)
    
    if (not Error):
        
        print('Time for me to act.')
        print('mySeatNumber=', gameUtilities.getSeatNumber(myPosition, handNumber, gameDefinition.numPlayers),
              ' myPosition=', myPosition,
              ' handRound=', handRound,
              ' handNumber=', handNumber,
              ' boardCards=', boardCards,
              ' (position) firstToAct[', handRound, ']=', gameDefinition.firstToAct[handRound],
              ' first to act this round (seat)=', firstToActThisRoundSeat)
        print('boardCards=', boardCards)
        
        for seatNumberCounter in range (0, gameDefinition.numPlayers):
            print('Player[', seatNumberCounter, ']=', players[seatNumberCounter].currentHandAsString())
            
        print('About to call pokerBot.')
        bettingAction = bot.getBettingAction(handNumber,
                                             handRound, 
                                             myPosition, 
                                             gameDefinition.firstToAct[handRound],
                                             gameDefinition.numPlayers,
                                             players)
        print('Finished calling pokerBot.')
    
        print('Pokerbot has decided to do: player[', myPosition, ']. actionState=', actionState,
              'bettingAction=', bettingAction)
    
        # send the action back to the server
        betString = actionState + ":" + bettingAction + '\r\n'
        print('Inside main. betString=', betString)
        dataOut=betString.encode('utf-8')

        if (socketComms):
            s.send(dataOut)
        print('Inside main. just sent the data')
        dataIn = ''
    else:
        # The actionString that you parsed was not good. Go back and get some
        # more of it
        print ('Going back and reading more data from the socket')

s.close()
historicalHandsFile.close()




