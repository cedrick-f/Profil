class Point:
    def __init__(self, x, y, z):    # méthode "constructeur"
        self.x = x      #
        self.y = y      # attributs: coordonnées
        self.z = z      #

    def __repr__(self):    # méthode pour l'affichage
        return "P(%.4f, %.4f, %.4f)" %(self.x, self.y, self.z)



#Q1:
from math import *
def distance(P1, P2):
    return sqrt((P2.x-P1.x)**2+(P2.y-P1.y)**2+(P2.z-P1.z)**2)
print(distance(Point(1, 3, -2), Point(2, 4, -1)))
    



class Vecteur:
    def __init__(self, x, y, z):    # méthode "constructeur"
        self.x = x      #
        self.y = y      # attributs : coordonnées
        self.z = z      #
        
    def __repr__(self):    # méthode pour l'affichage
        return "P(%.4f, %.4f, %.4f)" %(self.x, self.y, self.z)

#Q2:
def __add__(self, v):
    x1 = self.x
    y1 = self.y
    z1 = self.z
    x2 = v.x
    y2 = v.y
    z2 = v.z
    return (x1 + x2, y1 + y2, z1 + z2)

U = Vecteur(1,6,-8)
Y = Vecteur(1,8,-8)
print(__add__(U, Y))

#Q3:
def __sub__(self, v):
    x1 = self.x
    y1 = self.y
    z1 = self.z
    x2 = v.x
    y2 = v.y
    z2 = v.z
    return (x1 - x2, y1 - y2, z1 - z2)

U = Vecteur(1,6,-8)
Y = Vecteur(1,8,-8)
print(__sub__(U, Y))

'''
def __abs__(u):
    x = u.x
    y = u.y
    z = u.z
    return abs(u)

U = Vecteur(1,6,-8)
print(__abs__(U))
'''

def __neg__(u):
    x = u.x
    y = u.y
    z = u.z
    return (-x, -y, -z)

U = Vecteur(1,6,-8)
print(__neg__(U))

def __mul__(k, u):
    x1 = k.x
    y1 = k.y
    z1 = k.z
    x2 = u.x
    y2 = u.y
    z2 = u.z
    return (x1*x2, y1*y2, z1*z2)

U = Vecteur(1,6,-8)
Y = Vecteur(1,8,-8)
print(__mul__(U, Y))


