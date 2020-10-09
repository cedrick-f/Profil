#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
 
####################################################################################
# Déclaration des Types
####################################################################################
class Maillon():
    def __init__(self, data = None):
        self.data = data
        self.suiv = None # adresse (en Python, on pointe directement vers un Maillon)
 
    def __repr__(self):
        return self.data.__repr__()
 
 
    # Structures récursives
    def taille_suite(self):
        if self.suiv is None:
            return 1
        return 1+self.suiv.taille_suite()
 
 
    def get_dernier_suite(self):
        if self.suiv is None:
            return self
        return self.suiv.get_dernier_suite()
 
 
####################################################################################
class ListeC():
    def __init__(self):
        self.debut = None # adresse (en Python, on pointe directement vers un Maillon)
 
    def __repr__(self):
        m = self.debut
        l = []
        while m is not None:
            l.append(m.__repr__())
            m = m.suiv
        return " ".join(l)
 
 
    def est_vide(self):
        """ Renvoie True si la liste est vide
        """
        return self.debut is None
 
 
    def taille(self):
        """ Renvoie le nombre de maillons de la liste
        """
        m = self.debut
        l = 0
        while m is not None:
            l += 1
            m = m.suiv
        return l
 
 
    def taille_r(self):
        """ Renvoie le nombre de maillons de la liste
            Version récursive
        """
        if self.est_vide():
            return 0
        return self.debut.taille_suite()
 
 
    ############################################################################
    def get_dernier(self):
        """ Renvoie le dernier maillon de la liste
            IndexError si la liste est vide
        """
        if self.est_vide():
            raise IndexError("list index out of range")
        m = self.debut
        while m.suiv is not None:
            m = m.suiv
        return m
 
 
    def get_dernier_r(self):
        """ Renvoie le dernier maillon de la liste
            IndexError si la liste est vide
            Version récursive
        """
        if self.est_vide():
            raise IndexError("list index out of range")
        return self.debut.get_dernier_suite()
 
 
    def get_maillon_indice(self, i):
        """ Renvoie le maillon d'indice i
            IndexError si l'indice ne pointe pas dans la liste
        """
        m = mp = self.debut
        j = 0
        while j <= i:
            if m is None:
                raise IndexError("list index out of range")
            mp = m
            m = m.suiv
            j += 1
        return mp
 
    ############################################################################
    def ajouter_fin(self, nM):
        """ Ajoute un maillon à la fin de la liste
            Si nM n'est pas de type Maillon, le maillon est créé
            Renvoie le maillon ajouté
        """
        if not isinstance(nM, Maillon):
            nM = Maillon(nM)
        if self.est_vide():
            self.debut = nM
        else:
            dm = self.get_dernier()
            dm.suiv = nM
        return nM
 
 
    def ajouter_debut(self, nM):
        """ Ajoute un maillon au début de la liste
            Si nM n'est pas de type Maillon, le maillon est créé
            Renvoie le maillon ajouté
        """
        if not isinstance(nM, Maillon):
            nM = Maillon(nM)
        if self.est_vide():
            self.debut = nM
        else:
            nM.suiv = self.debut
            self.debut = nM
        return nM
 
 
    def inserer_apres(self, i, nM):
        """ Insère un maillon après le maillon d'indice i
            Si nM n'est pas de type Maillon, le maillon est créé
            IndexError si l'indice ne pointe pas dans la liste
            Renvoie le maillon ajouté
        """
        m = self.get_maillon_indice(i)
        if m is None:
            raise IndexError("list index out of range")
        nM.suiv = m.suiv
        m.suiv = nM
        return nM
 
 
    ############################################################################
    def supprimer_debut(self):
        """ Supprime et renvoie le premier maillon de la liste
            IndexError si la liste est vide
        """
        if self.debut is not None:
            d = self.debut
            self.debut = self.debut.suiv
            return d.data
        else:
            raise IndexError("list index out of range")
 
 
    def supprimer_fin(self):
        """ Supprime et renvoie le dernier maillon de la liste
            IndexError si la liste est vide
        """
        if self.est_vide():
            raise IndexError("list index out of range")
        m = self.debut
        a = None                # avant dernier
        while m.suiv is not None:
            a = m
            m = m.suiv
        if a is None:
            self.debut = None
            return
        else:
            a.suiv = None
            return a.data
 
 
    def supprimer_indice(self, i):
        """ Supprime le Maillon d'indice i de la liste
            IndexError si l'indice ne pointe pas dans la liste
        """
        if self.est_vide():
            raise IndexError("list index out of range")
        if i > 0:
            m = self.get_maillon_indice(i-1)
            if m.suiv is None:
                raise IndexError("list index out of range")
            m.suiv = m.suiv.suiv
        else:
            self.supprimer_debut()
 
 
 
    ############################################################################
    def renverser(self):
        """ Inverse la liste "sur place"
        """
        m = self.debut      # adresse maillon courant
        p = None         # prochaine adresse à écrire
 
        while m is not None:
            s = m.suiv # adresse maillon suivant
            m.suiv = p
            p = m
            m = s
 
        self.debut = p
 
 
    ############################################################################
    def concatener(self, L):
        """ Concaténation la liste avec une autre Liste L
            Ne renvoie rien : modification de la liste "sur place"
        """
        d = self.get_dernier()
        d.suiv = L.debut
 
 
    ############################################################################
    def __add__(self, L):
        """ Concaténation la liste avec une autre Liste L
            Renvoie une nouvelle liste
        """
        nL = ListeC()
        nL.debut = self.debut
        nL.concatener(L)
        return nL
 
 
if __name__ == "__main__":
    L1 = ListeC()
    L1.ajouter_fin(1)
    L1.ajouter_fin(Maillon(2))
    L1.ajouter_fin(Maillon(3))
    print(L1)
 
    L1.supprimer_indice(0)
    print(L1)