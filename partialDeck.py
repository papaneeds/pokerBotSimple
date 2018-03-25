#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2013 Will Drevo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Created on Sun Mar 18 12:17:00 2018

@author: tompokerlinux
TS - Modified Will Drevo's initial DECK so that partial decks could
be dealt out (in order to run simulations on hand strength)
"""

# This module contains a simplified betting algorithm based entirely on
# the pre-flop calculated value of a hand
import treys
from random import shuffle as rshuffle

# This class allows you to create a Deck that doesn't have all the cards
# in it.
# The excluded cards are defined in the cardsToExclude list of Card instances
#
# This class is meant to simulate the deck after part of the deck has 
# already been dealt out (for example, after the hole cards have been dealt)
class PartialDeck:
        
    def __init__(self, cardsToExclude):
        self._PARTIAL_DECK = [] 
        self.cardsToExclude = cardsToExclude
        self.shuffle()
        
    def shuffle(self):
        # and then shuffle
        self.cards = self.GetPartialDeck(self.cardsToExclude)
        rshuffle(self.cards)
        
    def draw(self, n=1):
        if n == 1:
            return self.cards.pop(0)

        cards = []
        for i in range(n):
            cards.append(self.draw())
        return cards

    def __str__(self):
        return treys.Card.print_pretty_cards(self.cards)
        
#    @staticmethod
    def GetPartialDeck(self, cardsToExclude):
        # create the standard 52 card deck with the cardsToExclude
        # excluded
        for rank in treys.Card.STR_RANKS:
            for suit, val in treys.Card.CHAR_SUIT_TO_INT_SUIT.items():
                candidateCard = treys.Card.new(rank + suit)
                # if this is not one of the cards to exclude then
                # add it to the deck
                includeCardInDeck = True
                for card in cardsToExclude:
                    if (card == candidateCard):
                        includeCardInDeck = False
                
                if (includeCardInDeck):                 
                    self._PARTIAL_DECK.append(treys.Card.new(rank + suit))
                    
        return list(self._PARTIAL_DECK)