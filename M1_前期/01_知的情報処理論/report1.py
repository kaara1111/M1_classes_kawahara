# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 18:56:07 2023

@author: 81703
"""
import matplotlib.pyplot as plt
import numpy as np

def learn_perceptron(X, W, rho, w0, w1):
    def g(x, W):
        ret = 0
        for idx in range(len(W)):
            ret += W[idx]*x[idx]
            
        return ret
    
    continue_flag = 1
    while continue_flag:
        for x in X:
            continue_flag = 0
            if (g(x, W) >= 0 and x[-1] == 1) or (g(x, W) < 0 and x[-1] == 2):
                pass
            elif g(x, W) >= 0 and x[-1] == 2:
                #更新
                W = [W[idx] - rho*x[idx] for idx in range(len(W))]
                w0.append(W[0])
                w1.append(W[1])
                print(f"x={x[1]} update:w={W}")
                continue_flag = 1
            elif g(x, W) < 0 and x[-1] == 1:
                W = [W[idx] + rho*x[idx] for idx in range(len(W))]
                w0.append(W[0])
                w1.append(W[1])
                print(f"x={x[1]} update:w={W}")
                continue_flag = 1
    
    return W, w0, w1

def plot(w0, w1, X):
    p=np.linspace(-1, 1, 10)
    plt.plot(p, -5*p, label="w1=-5w0")
    plt.plot(p, -1*p, label="w1=-w0")
    plt.plot(p, 10*p, label="w1=10w0")
    plt.plot(p, 0.5*p, label="w1=0.5w0")
    plt.xlim(-1,1)
    plt.ylim(-1,1)
    plt.legend()

def main():
    X = [[1, 0.2, 1], [1, 1.0, 1], [1, -2.0, 2], [1, -0.1, 2]]
    W = [0.4, -0.4]
    rho = 0.3
    
    w0, w1 = [], []
    w0.append(W[0])
    w1.append(W[1])
    
    print(f"w={W}")
    W, w0, w1 = learn_perceptron(X, W, rho, w0, w1)
    print(f"learned g(x) = {W[0]}+{W[1]}x")
    print(f"border={-W[0]/W[1]}")
    
    plot(w0, w1, X)

if __name__ == "__main__":
    main()