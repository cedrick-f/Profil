#IMPORTS
############################
import keyboard
import time

#CONSTANTES
############################

S = ["la pierre", "le papier", "les ciseaux", "le lézard", "Spock"]
V = ["écrase", "émousse", "enveloppe", "discrédite", "coupent", "décapitent", "empoisonne", "mange", "casse", "vaporise"]

F = [[0, 3, 0, 0, 10],
     [0, 0, 5, 7, 0],
     [2, 0, 0, 0, 9],
     [1, 0, 6, 0, 0],
     [0, 4, 0, 8, 0],]

#VARIABLES GLOBALES
############################

def plusFortQue(s1, s2):
    """ Renvoie
            True si s1 est stirctement supérieur à s2
            False si s2 est strictement supérieur à s1
            None s'ils sont égaux
        s1 et s2 sont des nombres allant de 0 à 4
    """
    if s1 == s2:
        return
    return F[s2][s1] > 0

def resultat(s1, s2):
    """ Renvoie la phrase donnant le résultat d'un "coup"
        ATTENTION : s1 est le gagnant sur s2
    """
    return S[s1] + " " + V[F[s2][s1]-1] + " " + S[s2]

j = 0 #ou 1
score = [0, 0]

def afficherScore(score):
    print("Joueur 1 : ",score[0], " - Joueur 2 : ", score[1])

def analyse(s1, s2):
    r = plusFortQue(s1, s2)
    if r is None:      #Match nul
        print("Match Nul")
    else:
        if r:
            score[0] += 1
            print(resultat(s2, s1))
        else:
            score[1] += 1
            print(resultat(s1, s2))
        afficherScore(score)

def changerJoueur():
    global j
    j = 1-j

def convertir(key):
    """A, B, C, D, E --> 0, 1, 2, 3, 4
    """
    return ord(key.upper()) - 65
    
def acquerir():
    """ Interroge l'utilisateur qui doit taper :
            A, B, C, D, E
            Echap
        S'il tape autre chose : aucun effet
        Sinon la fonction renvoie :
            0, 1, 2, 3, 4
            -1
    """
    key = "P"
    time.sleep(0.2)
    print(">>>")   #Invite
    while not key in "ABCDE":
        key = keyboard.read_key(suppress=True).upper()
        time.sleep(0.2) # permet d'éviter de détecter plusieurs appuis sur la touche
        if key == "ESC":
            return -1
    return convertir(key)

def fin():
    s1 = acquerir()
    changerJoueur()
    s2 = acquerir()
    print(s1, s2)
    analyse(s1, s2)
print(fin())
