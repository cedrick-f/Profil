liste = [-8, -6, -3, -1, 4, 7, 12, 13, 18, 20, 31, 33, 48, 59, 72, 73, 80]

def recherche_dichotomique(liste, valeur):
    deb = liste[0]
    fin = len(liste)-1
    mil = (deb+fin)//2
    while deb <= fin:
        if liste[mil] == valeur :
            return mil
        else:
            if liste[mil] >= valeur :
                fin = mil-1
            else :
                deb = mil+1
            mil = (deb+fin)//2
    return deb

print(recherche_dichotomique(liste, 31))