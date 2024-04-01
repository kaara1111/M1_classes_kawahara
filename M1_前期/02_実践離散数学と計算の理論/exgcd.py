import sympy

def exgcd(a, b):
    return sympy.gcdex(a, b)

if __name__ == '__main__':
    print(exgcd(25, 11))
    print((-298375%(32*25*11)))