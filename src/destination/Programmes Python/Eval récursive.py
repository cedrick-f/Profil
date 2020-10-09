#Q3:
def compte_a(chaine):
   if len(chaine) == 1:
      if chaine[0] == 'a' : 
         return 1
      else : 
         return 0
   else :
      if chaine[0] == 'a': 
         return 1 + compte_a(chaine[1:])
      else : 
         return compte_a(chaine[1:])
 
print (compte_a('blabla')) # affiche 2
print (compte_a('dur')) # affiche 0


#Q4:
def appartient_a(l, e):
    if len(l) == 0:
        return False
    if e not in l[0]:
        return False or appartient_a(l[1:], e)
    else:
        return True
print(appartient_a("i did it !", "e"))
