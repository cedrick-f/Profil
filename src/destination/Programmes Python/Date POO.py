
class Date:
	
	#Création des variables de la date
	def __init__(self):
		self.jour = 1
		self.mois = 1
		self.annee = 0
		self.liste_mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

	#Vérification du jour donné
	def verif_jour(self, jour):
		self.jour = input("Donnez un jour : ")
		try:
			self.jour = int(self.jour)
			if self.jour > 31 or jour < 0:
				raise ValueError("Un mois ne peut pas aller en-dessous du jour 0 ou au-dessus du jour 31, et encore...")
		except ValueError:
			print("Un nombre, pas une lettre voyons !")
		return self.jour

	#Vérification du mois donné et changement du nombre d'un mois en mot
	def verif_mois(self, mois):
		self.mois = self.liste_mois[0]
		self.mois_donne = input("Donnez le nombre d'un mois : ")
		try:
			self.mois_donne = int(self.mois_donne)
			if self.mois_donne < 1 or self.mois_donne > 12:
				raise IndexError("de toute façon cette erreur ne fonctione pas...")
		except IndexError:
			print("Bah alors, on cannaît pas le nombre des mois ?")
		return self.liste_mois[self.mois_donne-1]

	#Vérification de l'année donnée
	def verif_annee(self, annee):
		self.annee = input("Donnez une année : ")
		try :
			self.annee = int(self.annee)
			if self.annee <= 0:
				raise ValueError("Désolé, on va pas avant la naissance de Jésus !")
		except ValueError():
			print("Après la naissance de Jésus stp")
		return self.annee

	#Comparaison des dates d1 et d2
	def __lt__(self, d1, d2):
		return d1 < d2

	#Représentation de l'année
	def __repr__(self):
		return "%s %s %s" %(self.verif_jour(self.jour), self.verif_mois(self.mois), self.verif_annee(self.annee))

d = Date()
