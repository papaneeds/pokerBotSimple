#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 11:51:04 2018

@author: tompokerlinux
"""

import sys
import socket

# Server program to serve up a previous game 
# 

def readGameHistory(gameHistoryFile, numPlayers, myPlayerNumber):
    outputString = []
    
    with open(gameHistoryFile) as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content] 
        
    # look for the lines that are from the player that
    # precedes myPlayerNumber (modulo numPlayers)
    previousPlayer = (myPlayerNumber - 1) % 3
    print ('previousPlayer=', previousPlayer)
    # print('Inside readGameHistory. Game History =', content)
    tempString = ''
    for x in content[:]:
        # First, split the action along ' '
        splitStuff = x.split(' ')           
        # print(x)
        # print('len(splitStuff), splitStuff=', len(splitStuff), splitStuff)
        if ( splitStuff[0] == 'FROM'):
            playerNumber = int(splitStuff[1]) - 1 
            if (playerNumber == myPlayerNumber):
                outputString.append(tempString)
                tempString = ''
                print ('====================================')
                print ('Finished Betting Round outputString=', outputString) 

        # collect the stuff that is meant for this player
        if ( splitStuff[0] == 'TO' ):
            playerNumber = int(splitStuff[1]) - 1  
            if (playerNumber == myPlayerNumber):
                tempString = tempString + splitStuff[4] + '\r\n'
                print('Appended another item. tempString=', tempString)

    # append anything that is still hanging around in tempString
    outputString.append(tempString)   
                   
    return outputString

# main program starts here

# parse the command line arguments that tell you:
# 1. the game history file that you need to read in
# 2. what your ip address and port are
#

print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))

if (len(sys.argv) != 6) :
    print('Error. invalid arguments')
    print('Usage: dealerServer.py gameFile IP port numPlayers myPlayerNumber')
    sys.exit(1)

print ('The game history file is ', sys.argv[1])
print ('The IP address to connect to is ', sys.argv[2])
print ('The port to connect to is ', sys.argv[3])
print ('The number of players is ', int(sys.argv[4]))
print ('My player number is ', int(sys.argv[5]))

# read in the game history file
homeDirectory='/home/tompokerlinux/Documents/pokerBot/'
gameHistoryFilename=sys.argv[1]
myIpAddress = sys.argv[2]
myPort = int(sys.argv[3])
numberOfPlayers=int(sys.argv[4])
myPlayerNumber=int(sys.argv[5])
gameHistory=readGameHistory(homeDirectory + gameHistoryFilename, numberOfPlayers, myPlayerNumber)

print ('gameHistory=', gameHistory)
# Open a socket server listener 
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = (myIpAddress, myPort)
print ('starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print ('waiting for a connection')
    connection, client_address = sock.accept()
    print('connection=', connection, ' client_address=', client_address)

    try:
        print('connection from', client_address)
        gameRound = 0

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024)
            print ('received "%s"' % data)
            if data:
                data=gameHistory[gameRound].encode('utf-8')
                print ('sending gameRound=', gameRound, ' data=', data)
                connection.sendall(data)
                gameRound=gameRound+1
                if (gameRound >= len(gameHistory)):
                    print('Finished all stuff. gameRound=', gameRound)
                    break
            else:
                print ('no more data from', client_address)
                break
            
    finally:
        # Clean up the connection
        connection.close()

# Read in the previous game