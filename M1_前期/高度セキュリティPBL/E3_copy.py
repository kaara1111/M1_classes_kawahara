# def get_modulo(a,b,p):
#     return (a*b)%p

# def extended_gcd(a, b):
#     A = [a, b]
#     X = [1, 0]
#     Y = [0, 1]
#     i=1
#     while A[-1]!=0:
#         q = A[i-1]//A[i]
#         a_next = A[i-1]-A[i]*q
#         x_next = X[i-1]-q*X[i]
#         y_next = Y[i-1]-q*Y[i]
#         A.append(a_next)
#         X.append(x_next)
#         Y.append(y_next)
#         i+=1
#     return A[i-1], X[i-1], Y[i-1]

# def get_inv(p1, g1):
#     d, x, y = extended_gcd(p1, g1)
#     inv = y%p1
#     return d, x, y, inv

def Mod(a, b):
    return a%b

def ModBinary(g, k, p):
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

def main():
    # modulo = get_modulo(13, 8, 53)
    # print("3*5 mod 7 =", modulo)
    modulo = ModBinary(281, 995, 997)
    print("281^995 mod 997 =", modulo)
    modulo = ModBinary(23, 17, 47)
    print("17^23 mod 47 =", modulo)

if __name__=="__main__":
    main()