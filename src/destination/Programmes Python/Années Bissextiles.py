annee = input("Insérez une année : ")
annee = int(annee)

if annee%4 == 0 and annee%100 != 0 or annee%400 == 0:
    print("c'est une année bissextile")
else:
    print("ce n'est pas une annee bissextile")
print(annee%4)
print(annee%100)
print(annee%400)