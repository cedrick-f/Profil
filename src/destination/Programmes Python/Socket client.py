#IMPORTS
##########################################
import socket

#CREATION OBJET SOCKET CLIENT
########################################
connexion_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_serveur.connect(('localhost', 63000))

connexion_serveur.send(bytes("Serveur es-tu là ??????", "utf-8"))

message = connexion_serveur.recv(1024)
print(message.decode())

continuer = "oui"
while continuer != "fin":
    connexion_serveur.send(bytes(input("Quel méssage envoyer ?\n"), "utf-8"))
    


connexion_serveur.close()