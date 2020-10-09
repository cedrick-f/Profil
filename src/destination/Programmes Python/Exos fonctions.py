def g1(x):
    g1 = 3*x+2/x
    return g1
print(g1(3))


def g2(x, a, b):
    g2 = a*x+b/x
    return g2
print(g2(3, 3, 2))


def table(n):
    for i in range(0, 11):
        j = i*n
        print(i, " x ", n, " = ", j)
print(table(7))


def table2(n, debut, fin, pas):
    for h in range(debut, fin, pas):
        m = n*h
        print(h, " x ", n, " = ", m)
print(table2(7, 2, 13, 2))


def f(x):
    return 5*x**3 + 3*x -1
def evaluer(fct, b_inf, b_sup, n_eval):
    c = b_inf
    n = 10
    d = (b_sup - b_inf)/n
    c = c+d
    for d in range(n):
        print("f(", fct(x), ") = ", n_eval)
print(evaluer(f, 3, 7, 10))