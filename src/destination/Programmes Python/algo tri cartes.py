#on cherche 1
#regarder chaque nombre jusqu'a trouver 1
#prendre le 1 et le placer  dans la liste 2
#recommencer pour tous les autres nombre en ajoutant 1 au nombre recherché précédent

#on cherche la carte à la valeur la plus petite
#prendre cette carte et la placer dans la liste 3
#recommencer en mettant les plus petites valeurs dans la liste 3 les unes apres les autres

On prend le premier nombre de la liste


from random import randint
L = [5, 4, 3, 7, 1, 9, 10, 6, 2, 8]
def tri_insertion(cartes):
    l = len(cartes)
    for i in len(cartes):
        n = cartes[0]
        p = i
        while p > 0 and cartes[p - 1] > n:
            cartes[p] = cartes[p - 1]
            p = p-1
        cartes[p] = n
    return cartes
#print(trinsertion(L))

def tri_selection(cartes):
    taille = len(cartes)
    for u in taille:
        min = u
        for h in taille:
            if 
    return cartes
print(tri_selection(Z=[randint(1, 10) for s in range(5)]))