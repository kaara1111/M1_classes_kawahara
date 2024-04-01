import sympy as sp
import math
from fractions import Fraction
import random
# from Crypto.Hash import SHAKE256
import hashlib

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

# def mod_aff_ec_dbl(x1,y1,a,p):
#     _lambda = ((3*(x1**2)+a)*inv(2*y1,p))%p
#     x3 = (_lambda**2 - 2*x1)%p
#     y3 = (_lambda*(x1-x3)-y1)%p
#     return x3,y3
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

# def mod_aff_ec_exp(a,b,x0,y0,k,p):
#     x1 = x0
#     y1 = y0
#     # x1,y1 = mod_aff_ec_dbl(x1,y1,a,p)
#     k = str(bin(k))[3:]
#     for i in k:
#         if i=='1':
#             x1,y1 = mod_aff_ec_dbl(x1,y1,a,p)
#             x1,y1 = affine_sum(a,b,p,x0,y0,x1,y1)
#         else:
#             x1,y1 = mod_aff_ec_dbl(x1,y1,a,p)
#     return x1,y1

def prime_factor(n):
    return sp.factorint(n)

def ec_dsa_key_gen(G,x,a,p):
    Y = aff_ec_exp(a,G[0],G[1],x,p)
    return Y

def ec_dsa_sign(m,x,G,l,r,a,p):
    shake = shake256(m,l.bit_length())
    U = aff_ec_exp(a,G[0],G[1],r,p)
    u = U[0]%l
    if u == 0:
        r = random.randint(1,l-1)
        return ec_dsa_sign(m,x,G,l,r,a,p)
    v = (inv(r,l)*(shake+x*u))%l
    if v == 0:
        r = random.randint(1,l-1)
        return ec_dsa_sign(m,x,G,l,r,a,p)
    return u,v

def ec_dsa_verify(signature,m,Y,G,l,a,p):
    shake = shake256(m,l.bit_length())
    d = inv(signature[1],l)
    mdG = aff_ec_exp(a,G[0],G[1],(shake*d)%l,p)
    udY = aff_ec_exp(a,Y[0],Y[1],(signature[0]*d)%l,p)
    U = aff_ec_add(mdG[0],mdG[1],udY[0],udY[1],p)
    return U[0]%l == signature[0]

# shake256(m, ℓ)
# Input: 文字列： m, 出力のビット長 :ℓ
# Output: 整数： mのハッシュ値
def shake256(m, l):
    hash_size = (l//8 +10)
    m1 = hashlib.shake_256(m.encode()).digest(hash_size)
    m2 = int.from_bytes(m1, byteorder='big')
    Hm = m2 >> (m2.bit_length()-l+1)
    return Hm

def main():
    n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
    a = -3
    b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
    gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
    p = 2**256-2**224 + 2**192 + 2**96-1
    print(prime_factor(n))
    print(gx,gy)
    print(aff_ec_exp(a,gx,gy,n, p))

    m = "98521615734197693183829763553364238171997077546103137167081630932682443865550"
    x = 1135216157341976932567891234567891234567891234567891234567891232567891234
    r = 66540815278985542449375626814020809618003608689798961265876446336936734967749

    Y = ec_dsa_key_gen((gx,gy),x,a,p)
    signature = ec_dsa_sign(m,x,(gx,gy),n,r,a,p)
    print(signature)
    print(f"verify = {ec_dsa_verify(signature,m,Y,(gx,gy),n,a,p)}")


if __name__ == '__main__':
    main()