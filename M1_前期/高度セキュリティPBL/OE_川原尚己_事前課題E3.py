# -*- coding: utf-8 -*-
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
    
    
    