from random import randint

vies = 10
nbr_essais = 1
nombre_mystere = randint(1, 100)
nbr_propose = 0

print("Vous avez 10 tentatives pour deviner le nombre mystère sans le dépasser")

while nbr_propose != nombre_mystere and nbr_essais <= 10:
    print("Essais numéro : ", nbr_essais)
    nbr_propose = int(input("Donnez un nombre entier entre 1 et 100 : "))
    if nbr_propose < nombre_mystere:
    	print("Trop petit")
    elif nbr_propose == nombre_mystere:
    	print("Bravo ! Vous avez trouvé",nombre_mystere,"en",nbr_essais,"essai(s)")
    elif nbr_essais > 10 and nbr_propose != nombre_mystere :
	    print("Perdu ! Il fallait trouver ",nombre_mystere)
    else:
    	break
    nbr_essais += 1
print("Perdu ! Il fallait trouver ", nombre_mystere)