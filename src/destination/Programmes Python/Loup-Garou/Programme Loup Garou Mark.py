'''
- Ajoute le nombre de joueurs total (fonction), ///
    (dictionnaire) pour chaque joueur ///
    (input) le pseudo ///
- Attribuer randomly le role (fonction)///
- Vivant = 1, spec = 0 ///
'''
####IMPORTS
import random

####LISTES
liste_noms_joueurs = []
roles = ("loup_garou", "loup_garou", "villageois", "villageois", "villageois")
roles_rand = random.sample(list(roles), nbr_joueurs)
vivant_spec = (1, 1, 1, 1, 1)

####NOMBRE DE JOUEURS
nbr_joueurs = int(input("Nombre de joueurs : "))

####NOMS DES JOUEURS
def nomsjoueurs():
    for i in range(0,nbr_joueurs):
        nom_joueur = input("Entrez le nom du joueur : ")
        liste_noms_joueurs.append(nom_joueur)
    return liste_noms_joueurs
print(nomsjoueurs())

####VIVANT/SPEC
def vivant_spect():
    

####COMPOSITION JOUEUR
compo_joueurs = zip(liste_noms_joueurs, roles_rand, vivant_spec)
print(list(compo_joueurs))

