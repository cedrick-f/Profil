#exo 105 page 109
liste = [10**i for i in range(0, -6, -1)]
print(liste)
x = float(input("Rentrez x : "))

def f(x):
	f=x**3+2*x**2-x+4
	return f
print(f(x))

a = float(input("Entrez a : "))
def secante(a, liste_h):
	f_a = f(a)
	coefficients = [(f(a+h)-f(a))/h for h in liste_h]
	return coefficients
print(secante(a, liste_h))

'''
#exo 106 page 129
def secante_2(a, liste_h):
	nb_pas = len(liste_h)
	f_a = f(a) #on evite de refaire le calcul
	coefficients = #création tableau de la bonne taille
	for idPas in range(nb_pas):
		h = ...
		coefficients[idPas] = ...
	return coefficients

#exo 107 page 129
def secante_3(a, liste_h):
	f_a = f(a)
	coefficients = [] #on crée une liste vide
	for h in liste_h:
		...
		...
	return coefficients
'''