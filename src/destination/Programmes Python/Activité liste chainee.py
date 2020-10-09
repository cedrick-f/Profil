class Maillon:
    def __init__(self):
        self.val = None
        self.suiv = None # Pas de maillon suivant

    def __repr__(self):
        return str(self.val)

class ListeC:
    def __init__(self):
        self.tete = None # Liste vide
        
    def __repr__(self):
        s = ""
        m = self.tete
        while m is not None:
            s += str(m.val)
            m = m.suiv
        return s

    def est_vide(self):
        return self.tete is None

    def taille(self): #Connaître la taille de la chaîne
        i = 0
        m = self.tete
        while m is not None:
            m = m.suiv
            i +=1
        return i
    
    def get_dernier_maillon(self): #Chopper le dernier maillon
        m = mp = self.tete
        while m is not None:
            mp = m  
            m = m.suiv  # mp =  maillon précédent m
        return mp

    def get_maillon_indice(self, i): #Chopper le maillon d'indice i
        m = self.tete
        o = 0
        if self.tete is None:
            return "La liste est vide"
        else:
            while o != i:
                m = m.suiv
                o += 1
        return m
    
    def ajouter_debut(self, nm): #Ajouter un maillon au debut
        m = self.tete
        nm.suiv = m
        self.tete = nm

    def ajouter_fin(self, nm): #Ajouter un maillon à la fin
        dernier_maillon = self.get_dernier_maillon()
        dernier_maillon.suiv = nm

    def ajouter_apres(self, i, nm): #Ajouter un maillon après i
        maillon_indice = self.get_maillon_indice(i)
        nm.suiv = maillon_indice.suiv
        maillon_indice.suiv = nm

    def supprimer_debut(self): #Supprimer le maillon du debut
        if self.tete is None:
            return "La liste est vide"
        else:
            self.tete = self.tete.suiv
        

    def supprimer_fin(self): #Supprimer un maillon à la fin
        dernier_maillon = self.get_dernier_maillon()
        
    
    '''
    def supprimer_apres(self, nm): #Supprimer un maillon après i
        
    '''
L = ListeC()
##
M1, M2, M3, M4, M5, M6 = Maillon(), Maillon(), Maillon(), Maillon(), Maillon(), Maillon()
##
M1.val = "a"
M2.val = "b"
M3.val = "c"
M4.val = "d"
M5.val = "e"
M6.val = "f"
##
M1.suiv = M2
M2.suiv = M3
M3.suiv = M4
L.tete = M1
##

print(L.get_maillon_indice(1))