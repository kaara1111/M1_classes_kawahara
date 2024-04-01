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

def main():
    p = 2**(256)-2**(224)+2**(192)+2**(96)-1
    n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
    b = int("0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b",16)
    gx = int("0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296",16)
    gy = int("0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5",16)
    k = 172350919665451459123451714499640833062234544321

    kgx,kgy = mod_aff_ec_exp(-3,gx,gy,k,p)
    print(kgx,kgy)

    kgx,kgy = mod_aff_ec_exp(0,4,0,5,5)
    print(kgx,kgy)

if __name__ == '__main__':
    main()