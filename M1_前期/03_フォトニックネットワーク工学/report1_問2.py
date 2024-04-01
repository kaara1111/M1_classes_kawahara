import math
def order_1st():
    x1_lst, x3_lst, x5_lst = [], [], []
    for i in range(100):
        x1 = (i+5/4)*math.pi - 3/(2*math.pi*(4*i+5))
        x3 = (i+9/4)*math.pi - 35/(2*math.pi*(4*i+9))
        x5 = (i+13/4)*math.pi - 99/(2*math.pi*(4*i+13))

        if x1 > 0:
            x1_lst.append([i, x1])
        if x3 > 0:
            x3_lst.append([i, x3])
        if x5 > 0:
            x5_lst.append([i, x5])

    print("1-th order approximation:")
    print("x1:", sorted(x1_lst, key=lambda x:x[1])[:4])
    print("x3:", sorted(x3_lst, key=lambda x:x[1])[:4])
    print("x5:", sorted(x5_lst, key=lambda x:x[1])[:4])

def order_0th():
    x1_lst, x3_lst, x5_lst = [], [], []
    for i in range(100):
        x1 = (i+5/4)*math.pi
        x3 = (i+9/4)*math.pi
        x5 = (i+13/4)*math.pi

        if x1 > 0:
            x1_lst.append([i, x1])
        if x3 > 0:
            x3_lst.append([i, x3])
        if x5 > 0:
            x5_lst.append([i, x5])
    
    print("0-th order approximation:")
    print("x1:", sorted(x1_lst, key=lambda x:x[1])[:4])
    print("x3:", sorted(x3_lst, key=lambda x:x[1])[:4])
    print("x5:", sorted(x5_lst, key=lambda x:x[1])[:4])

def main():
    order_0th()
    order_1st()

if __name__ == '__main__':
    main()