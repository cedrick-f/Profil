#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verif_credentials.py : vérifie qu'une restauration de credentials (mode 4) est exacte.

`cmdkey /list` n'affiche pas les mots de passe. Ce script les compare via leur
EMPREINTE (SHA-256 du contenu brut) : le fichier d'empreintes ne contient aucun secret,
et la comparaison porte sur les octets exacts (pas seulement sur le texte affiché).

SÉCURITÉ : il ne touche QUE les credentials dont le nom commence par STP_TEST_.

Scénario complet (à lancer depuis le dossier src, avec stp.py en mode DEBUG) :

    python verif_credentials.py creer       # crée 3 credentials de test + enregistre leurs empreintes
    (dans STP : saisir un mot de passe, cocher le groupe de test, Sauvegarder)
    python verif_credentials.py supprimer   # simule une session vierge
    (dans STP : Restaurer, avec le même mot de passe)
    python verif_credentials.py verifier    # compare avec les empreintes enregistrées

Autres commandes :
    figer       enregistre les empreintes des STP_TEST_* déjà présentes (ex. créées avec cmdkey)
    afficher    affiche les mots de passe EN CLAIR des STP_TEST_* (données de test uniquement !)
"""
import hashlib
import json
import os
import sys

from windows_credential_manager import (delete_credential, list_credentials,
                                        write_credential)

PREFIXE = "STP_TEST_"
FICHIER_EMPREINTES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "stp_test_empreintes.json")

# Credentials de test : texte simple, accents et symbole, contenu NON textuel (longueur impaire)
ECHANTILLONS = {
    "STP_TEST_texte":   dict(username="alice", comment="texte simple", blob="Mot2Passe!".encode("utf-16-le")),
    "STP_TEST_accents": dict(username="bob",   comment="accents",      blob="é€ ç œ ñ – 日本".encode("utf-16-le")),
    "STP_TEST_binaire": dict(username="carol", comment="binaire",      blob=bytes([0, 255, 1, 2, 3])),
}


def _etat() -> dict:
    """{nom: {utilisateur, commentaire, persistance, empreinte}} des STP_TEST_ présentes."""
    return {e.target_name: {"utilisateur": e.username,
                            "commentaire": e.comment,
                            "persistance": e.persist,
                            "octets": len(e.blob),
                            "empreinte": hashlib.sha256(e.blob).hexdigest()}
            for e in list_credentials(PREFIXE + "*")
            if e.target_name.upper().startswith(PREFIXE)}


def _enregistrer(etat: dict):
    with open(FICHIER_EMPREINTES, "w", encoding="utf-8") as f:
        json.dump(etat, f, indent=2, ensure_ascii=False)
    print("Empreintes enregistrées (%d credentials) : %s" % (len(etat), FICHIER_EMPREINTES))


def _alerte_vides(etat: dict):
    vides = [nom for nom, v in etat.items() if v["octets"] == 0]
    if vides:
        print("\nATTENTION : contenu VIDE pour : " + ", ".join(vides))
        print("  Soit ces credentials n'ont vraiment pas de mot de passe, soit le contenu n'est pas lu :")
        print("  vérifiez que list_credentials renseigne bien  blob = raw  (windows_credential_manager.py).")
    return vides


def creer():
    for nom, c in ECHANTILLONS.items():
        write_credential(nom, c["username"], "", c["comment"], blob=c["blob"])
    etat = _etat()
    # Auto-test : ce que le module relit doit être EXACTEMENT ce qui vient d'être écrit
    for nom, c in ECHANTILLONS.items():
        if nom not in etat or etat[nom]["empreinte"] != hashlib.sha256(c["blob"]).hexdigest():
            _alerte_vides(etat)
            sys.exit("ÉCHEC de l'auto-test : le module ne relit pas le contenu écrit (%s).\n"
                     "Les sauvegardes de credentials seraient VIDES : corrigez le module d'abord." % nom)
    print("Auto-test du module : OK (le contenu écrit est relu à l'identique)")
    _enregistrer(etat)


def figer():
    etat = _etat()
    if not etat:
        sys.exit("Aucune credential %s* trouvée." % PREFIXE)
    if _alerte_vides(etat):
        sys.exit("Empreintes NON enregistrées (une vérification sur des contenus vides ne prouverait rien).")
    _enregistrer(etat)


def supprimer():
    for nom in _etat():
        delete_credential(nom)


def afficher():
    print("ATTENTION : mots de passe en clair, à n'utiliser que pour des données de test.\n")
    for e in list_credentials(PREFIXE + "*"):
        print("%-22s utilisateur=%-8s mot de passe=%r  (%d octets)" % (e.target_name, e.username, e.password, len(e.blob)))


def verifier() -> bool:
    if not os.path.isfile(FICHIER_EMPREINTES):
        sys.exit("Pas d'empreintes enregistrées : lancez d'abord 'creer' ou 'figer'.")
    with open(FICHIER_EMPREINTES, encoding="utf-8") as f:
        attendu = json.load(f)
    obtenu = _etat()

    ok = True
    for nom in sorted(set(attendu) | set(obtenu)):
        if nom not in obtenu:
            print("  MANQUANTE   %s" % nom); ok = False
        elif nom not in attendu:
            print("  EN TROP     %s" % nom); ok = False
        else:
            diff = [k for k in attendu[nom] if attendu[nom][k] != obtenu[nom][k] and k != "octets"]
            if diff:
                print("  DIFFÉRENTE  %s (%s)" % (nom, ", ".join("mot de passe" if k == "empreinte" else k for k in diff)))
                ok = False
            else:
                print("  OK          %s" % nom)
    if any(v["octets"] == 0 for v in obtenu.values()):
        _alerte_vides(obtenu)
        ok = False
    print("\nRESTAURATION %s" % ("CONFORME" if ok else "NON CONFORME"))
    return ok


COMMANDES = {"creer": creer, "figer": figer, "supprimer": supprimer,
             "afficher": afficher, "verifier": verifier}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDES:
        sys.exit(__doc__)
    resultat = COMMANDES[sys.argv[1]]()
    sys.exit(0 if resultat in (None, True) else 1)
