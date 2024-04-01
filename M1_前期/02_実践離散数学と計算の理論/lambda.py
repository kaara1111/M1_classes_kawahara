#0~3の整数値の定義
zero = lambda f: lambda x: x
one = lambda f: lambda x: f(x)
two = lambda f: lambda x: f(f(x))
three = lambda f: lambda x: f(f(f(x)))
######pythonで定義した演算で出力結果を表示するための関数##############
def print_nat(nat):
    print(nat(lambda n: n+1)(0))
##################################################################
#後継者関数succの定義
succ = lambda n: lambda f: lambda x: f(n (f)(x))
plus = lambda m: lambda n:(m (succ))(n)
mult = lambda m: lambda n: lambda f: m(n (f))
exp = lambda m: lambda n: n(mult (m))(one)
print("succ(2) = ", end="")
print_nat(succ(two))
print("succ(1) = ", end="")
print_nat(succ(one))
print()
#加算の定義

print("2+3 = ", end="")
print_nat(plus(two)(three))
print("0+1 = ", end="")
print_nat(plus(zero)(one))
print()
#乗算の定義

print("2*3 = ", end="")
print_nat(mult(two)(three))
print("0*2 = ", end="")
print_nat(mult(zero)(two))
print()
#べき乗算の定義

print("2^3 = ", end="")
print_nat(exp(two)(three))
print("0^2 = ", end="")
print_nat(exp(zero)(two))
print("3^0 = ", end="")
print_nat(exp(three)(zero))
print()