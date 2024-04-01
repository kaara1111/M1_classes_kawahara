# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 19:52:14 2021

@author: laplacian
"""

def binary(g,k):
    bk = bin(k)[2:]
    y = 1
    for i in bk:
        if i == '1':
            y = (y*y)*g
        else:
            y = y*y        
    return y

def main():
    y = binary(23, 17)
    print("binary(23,17)=", y)
    y = binary(13, 8)
    print("binary(13,8)=", y)
    y = binary(5, 31)
    print("binary(5,31)=", y)
    y = binary(7, 41)
    print("binary(7,41)=", y)

if __name__=="__main__":
    main()