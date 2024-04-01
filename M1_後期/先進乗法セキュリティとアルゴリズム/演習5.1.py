import math
import random

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

def aff_ec_add(x1, y1, x2, y2, p):
    if x1 == math.inf:
        return (x2, y2)
    elif x2 == math.inf:
        return (x1, y1)
    elif x1%p == x2%p and y1%p == -y2%p:
        return (math.inf, math.inf)
    # lam = Fraction((y2-y1)%p, (x2-x1)%p)%p
    lam = ((y2-y1)*inv(x2-x1,p))%p
    x3 = (lam**2 - x1 - x2)%p
    y3 = (lam*(x1-x3) - y1)%p
    return (x3%p, y3%p)

def aff_ec_dbl(x1, y1, a, p):
    if y1 == math.inf or y1%p == 0:
        return (math.inf, math.inf)
    # t = Fraction((3*x1**2+a)%p, 2*y1%p)%p
    t = ((3*(x1**2)+a)*inv(2*y1,p))%p
    x2 = (t**2 - 2*x1)%p
    y2 = (t*(x1-x2) - y1)%p
    return (x2%p, y2%p)

def aff_ec_exp(a, x0, y0, k, p):
    if k == 0:
        return (math.inf,math.inf)
    if k < 0:
        return aff_ec_exp(a, x0, -y0, -k, p)
    (x, y) = (math.inf, math.inf)
    bk = bin(k)[2:]
    for i in bk:
        (x, y) = aff_ec_dbl(x, y, a, p)
        if i == '1':
            (x, y) = aff_ec_add(x, y, x0, y0, p)
    return (x, y)

def ec_dsa_key_gen(G,x,a,p):
    Y = aff_ec_exp(a,G[0],G[1],x,p)
    return Y

def ec_dsa_sign(m,x,G,l,r,a,p):
    # shake = shake256(m,l.bit_length())
    U = aff_ec_exp(a,G[0],G[1],r,p)
    u = U[0]%l
    if u == 0:
        r = random.randint(1,l-1)
        return ec_dsa_sign(m,x,G,l,r,a,p)
    v = (inv(r,l)*(m+x*u))%l
    if v == 0:
        r = random.randint(1,l-1)
        return ec_dsa_sign(m,x,G,l,r,a,p)
    return u,v

def ec_dsa_verify(signature,m,Y,G,l,a,p):
    # shake = shake256(m,l.bit_length())
    d = inv(signature[1],l)
    mdG = aff_ec_exp(a,G[0],G[1],(m*d)%l,p)
    udY = aff_ec_exp(a,Y[0],Y[1],(signature[0]*d)%l,p)
    U = aff_ec_add(mdG[0],mdG[1],udY[0],udY[1],p)
    return U[0]%l == signature[0]

def main():
    x = 2
    a = 2
    b = 1
    Gx = 1
    Gy = 2
    p = 5
    l = 7
    r = 5

    # for l in range(1,10):
    #     if aff_ec_exp(a,Gx,Gy,k,p) == (math.inf,math.inf):
    #         print("l = ",l)
    #         break

    Y = ec_dsa_key_gen((Gx,Gy),x,a,p)
    print("Y = ",Y)

    xa = 3
    Ya = ec_dsa_key_gen((Gx, Gy),xa,a,p)
    print("Ya = ",Ya)
    signature = ec_dsa_sign(Ya[0],xa,(Gx,Gy),l,r,a,p)
    print("signature = ",signature)

if __name__ == '__main__':
    main()