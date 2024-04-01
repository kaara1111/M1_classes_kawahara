import math
import random
import hashlib
import binascii

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

def ec_elgamal_key_gen(a,x0,y0,p,x):
    gx,gy = aff_ec_exp(a,x0,y0,x,p)
    return gx,gy

def ec_elgamal_enc(m,a,x0,y0,pubx,puby,p,r):
    U = aff_ec_exp(a,x0,y0,r,p)
    V = aff_ec_exp(a,pubx,puby,r,p)
    c = m^V[0]
    return U,c

def ec_elgamal_dec(C,a,x,p):
    V = aff_ec_exp(a,C[0][0],C[0][1],x,p)
    m = V[0]^C[1]
    return m

# shake256(m, ℓ)
# Input: 文字列： m, 出力のビット長 :ℓ
# Output: 整数： mのハッシュ値
def shake256(m, l):
    hash_size = (l//8 +10)
    m1 = hashlib.shake_256(m.encode()).digest(hash_size)
    m2 = int.from_bytes(m1, byteorder='big')
    Hm = m2 >> (m2.bit_length()-l+1)
    return Hm

# MGF(Message Generation Function) mgf(D, oLen)
# Input: データ(16 進文字列) : D, 出力バイト長 : oLen
# Output: D の MGF 出力値 (16進文字列)
def mgf(D, oLen):
    if len(D) % 2 == 1:
        D = '0' + D
    m = binascii.unhexlify(D)
    return hashlib.shake_128(m).hexdigest(oLen)

def xor(a, b):
    return hex(int(a, 16) ^ int(b, 16))[2:]

# def OAEP_enc(m,a,G,SK,PK,p,k0,k1,k2):
# メッセージ (16 進バイト列):m < ℓ (ℓ はベースポイントの位数), OAEP 乱数バイト長 k0, パディングバイト長
# k1, メッセージバイト長: k2, 曲線パラメータ: a, ベースポイント: G = (x0, y0), 公開鍵: Y = (pubx, puby), 法: p, 楕円
# ElGamal 暗号用乱数: r1 < ℓ, OAEP 用乱数 (k0 バイト 16 進バイト列): r2
def ec_elgamal_oaep_enc(m,k0,k1,k2,a,x0,y0,pubx,puby,p,r1,r2):
    Gr = mgf(r2, k1+k2)
    s = xor(Gr, m + '0'*(2*k1))
    Hs = mgf(s, k0)
    t = xor(Hs, r2)
    w = int(s + t,16)

    U,c = ec_elgamal_enc(w,a,x0,y0,pubx,puby,p,r1)
    return U,c

def ec_elgamal_oaep_dec(C,k0,k1,k2,a,x,p):
    k = k0 + k1 + k2
    w = ec_elgamal_dec(C,a,x,p)
    s = hex(w)[2:][:2*(k1+k2)]
    t = hex(w)[2:][2*(k1+k2):2*k]
    r = xor(mgf(s,k0), t)
    z = xor(mgf(r,k1+k2), s)
    m = z[:2*k2]
    chk = z[2*k2:]
    if chk == '0'*(2*k1):
        return m
    else:
        return "Decryption Error"


def main():
    n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
    a = -3
    b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
    gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
    p = 2**256-2**224 + 2**192 + 2**96-1
    k0,k1,k2 = 8,8,16

    SK = 27077763127661076507477261512997103447780673270796970849255477399292372780398
    PK = (84546812694622314234645652022815970258631217784135599287049648644983010139605, 62074767048292746179747235898686980422491711536393340602868877577748039401698)


    # PK = ec_dsa_key_gen((gx,gy),SK,a,p)
    # print("PK = ",PK)
    
    # m = random.randint(1,2**(8*k2)-1)
    # m = 322181488134327915440142334459385904422
    m = "8a97adebda4bc65e072c25a870dd939e"
    r1 = 94942963219160478645616456847425949118405414797801813963145265022204180576071
    r2 = hex(14454421632045786768)[2:]
    # C = OAEP_enc(m,a,(gx,gy),SK,PK,p,k0,k1,k2)
    C = ec_elgamal_oaep_enc(m,k0,k1,k2,a,gx,gy,PK[0],PK[1],p,r1,r2)
    print(C)

    # m_dec = OAEP_dec(U,c,a,SK,p,k0,k1,k2)
    m_dec = ec_elgamal_oaep_dec(C,k0,k1,k2,a,SK,p)
    print(m_dec)


if __name__ == '__main__':
    main()