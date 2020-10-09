L = [45, 54, 87, 13, 54, 5, 56, 78]
def maximum(L):
    m = L[0]
    for e in L:
        if e > m:
            m = e
    return m
#print(maximum(L))


def moyenne(L):
    s = 0
    for e in L:
        s = s + e
    s = s/len(L)
    return s
#print(moyenne(L))
#ou aussi possible comme ça :
def somme2(L):
    w = sum(L)/len(L)
    return w
#print(somme2(L))

def somme(L):
    v = 0
    for e in L:
        v = v+e
    return v
#print(somme(L))

def compter(chaine, lettre):
    n = 0
    for l in chaine:
        if l == lettre:
            n += 1
    return n
#print(compter("Numérique et Sciences Informatiques !", "m"))

def separer(liste, seuil):
    liste1, liste2 = [], []
    for n in liste:
        if n <= seuil:
            liste1.append(n)
        else:
            liste2.append(n)
    return liste1, liste2
#print(separer([45, 21, 56, 12, 1, 8, 30, 22, 6, 33], 30))

#liste, nombre, nproche, diff_v_abs, diff_v_abs_actu
def plus_proche(liste, nombre):
    nproche = liste[0]
    diff_v_abs = abs(nombre - nproche)
    for p in liste:
        diff_v_abs_actu = abs(nombre-p)
        if diff_v_abs_actu < diff_v_abs:
            nproche = p
            diff_v_abs = diff_v_abs_actu
    return nproche
print(plus_proche([45, 21, 56, 12, 1, 8, 30, 22, 6, 33], 20))