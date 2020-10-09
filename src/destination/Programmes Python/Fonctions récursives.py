def factorielle_r(x):
    if x > 0:
        return x * factorielle_r(x-1)
    else:
        return 1
print(factorielle_r(4))
        
def factorielle_nr(y):
    r=1
    for i in range(1, y+1):
        r = r*i
    return r
print(factorielle_nr(4))

def som2entiersnat_r(a, b):
    if b > 0:
        b -= 1
        a += 1
        return som2entiersnat_r(a, b)
    else:
        return a
print(som2entiersnat_r(2, 8))


def som2entiersnat_rr(a, b):
    if b > 0 :
        b -= 1
        a += 1
        return som2entiersnat_r(a, b) 
    else:
        return a
    if b < 0:
        b += 1
        a += 1
        return som2entiersnat_r(a, b)
    else:
        return a
    if b == 0:
        return a
print(som2entiersnat_rr(-4, 8))

def palindromedesesmorts(mot):
    if len(mot) < 2:
        return True
    else:
        return (mot[0] == mot[-1]) and palindromedesesmorts(mot[1:-1])

print(palindromedesesmorts("OOFOO"))
