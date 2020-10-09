import socket

#msgfin = 'fini'
HOST_pair = #mettre l'IP d'un ordi en chaîne de caractère
PORT_pair = 63000

connexion_pair = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connextion_pair.settingtimeout(1)
try:
    adresse_pair = (HOST_pair, PORT_pair)
    print("Tentative de connexion à", adresse_pair, "...")
    connexion_pair.connect(adresse_pair)

except socket.timeout:
    print(adresse_pair, "n'est pas démarré : c'est moi le serveur !"
    ecoute = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ecoute.bind((' ', PORT_pair))
    ecoute.listen()
    print("Attente d'une connexion...")
    connexion_pair, adresse_pair = ecoute.accept()
    ecoute.close()
    
    
print("Connexion établie avec", adresse_pair)

connexion_pair.close()