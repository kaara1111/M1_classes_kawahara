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
    _2P1 = affine_double(1,1,13,0,1)
    _3P1 = affine_sum(1,1,13,0,1,_2P1[0],_2P1[1])
    _4P1 = affine_double(1,1,13,_2P1[0],_2P1[1])
    _5P1 = affine_sum(1,1,13,0,1,_4P1[0],_4P1[1])

    _2P2 = affine_double(1,-1,13,1,1)
    _3P2 = affine_sum(1,-1,13,1,1,_2P2[0],_2P2[1])
    _4P2 = affine_double(1,-1,13,_2P2[0],_2P2[1])
    _5P2 = affine_sum(1,-1,13,1,1,_4P2[0],_4P2[1])

    print("2P1 = ",_2P1)
    print("3P1 = ",_3P1)
    print("4P1 = ",_4P1)
    print("5P1 = ",_5P1)

    print("2P2 = ",_2P2)
    print("3P2 = ",_3P2)
    print("4P2 = ",_4P2)
    print("5P2 = ",_5P2)

if __name__ == '__main__':
    main()