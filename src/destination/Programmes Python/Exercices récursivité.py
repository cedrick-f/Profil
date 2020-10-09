def f(a, b) :
   """ a et b sont deux entiers naturels non nuls """
   if b == 1 :
      return a
   return a + f(a, b-1)
print(f(3, 5))

print("Le résultat est 15")
print("Le cas de base est b != 1")
print("Dans les appels récursifs, le programme fini par s'arrêter grâce à une condition")
print("f(a, b) retourne b*a")

#############################################################################

def nb_occurrences(s, c):
    if len(s) != 0:
        if s[0] == c:
            return 1 + nb_occurrences(s[1:], c)
        else:
            return nb_occurrences(s[1:], c)
    else:
        return 0

print(nb_occurrences("coucou", "c"))

#############################################################################

import pylab
F = pylab.gca() # F peut être vue comme un objet ’figure’
 
def cercle(x, y, r):
   """ cercle de centre (x,y) et de rayon r """
   # création du cercle:
   cir = pylab.Circle([x, y], radius = r, fill = False)
   # ajout du cercle à la figure :
   F.add_patch(cir)
 
def CerclesRec(x, y, r):
   """ construction récursive de la figure """
   cercle(x, y, r)
   if r > 1:
       if x >= 0:
          CerclesRec(x+3*r/2, y, r/2)
       if y >= 0:
          CerclesRec(x, y-3*r/2, r/2)
       if x <= 0:
          CerclesRec(x-3*r/2, y, r/2)
       if y <= 0:
          CerclesRec(x, y+3*r/2, r/2)
 
# appel de la fonction CerclesRec
CerclesRec(0, 0, 8)
 
# pour placer toute la figure dans un repère orthonormé :
pylab.axis('scaled')
# affichage de la figure :
pylab.show()

print("cette fonction ne s'appellera pas un nombre fini de fois car il faut atteindre r<1 pour que la fonction s'arrête.")
print("on obtiendra plus de cercles.")
