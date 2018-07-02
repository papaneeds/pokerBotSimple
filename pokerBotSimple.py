#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 10:14:14 2018

@author: tompokerlinux
"""

import gameUtilities 
import preFlopOddsBot
import expectedValueBot
import os  
import socket
import sys
import treys

# This function handles the hand changes
def handleHandChange(previousHandNumber, handNumber, gameDefinition, players,
                     historicalHandsFile, handEvaluator, handString,
                     playerCumulativeWinnings) :
    
    # If the hand has incremented then reset the variables that are used
    # to keep track of this hand
    if (handNumber > 0):      

        lastActionInPreviousHands = gameUtilities.lastActionInPreviousHands(handString)
        
        print('Inside handleHandChange. len(lastActionInPreviousHands)=', len(lastActionInPreviousHands))
        
        for lastActionInPreviousHand in lastActionInPreviousHands:
        
            print('\r\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\r\n')
            print('There is a new hand. previousHandNumber=', previousHandNumber,
                  ' currentHandNumber=', handNumber, 
                  ' lastActionInPreviousHand=', lastActionInPreviousHand)
        
            # decode anything that happened in the last hand
            print('Decoding lastActionInPreviousHand')
            [myPosition, boardCards, actionState, \
             handRound, previousHandNumber, firstToActThisRoundSeat, Error] \
             = gameUtilities.decode(lastActionInPreviousHand, 
                                    gameDefinition, players, False)
            print('Finished decoding lastActionInPreviousHand')
       
            mySeatNumber = gameUtilities.getSeatNumber(myPosition, previousHandNumber,
                                                       gameDefinition.numPlayers)
        
            print('For the previous hand mySeatNumber=', mySeatNumber,
                  ' myPosition=', myPosition, 
                  ' previousHandNumber=', previousHandNumber,
                  'numPlayers=', gameDefinition.numPlayers)  
                                   
            # Save the historical values from this hand inside the player's
            # historical data
            historicalHandsFile.write('============================================\n')
            historicalHandsFile.write('Finished handNumber=' + str(previousHandNumber) + '\n')
            outputString = 'myPosition=' + str(myPosition) + '\n'
            outputString += 'mySeatNumber=' + str(mySeatNumber) + '\n'
            historicalHandsFile.write(outputString)

            print('myPosition=', str(myPosition))
            print('mySeatNumber=' + str(mySeatNumber))
        
            # Figure out who won.
            # If everyone folded but a single player then the non-folding player won
            numFolded = 0
            indexOfLastNonFoldedSeat = 0
            numTies = 0
            winner = [0] * gameDefinition.numPlayers
        
            for seatNumberCounter in range (0, gameDefinition.numPlayers):
                if (players[seatNumberCounter].folded):
                    numFolded += 1
                else:
                    indexOfLastNonFoldedSeat = seatNumberCounter
        
            if (numFolded == (gameDefinition.numPlayers - 1)):
                if (indexOfLastNonFoldedSeat == mySeatNumber):
                    print(' I win because everyone else folded!')
                    winner[mySeatNumber] = 1
                    numTies = 0
                else:
                    print(' Player in seat=', indexOfLastNonFoldedSeat, 
                          ' wins because everyone else folded')
                    winner[indexOfLastNonFoldedSeat] = 1
                    numTies = 0
            else:            
                # Get each player's hand rank. You  use the hand rank to figure
                # out who won the hand
            
                boardCardsAsString = ''
                for i in (boardCards):
                    boardCardsAsString = boardCardsAsString + i
                
                print('boardCards=', boardCardsAsString)
                boardCardsAsTreys = gameUtilities.cardStringToTreysList(boardCardsAsString)
                playerCards = [[]] * gameDefinition.numPlayers
            
                for seatNumberCounter in range (0, gameDefinition.numPlayers): 
                    print('player ', seatNumberCounter, 
                          ' cards=', players[seatNumberCounter].holeCards,
                          ' folded=', players[seatNumberCounter].folded,
                          ' foldedHandRound=', players[seatNumberCounter].foldedHandRound)
                    # If the player has folded then set their hole cards to blanks.
                    # This will cause the gameUtilities.findWinners function to rank
                    # this player's hand at the worst possible value (and they won't win
                    # the hand)
                    holeCards = ''
                    if (players[seatNumberCounter].folded):
                        print('player=', seatNumberCounter, ' folded. setting holeCards to nothing')
                        holeCards = ''
                    else:
                        print('player=', seatNumberCounter, ' did not fold. setting holeCards to ', players[seatNumberCounter].holeCards)
                        holeCards = players[seatNumberCounter].holeCards
                        
                    #[numCards, cardsAsList] = gameUtilities.cardStringToList(holeCards)                   
                    playerCards[seatNumberCounter] = gameUtilities.cardStringToTreysList(holeCards)
                
                # Evaluate this hand
                numTies = gameUtilities.findWinners(True, handEvaluator, 
                                                        gameDefinition.numPlayers, 
                                                        playerCards, boardCardsAsTreys, winner)

            if (numTies > 0):
                print('There is a ', numTies+1, ' way split pot')
            else:
                print('The pot is won by a single player')
                
            # Calculate the pot size
            pot = gameUtilities.getPot(players)
            print('pot=', pot)
            
            # Now, divvy up the pot
            for seatNumber in range(0, len(winner)):
                playerCumulativeWinnings[seatNumber] = \
                    playerCumulativeWinnings[seatNumber] + \
                    players[seatNumber].stackSize - players[seatNumber].handStartingStackSize \
                    + winner[seatNumber]*pot
                
                print('seatNumber ', seatNumber, ' wins ', winner[seatNumber]*100, 
                      ' percent of the pot. Player has stackSize=', players[seatNumber].stackSize,
                      ' and cumulative winnings of ', playerCumulativeWinnings[seatNumber])
                print('seatNumber ', seatNumber, ' folded=', players[seatNumber].folded, ' in handRound=', players[seatNumber].foldedHandRound)
        
            for seatNumberCounter in range (0, gameDefinition.numPlayers):
                players[seatNumberCounter].addCurrentHandToHistoricalInfo()
                historicalHandsFile.write('*******Data for player in seatNumber=' + str(seatNumberCounter) + ':\n')
                historicalHandsFile.write(players[seatNumberCounter].currentHandAsString())
                players[seatNumberCounter].currentHandAsString
        
            handString = gameUtilities.lastAction(handString) + '\r\n'
            
    return [handString, previousHandNumber]

# main program starts here

# Turning socketComms = False allows you to define input strings for debugging
socketComms = False

print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))

if (len(sys.argv) != 5) :
    print('Error. invalid arguments')
    print('Usage: pokerBotSimple.py gameFile IP port <botType>')
    print('   where <botType> is one of preFlopOddsBot|expectedValueBot')
    sys.exit(1)

gameDefinitionFilename = sys.argv[1]
HOST = sys.argv[2]   
PORT = int(sys.argv[3]) 
botType = sys.argv[4]

if (not ((botType == 'preFlopOddsBot') | (botType == 'expectedValueBot'))):
    print('Error: you entered <botType>=', botType )
    print('  Allowed values of <botType> is one of reFlopOddsBot|expectedValueBot')

print ('The game definition file is ', gameDefinitionFilename)
print ('The IP address to connect to is ', HOST)
print ('The port to connect to is ', PORT)
print ('The botType is ', botType)

# read in the game definition file
serverDirectory        = '/home/tompokerlinux/Documents/project_acpc_server/'
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

if (botType == 'preFlopOddsBot'):
    bot = preFlopOddsBot.PreFlopOddsBot(gameDefinition.numPlayers, 
                                        threshold, 
                                        dataDirectory)
elif (botType == 'expectedValueBot'):
    bot = expectedValueBot.ExpectedValueBot(gameDefinition.numPlayers, 
                                             threshold, 
                                             dataDirectory)
    
print ('Finished creating bot=', bot.name)
        
# create the players for the game
players = list()
for i in range (0, gameDefinition.numPlayers):
    print("Inside main. creating player=", i, 
          'startingStack=', gameDefinition.startingStack[i])
    # Start at handNumber = 0
    players.insert(i, gameUtilities.Player(i, gameDefinition, 0))
    print('players[',i,'].stackSize=', players[i].stackSize)
    
#    Once you've got that sorted out then move on to the end of hand
#    play and how you store the values of the current hand (cards, bet, stack)
#    in the historical list of values.
print ('players[0].stackSize=', players[0].stackSize)

# Create a list to hold the player winnings (needed for the ACPC because the player's
# stacks are reset after every hand)
playerCumulativeWinnings = [0] * gameDefinition.numPlayers

# Create the hand evaluator that will tell you who won a hand
handEvaluator = treys.Evaluator()

# start communicating with the dealer
if (socketComms):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    versionString = "VERSION:2.0.0\r\n"
    s.send(versionString.encode('utf-8'))
   
previousHandNumber = -1
    
cont= True
dataIn = ''
handString = ''

while (cont == True):

    print('=======================================')
    print('Inside main. Just before receiving data')

    if (socketComms):
        dataIn = s.recv(16384)
        dataString = dataIn.decode('utf-8')
        # The ACPC server indicates that the hand is over by sending a zero length dataString
        if (len(dataString) == 0):
            print(' Received zero length dataString from socket. Game is over')
            cont = False
            # In order to process the last hand you have to make a "fake" hand that 
            # increments the hand number.
            print(' Creating a fake dataString so that the last hand can be processed')
            dataString = 'MATCHSTATE:0:' + str(previousHandNumber + 2) + ':c:KcQd||\r\n'
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
        #dataString = 'MATCHSTATE:1:123:cr16943fc/cc/r17077r18184f:|4cQc|/Ts3c8s/Kc\r\nMATCHSTATE:0:124::3h4c||\r\nMATCHSTATE:0:124:c:3h4c||\r\n'
        #dataString = 'MATCHSTATE:1:0:r20000c///:5d5c|9hQd/8dAs8s/4h/6d\r\nMATCHSTATE:0:1::6sKs|\r\n'
        #dataString = 'MATCHSTATE:1:0:cfc/cc/cr2376f:|9hQd|/8s4h6d/5s\r\nMATCHSTATE:0:1::Ks6h||\r\n'
        #dataString = 'MATCHSTATE:2:2:r20000cc///:Jh7c|Kd7d|Kh3h/8d2c9h/Ts/Kc\r\nMATCHSTATE:1:3::|JhKd|\r\nMATCHSTATE:1:3:r12384:|JhKd|\r\n'
        #dataString ='MATCHSTATE:2:257:cr17261cf/r18594r19956r20000:||7h6s/4s6c3s\r\nMATCHSTATE:2:257:cr17261cf/r18594r19956r20000c//:2dAs|2c5c|7h6s/4s6c3s/Qc/5h\r\nMATCHSTATE:1:258::|7sQh|\r\nMATCHSTATE:1:258:f:|7sQh|\r\nMATCHSTATE:1:258:ff:|7sQh|\r\nMATCHSTATE:0:259::Kh4s||\r\nMATCHSTATE:0:259:c:Kh4s||\r\n'
        #dataString = 'MATCHSTATE:1:0:r12172r20000fc///:5d5c|9hQd|8dAs/8s4h6d/5s/Js\r\nMATCHSTATE:0:1::Ks6h||\r\n'
        dataString = 'MATCHSTATE:1:2:cr19472f:|2h4c\r\nMATCHSTATE:0:3:c:KcQd||\r\n'
        previousHandNumber = -1

    print('Length of dataString numBytes=', len(dataString), '\r\ndataString=', dataString)
    handString = handString + dataString
    print('         handString=', handString)

    handNumber = gameUtilities.getHandNumber(handString)
    print('handNumber =', handNumber, ' previousHandNumber=', previousHandNumber)
    
    # Check to see if the hand has changed, and, if it has then handle it
    # by evaluating who is the winner and writing historical values out to file
    [handString, previousHandNumber] = handleHandChange(previousHandNumber, handNumber, gameDefinition, players,
                     historicalHandsFile, handEvaluator, handString, playerCumulativeWinnings)  
    
    # Check to see if this is the last hand.
    # If it is the last hand then stop reading from the socket and clean up.
    if (cont == False):
        break
    
    # Reset the values for this hand
    for seatNumberCounter in range (0, gameDefinition.numPlayers):
        players[seatNumberCounter].resetCurrentState(handNumber, gameDefinition)
    
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
                                             players,
                                             gameDefinition.blinds)
     
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




