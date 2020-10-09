#IMPORTS
##########################################
import socket

#CREATION OBJET SOCKET SERVEUR
#########################################
connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion.bind(('', 63000))
connexion.listen()


connexion_client, adresse_client = connexion.accept()
print(adresse_client)
message = connexion_client.recv(1024)
connexion_client.send(message+bytes("\nCOUCOU TOUA", "utf-8"))

continuer = "oui"
while continuer != "fin":
    message = connexion_client.recv(1024)
    print(message.decode())
    continuer = input("Continuer ? ")
    if continuer == "oui":
        connexion_client.send(bytes(input("Quel message envoyer ?\n "), "utf-8"))
    else:
        connexion_client.close()
        connexion.close()