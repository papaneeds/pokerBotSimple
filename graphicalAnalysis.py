#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Created on Sat Mar 31 15:13:45 2018

@author: tompokerlinux
"""
import matplotlib.pyplot as plt

'''
This function plots out a matrix and shows it with a colourbar beside it.
It is based on the code in the example at:
    https://stackoverflow.com/questions/3529666/matplotlib-matshow-labels
'''
def plotMatrix(myMatrix):

    fig = plt.figure()
    # custom_map = custom_div_cmap(5, mincol='r', midcol='g' ,maxcol='b')
    ax = fig.add_subplot(111)
    cax = ax.matshow(myMatrix)
    fig.colorbar(cax)

    plt.show()

