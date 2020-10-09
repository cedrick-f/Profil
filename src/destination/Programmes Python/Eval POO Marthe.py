
class Utilisateur:
    def __init__(self, nom, prenom, email, civilite):
        self.nom = str(nom)
        self.prenom = str(prenom)
        self.email = str(email)
        self.civilite = civilite

        if self.civilite == 1:
            self.civilite = "Mme"
        else:
            self.civilite = "M"
    
    def __repr__(self):
        return "%s %s %s (%s)" %(self.civilite, self.prenom, self.nom, self.email)
 
U = Utilisateur("LEFEVRE", "Robert", "bob.smith@gmail.com", 2)       
print(U)


class Grille:
    def __init__(self, w, h):
        self._grille = [["-"]]
        self.w = w
        self.h = h
        for _ in range(w):
            self._grille.append(["-"])
    
    def __repr__(self):
        return self._grille

G = Grille
print(G(1, 2))


class Fraction:
    def __init__(self, num, den):
        self.num = num
        self.den = den
    
    def __repr__(self):
        return ""
    
    def __mul__(self, f1, f2):
        mul_num = f1.num * f2.num
        mul_den = f1.den * f2.den
        return "%s \n -- \n %s" %(self.mul_num, self.mul_den)
    
    def __add__(self, f1, f2):
        self.add_num = f1.num + f2.num
        self.add_den = f1.den + f2.den
        return "%s \n -- \n %s" %(self.add_num, self.add_den)


f1 = Fraction(3, 4)
f2 = Fraction(1, 3)
print(f1+f2)