import random
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

def mod_aff_ec_dbl(x1,y1,a,p):
    _lambda = ((3*(x1**2)+a)*inv(2*y1,p))%p
    x3 = (_lambda**2 - 2*x1)%p
    y3 = (_lambda*(x1-x3)-y1)%p
    return x3,y3

def mod_aff_ec_exp(a,x0,y0,k,p):
    x1 = x0
    y1 = y0
    # x1,y1 = mod_aff_ec_dbl(x1,y1,a,p)
    k = str(bin(k))[3:]
    for i in k:
        if i=='1':
            x1,y1 = mod_aff_ec_dbl(x1,y1,a,p)
            x1,y1 = affine_sum(a,0,p,x0,y0,x1,y1)
        else:
            x1,y1 = mod_aff_ec_dbl(x1,y1,a,p)
    return x1,y1

def ec_elgamal_key_gen(a,x0,y0,p,x):
    gx,gy = mod_aff_ec_exp(a,x0,y0,x,p)
    return gx,gy

def ec_elgamal_enc(m,a,x0,y0,pubx,puby,p,r):
    U = mod_aff_ec_exp(a,x0,y0,r,p)
    V = mod_aff_ec_exp(a,pubx,puby,r,p)
    c = Mod(m^V[0],p)
    return U,c

def ec_elgamal_dec(C,a,x,p):
    pass

def main():
    p = 2**256 - 2**224 + 2**192 + 2**96-1
    print(p)
    n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
    b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
    gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5

    x = 125792089210356248262697496949407573629996953224135760348422359061668512044368
    Y = ec_elgamal_key_gen(-3,gx,gy,p,x)
    print("x.bit_length() = ",x.bit_length())

    new_x = random.randint(2*255,2**256-1)
    new_Y = ec_elgamal_key_gen(-3,gx,gy,p,new_x)
    print("new_x.bit_length() = ",new_x.bit_length())
    print("new_x = ",new_x)
    print(new_Y)
    print("Y.bit_length() = ",Y[0].bit_length())
    print("Y.bit_length() = ",Y[1].bit_length())

    # mattiu's public key
    Y = (41580501048180933804086954770861484953913883768479524984438533091468338605057, 79707205083508359684418760286040227478361997870485160379416467476575427557536)

    m = "curry"
    m = int(binascii.hexlify(m.encode("utf-8")),16)
    r = 125791083210356248262297496149407573629896953223142762348422359561568512144273
    U,c = ec_elgamal_enc(m,-3,gx,gy,Y[0],Y[1],p,r)
    print(hex(U[0]),hex(U[1]))
    print(hex(c))

if __name__ == '__main__':
    main()