#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
outil_profils.py : OUTIL D'ADMINISTRATEUR (à ne PAS installer sur les postes ni dans l'exe).

    python outil_profils.py genkey                 # crée la paire de clés (UNE SEULE FOIS)
    python outil_profils.py verifier profils.json  # contrôle le contenu (et la signature si .sig présent)
    python outil_profils.py signer   profils.json  # contrôle puis crée profils.json.sig

La clé PRIVÉE (cle_privee_stp.pem, protégée par un mot de passe) reste chez vous : jamais sur les
postes élèves, jamais dans le dépôt. La clé PUBLIQUE s'affiche : collez-la dans CLE_PUBLIQUE
(profils_externes.py), puis recompilez UNE fois. Ensuite, mettre à jour profils.json ne demande
plus de recompilation : modifier, `verifier`, `signer`, copier les deux fichiers.
"""
import base64
import getpass
import os
import sys

from Cryptodome.PublicKey import ECC
from Cryptodome.Signature import eddsa

import profils_externes as pe

CLE_PRIVEE = "cle_privee_stp.pem"


def genkey():
    if os.path.exists(CLE_PRIVEE):
        sys.exit("%s existe déjà : je ne l'écrase pas." % CLE_PRIVEE)
    mdp = getpass.getpass("Mot de passe pour protéger la clé privée : ")
    if len(mdp) < 8 or mdp != getpass.getpass("Confirmez : "):
        sys.exit("Mot de passe trop court (8 caractères minimum) ou différent.")
    cle = ECC.generate(curve = "ed25519")
    with open(CLE_PRIVEE, "wt") as f:
        f.write(cle.export_key(format = "PEM", passphrase = mdp, protection = "PBKDF2WithHMAC-SHA1AndAES128-CBC"))
    print("\nClé privée écrite dans %s : GARDEZ-LA HORS DES POSTES (clé USB chiffrée, coffre...)." % CLE_PRIVEE)
    print("\nClé PUBLIQUE à coller dans CLE_PUBLIQUE (profils_externes.py) :\n")
    print(cle.public_key().export_key(format = "PEM"))


def _lire(chemin):
    with open(chemin, "rb") as f:
        contenu = f.read()
    try:
        import json
        groupes = pe.valider(json.loads(contenu.decode("utf-8")))
    except (pe.ProfilsError, ValueError) as exc:
        sys.exit("CONTENU REFUSÉ : %s" % exc)
    print("Contenu valide : %d groupe(s)" % len(groupes))
    for g in groupes:
        print("  - %-25s %2d élément(s)%s" % (g["nom"], len(g["elements"]), "" if g["coche_par_defaut"] else "  (non coché par défaut)"))
    return contenu


def verifier(chemin):
    contenu = _lire(chemin)
    sig = chemin + ".sig"
    if os.path.isfile(sig):
        try:
            with open(sig, "rb") as f:
                pe.verifier_signature(contenu, f.read(1000), pe.CLE_PUBLIQUE)
            print("Signature VALIDE (clé publique de profils_externes.py)")
        except pe.ProfilsError as exc:
            sys.exit("SIGNATURE REFUSÉE : %s" % exc)
    else:
        print("Pas de signature (%s)." % sig)


def signer(chemin):
    contenu = _lire(chemin)
    if not os.path.isfile(CLE_PRIVEE):
        sys.exit("%s introuvable (lancez d'abord genkey, ou placez-vous dans le bon dossier)." % CLE_PRIVEE)
    try:
        with open(CLE_PRIVEE) as f:
            cle = ECC.import_key(f.read(), passphrase = getpass.getpass("Mot de passe de la clé privée : "))
    except ValueError:
        sys.exit("Mot de passe incorrect.")
    signature = eddsa.new(cle, "rfc8032").sign(contenu)
    with open(chemin + ".sig", "wb") as f:
        f.write(base64.b64encode(signature))
    print("Signature écrite : %s.sig\nCopiez %s ET %s.sig à côté de stp.exe." % (chemin, chemin, chemin))
    verifier(chemin)


COMMANDES = {"genkey": (genkey, 0), "verifier": (verifier, 1), "signer": (signer, 1)}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDES or len(sys.argv) - 2 != COMMANDES[sys.argv[1]][1]:
        sys.exit(__doc__)
    COMMANDES[sys.argv[1]][0](*sys.argv[2:])
