#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 11:02:04 2018

@author: tompokerlinux
"""

import treys
import preFlopValue
import numpy as np
import matplotlib.pyplot as plt

# Define a map between the suits and a number for indexing into an array
INDEX_CHAR_SUIT_TO_INT_SUIT = {
        's': 0,  # spades
        'h': 1,  # hearts
        'd': 2,  # diamonds
        'c': 3,  # clubs
}
NUM_SUITS = 4
NUM_CARDS_IN_DECK = 52

def probabilityMatrix(numIterations, numPlayers, numBoardCards, debug=False):

    # A 2-d array of NUM_CARDS_IN_DECK * NUM_CARDS_IN_DECK to hold
    # the probabilities   
    probabilities = np.zeros((NUM_CARDS_IN_DECK, NUM_CARDS_IN_DECK)) 
    visited = np.full((NUM_CARDS_IN_DECK, NUM_CARDS_IN_DECK), False, dtype=bool)
    
    for rank1 in treys.Card.STR_RANKS:
        for suit1, val1 in treys.Card.CHAR_SUIT_TO_INT_SUIT.items():
            card1 = treys.Card.new(rank1 + suit1)
            i = (treys.Card.CHAR_RANK_TO_INT_RANK[rank1])*NUM_SUITS \
                + INDEX_CHAR_SUIT_TO_INT_SUIT[suit1]
            for rank2 in treys.Card.STR_RANKS:
                for suit2, val2 in treys.Card.CHAR_SUIT_TO_INT_SUIT.items():
                    j = (treys.Card.CHAR_RANK_TO_INT_RANK[rank2])*NUM_SUITS \
                        + INDEX_CHAR_SUIT_TO_INT_SUIT[suit2]
                    if (not((rank1 == rank2) & (suit1 == suit2))):
                        # The probabilities are symmetric about (i=j). So,
                        # if you've already calculated the probability then
                        # just fill it in
                        if (visited[j,i]):
                            probabilities[i,j] = probabilities[j,i]
                        else:
                            card2 = treys.Card.new(rank2 + suit2)
                            p1_hand = [card1, card2] 
                            if (debug):
                                print('i=', i, ' j=', j)
                                treys.Card.print_pretty_cards(p1_hand)
                            winners = preFlopValue.getOdds(p1_hand, numIterations, 
                                                       numPlayers, numBoardCards)
                            probabilities[i,j] = winners[0] 
                            visited[i,j] = True

    return probabilities

# This function returns the index of a particular card
# The card is defined as a string like 'As' or '2c' or 'Td'
def getIndexFromCard(cardAsString):
    # Find the rank and suit of the card
    rank1 = cardAsString[0]
    suit1 = cardAsString[1]
    index = (treys.Card.CHAR_RANK_TO_INT_RANK[rank1])*NUM_SUITS \
        + INDEX_CHAR_SUIT_TO_INT_SUIT[suit1]  
    return index    