from random import randint

class Jeu:
    #Création de X dés avec X faces
    def __init__(self, nbr_des = 3, nbr_faces = 6):
        self.des = [De(nbr_faces) for _ in range(nbr_des)]

    #Ecriture du tirage obtenue
    def __repr__(self):
        return " ".join(num_des)
    
   
    
    #Lancement des dés pour obtenir [X, X, X]
    def lancer(self, *num_des):
        for num in num_des:
            self.des[num].lancer()
        return self.des
        

##

class De:
    #Création d'une variable contenant le nombre de faces
    def __init__(self, nbr_faces = 6):
        self.nbr_faces = nbr_faces
        self.set_valeur(0)

    #Ecriture du dé
    def __repr__(self):
        if not self.est_pose():
            return "_"
            
        if self.est_bloque():
            b = "x"
        else:
            b = " "
        return b + chr(0x267F + self.get_valeur())
    
    #Vérifie si un dé est posé
    def est_pose(self):
        return self._valeur != 0
      
    #Vérifie si un dé est bloqué
    def est_bloque(self):
        return self._valeur < 0
    
    #Lancement d'un dé
    def lancer(self):
        if self.est_bloque():
            return False
        else:
            val = randint(1, self.nbr_faces)
            self.set_valeur(val)
            return True
    
    def set_valeur(self, val):
        self._valeur = val
        
    def get_valeur(self):
        return abs(val)

    #bloquer ou débloquer un dé lancé
    def bloquer(self):
        if self.est_bloque() or not self.est_pose():
            return False
        else:
            self._valeur = -1 * val  
            return True 

j = Jeu()
d = De()

print(j.lancer())

