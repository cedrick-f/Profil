# valeurs des pièces
systeme_monnaie = [100, 50, 20, 10, 5, 2, 1]
# liste des pièces à rendre
lst_pieces = []
# indice de la première pièce comparer à la somme à rendre
i = 0
# definition de la somme à rendre
somme_a_rendre = int(input("Somme à rendre ? "))

def algo_glouton(systeme_monnaie, lst_pieces, i, somme_a_rendre):
	while somme_a_rendre != 0:
		if systeme_monnaie[i] <= somme_a_rendre:
			lst_pieces.append(systeme_monnaie[i])
			somme_a_rendre = somme_a_rendre - systeme_monnaie[i]
		else:
			i = i + 1
	return lst_pieces

print("Vous allez devoir rendre les pièces", algo_glouton(systeme_monnaie, lst_pieces, i, somme_a_rendre))
