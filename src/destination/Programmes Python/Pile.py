from listes_chainees import *

class Pile:
    
    def __init__(self):
        self._liste = ListeC()
    
    def __repr__(self):
        return self._liste.__repr__()
        
    def est_vide(self): #Renvoie True si la liste est vide
        return self._liste.est_vide()
    
    def push(self, nouvel_element):
        return self._liste.ajouter_debut(nouvel_element)
        
    def pop(self):
        return self._liste.supprimer_debut()
    
    
if __name__ == "__main__":
    
    #### C'EST BON LA PIZZA ####
    
    # p = Pile()
    # p.push("pâte à pizza")
    # print(p.pop())
    # p.push("sauce tomate")
    # print(p.pop())
    # p.push("jambon")
    # print(p.pop())
    # p.push("mozzarella")
    # print(p.pop())
    # p.push("tranche d'ananas")
    # print(p.pop())
    # p.push("fromage râpé")
    # print(p.pop())
    # print(p._liste)
    
    #### PARENTHESE DE MES DEUX ####
    
    

    expression = "[-(b)+sqrt(4*(a*c)])/(2*a)"
    print(parenthesesdemesdeux(expression))