age = input("Veuillez insérer votre âge : ")
age = int(age)

if age < 16:
    print("vous n'avez pas le droit d'accéder à cette séance !")
    #inférieur à 16 ans
elif age >= 16 and age <= 18 or age >= 65:
    print("Vous avez le droit d'accéder à cette séance en payant un tarif réduit")
    #supérieur à 16 ans et tarif réduit
elif age >= 16 and age > 18 or age < 65:
    print("Vous avez le droit d'accéder à cette séance en payant un tarif plein")
    #supérieur à 16 et tarif plein