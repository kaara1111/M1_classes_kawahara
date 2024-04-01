# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 13:10:52 2023

@author: 81703
"""

def Mod(a, b):
    return a%b

def mod_binary(g, k, n, p):
    y=1
    k = str(bin(k))[2:]
    for i in k:
        if i=='1':
            y = Mod(Mod(y**2, p)*g, p)
            # print(y)
        else:
            y = Mod(y**2, p)
            # print(y)
    return y

def inv(a, n):
    # return a^-1 mod n
    return mod_binary(a, n-2, len(str(bin(n-2))[2:]) , n)

def affine_sum(a,b,p,x1,y1,x2,y2):
    _lambda = ((y2-y1)*inv(x2-x1,p))%p
    x3 = (_lambda**2 - x1 - x2)%p
    y3 = (_lambda*(x1-x3)-y1)%p
    return x3,y3

def affine_double(a,b,p,x1,y1):
    _lambda = ((3*(x1**2)+a)*inv(2*y1,p))%p
    x3 = (_lambda**2 - 2*x1)%p
    y3 = (_lambda*(x1-x3)-y1)%p
    return x3,y3

def main():
    x3, y3 = affine_double(0, 1, 5, 0, 2)
    print(x3, y3)

if __name__=="__main__":
    main()