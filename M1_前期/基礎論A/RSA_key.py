import random
import math
import sympy as sp

def make_prime_number(bit_length):
    m = random.randint(2**(bit_length-1), 2**bit_length-1)
    while not sp.isprime(m):
        m = random.randint(2**(bit_length-1), 2**bit_length-1)
    return m

# def make_prime_number(bit_length):
#     m = random.randint(2**(bit_length-1), 2**bit_length-1)
#     eratosthenes_lst = eratosthenes(m)
#     if is_prime(m, eratosthenes_lst=eratosthenes_lst):
#         return m

# def eratosthenes(n):
#     # n までの自然数を列挙する
#     isPrimes = [True] * (n+1)

#     # 0 と 1 を取り除く
#     isPrimes[0], isPrimes[1] = False, False

#     # 2 から √n まで繰り返す
#     for i in range(2, int(n**0.5)+1):
#         # i が取り除かれていないとき
#         if isPrimes[i]:
#             # i の倍数を取り除く
#             for j in range(2*i, n+1, i):
#                 isPrimes[j] = False
#     return [i for i in range(2, n+1) if isPrimes[i]]

# def is_prime(n, eratosthenes_lst):
#     if n in eratosthenes_lst:
#         return True

def make_RSA_key():
    bit_length = 512
    p = make_prime_number(bit_length)
    q = make_prime_number(bit_length)
    while p==q:
        q = make_prime_number(bit_length)
    
    n = p * q
    L = int(sp.lcm(p-1, q-1))

    # e = random.randint(2, L-1)
    # while math.gcd(e, L) != 1:
    #     e = random.randint(2, L-1)
    e = 65537
    d = sp.mod_inverse(e, L)

    return n, e, d

def RSA_decrypt(c, d, n):
    m = pow(c, d, n)
    return m

def main():
    print("RSA key generator")
    n, e, d = make_RSA_key()
    print("n =", n)
    print("e =", e)
    print("d =", d)

if __name__ == "__main__":
    main()
    