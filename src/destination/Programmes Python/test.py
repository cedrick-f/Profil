def secante(a, liste_h):
	f_a = f(a)
	coefficients = [(f(a+h)-f(a))/h for h in liste_h]
	return coefficients
