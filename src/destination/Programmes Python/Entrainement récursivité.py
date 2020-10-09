'''
Soit une chaine de caractères, écrire un algorithme récursif
permettant de déterminer sa longueur
'''
def longueur_chaine(mots):
	if len(mots) != 0:
		return 1 + longueur_chaine(mots[1:])
	else:
		return 0
print(longueur_chaine("Ca roule ma poule ?"))

'''
Pour convertir un nombre entier positif N de la base décimale à 
la base binaire, il faut opérer par des divisions successives du 
nombre N par 2. Les restes des divisions constituent la 
représentation binaire.
Ecrire une fonction récursive « Binaire » permettant d’imprimer à 
l’écran la représentation binaire d’un nombre N.
'''
def binaire(N):
    if N == 0:
        return []
    return binaire(N//2)+[N % 2]
 
print(binaire(13))

'''
La suite de Fibonacci
Ecrire un programme récursif calculant Fib(n)
'''
def Fibonacci(n):
        if n < 2:
                return 1
        return Fibonacci(n-1)+Fibonacci(n-2)
print(Fibonacci(4))

'''
Ecrire un programme récursif permettant de calculer le nème terme de la suite:
Un = 3U(n-1)+U(n-2), lorsque n < 2.
'''

def unbordel(n):
        if n < 2:
                return 1
        else:
                return 3*unbordel(n-1)+unbordel(n-2)
print(unbordel(6))

'''
Un nombre N est pair si (N-1) est impair, et un nombre N est impair si (N-1) est pair.
Ecrire deux fonctions récursives mutuelles pair(N) et impair(N)
permettant de savoir si un nombre N est pair et si un nombre N est impair.
'''

def pair(N):
        if N%2 == 1 or N%2 == 0
