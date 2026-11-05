#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Groupes à sauvegarder définis par un fichier externe (profils.json), sans recompiler.

Le fichier est UTILISÉ SEULEMENT s'il passe deux contrôles :
  1. sa SIGNATURE (profils.json.sig) est valide : elle prouve qu'il vient de l'administrateur
     (clé privée, jamais présente sur les postes) et n'a pas été modifié ;
  2. son CONTENU respecte des règles strictes (voir valider) : seulement des chemins relatifs
     sous USERPROFILE / APPDATA / LOCALAPPDATA, pas de "..", modes connus, etc.
Sinon il est ignoré (erreur dans le log) et l'application utilise ses définitions intégrées.

Format de profils.json :
{
  "version": 3,
  "groupes": [
    {"nom": "Clés SSH", "coche_par_defaut": false,
     "elements": [ {"nom": "", "env": "USERPROFILE", "chemin": ".ssh.", "mode": 1} ]}
  ]
}
"""
import base64
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

NOM_FICHIER = "profils.json"
NOM_SIGNATURE = NOM_FICHIER + ".sig"
TAILLE_MAX = 1_000_000                      # octets
ENV_AUTORISEES = ("USERPROFILE", "APPDATA", "LOCALAPPDATA")
MODES = (0, 1, 2, 3, 4)
LONGUEUR_PREFIXE_CREDENTIAL = 4             # mode 4 : au moins 4 caractères avant le premier joker

# Clé PUBLIQUE de l'administrateur (Ed25519). Elle n'est pas secrète.
# À remplacer par celle affichée par :  python outil_profils.py genkey
CLE_PUBLIQUE = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAbgVWdKjX8LAEHCYrxGCWtycAeKnNsvl+gqOQogHDyz4=
-----END PUBLIC KEY-----"""


################################################################################
class ProfilsError(Exception):
    """Fichier de profils refusé (signature invalide ou contenu non conforme)."""


################################################################################
# 1) Signature
################################################################################
def verifier_signature(contenu: bytes, signature_b64: bytes, cle_pem: str):
    """Lève ProfilsError si la signature (base64) de `contenu` n'est pas valide."""
    from Cryptodome.PublicKey import ECC
    from Cryptodome.Signature import eddsa
    try:
        cle = ECC.import_key(cle_pem)
        signature = base64.b64decode(signature_b64.strip(), validate = True)
        eddsa.new(cle, 'rfc8032').verify(contenu, signature)
    except (ValueError, TypeError) as exc:
        raise ProfilsError("signature invalide (%s)" % exc) from exc


################################################################################
# 2) Contenu
################################################################################
_ILLEGAUX = re.compile(r'[<>"|\x00-\x1f]')
_RESERVES = {"CON", "PRN", "AUX", "NUL"} | {"COM%d" % i for i in range(1, 10)} | {"LPT%d" % i for i in range(1, 10)}
_CLES_GROUPE = {"nom", "coche_par_defaut", "elements"}
_CLES_ELEM = {"nom", "env", "chemin", "mode"}


def _nom(valeur: Any, contexte: str, vide_ok: bool) -> str:
    """Nom de groupe / d'élément : il devient un NOM DE DOSSIER dans l'archive."""
    if not isinstance(valeur, str):
        raise ProfilsError("%s : texte attendu" % contexte)
    if valeur == "":
        if vide_ok:
            return valeur
        raise ProfilsError("%s : nom vide" % contexte)
    if (len(valeur) > 60 or valeur != valeur.strip() or valeur.endswith(".") or valeur in (".", "..")
            or re.search(r'[\\/:*?"<>|\x00-\x1f]', valeur) or valeur.split(".")[0].upper() in _RESERVES):
        raise ProfilsError("%s : nom non valable (%r)" % (contexte, valeur))
    return valeur


def _chemin(valeur: Any, mode: int, contexte: str) -> str:
    """Chemin relatif (modes 0 à 3) ou filtre de nom de credential (mode 4)."""
    if not isinstance(valeur, str) or valeur == "" or len(valeur) > 260 or _ILLEGAUX.search(valeur):
        raise ProfilsError("%s : chemin absent ou non valable" % contexte)

    if mode == 4:                           # filtre sur le nom d'une credential Windows
        if re.search(r"[\\/]", valeur):
            raise ProfilsError("%s : un filtre de credential ne contient pas de séparateur" % contexte)
        prefixe = re.split(r"[*?\[]", valeur)[0]
        if len(prefixe) < LONGUEUR_PREFIXE_CREDENTIAL:
            raise ProfilsError("%s : filtre trop large (au moins %d caractères avant le premier joker)"
                               % (contexte, LONGUEUR_PREFIXE_CREDENTIAL))
        return valeur

    morceaux = [m for m in re.split(r"[\\/]+", valeur) if m != ""]
    if (valeur.startswith(("\\", "/")) or ":" in valeur or os.path.isabs(valeur)) or not morceaux:
        raise ProfilsError("%s : le chemin doit être RELATIF (%r)" % (contexte, valeur))
    if ".." in morceaux:
        raise ProfilsError("%s : '..' est interdit (%r)" % (contexte, valeur))
    for m in morceaux[:-1]:
        if re.search(r"[*?]", m):
            raise ProfilsError("%s : joker (* ?) autorisé seulement dans le dernier élément du chemin" % contexte)
    if mode in (0, 1) and re.search(r"[*?]", valeur):
        raise ProfilsError("%s : pas de joker pour les modes 0 et 1" % contexte)
    return os.path.join(*morceaux)


def valider(donnees: Any) -> List[Dict[str, Any]]:
    """Contrôle strictement la structure. Renvoie une liste normalisée de groupes,
    ou lève ProfilsError avec un message précis."""
    if not isinstance(donnees, dict) or not isinstance(donnees.get("groupes"), list):
        raise ProfilsError('structure attendue : {"groupes": [...]}')
    if len(donnees["groupes"]) > 100:
        raise ProfilsError("trop de groupes (100 maximum)")

    resultat: List[Dict[str, Any]] = []
    noms_groupes = set()
    for i, g in enumerate(donnees["groupes"], 1):
        if not isinstance(g, dict) or set(g) - _CLES_GROUPE or "nom" not in g or not isinstance(g.get("elements"), list):
            raise ProfilsError("groupe n°%d : structure incorrecte (clés permises : %s)" % (i, ", ".join(sorted(_CLES_GROUPE))))
        nom = _nom(g["nom"], "groupe n°%d" % i, vide_ok = False)
        if nom.lower() in noms_groupes:
            raise ProfilsError("groupe '%s' en double" % nom)
        noms_groupes.add(nom.lower())
        coche = g.get("coche_par_defaut", True)
        if not isinstance(coche, bool):
            raise ProfilsError("groupe '%s' : coche_par_defaut doit être true ou false" % nom)
        if not 0 < len(g["elements"]) <= 100:
            raise ProfilsError("groupe '%s' : 1 à 100 éléments attendus" % nom)

        elements, noms_elem = [], set()
        for j, e in enumerate(g["elements"], 1):
            ctx = "groupe '%s', élément n°%d" % (nom, j)
            if not isinstance(e, dict) or set(e) - _CLES_ELEM or not {"chemin", "mode"} <= set(e):
                raise ProfilsError("%s : structure incorrecte (clés permises : %s)" % (ctx, ", ".join(sorted(_CLES_ELEM))))
            mode = e["mode"]
            if isinstance(mode, bool) or mode not in MODES:
                raise ProfilsError("%s : mode %r inconnu (permis : %s)" % (ctx, mode, MODES))
            nom_e = _nom(e.get("nom", ""), ctx, vide_ok = True)
            if nom_e.lower() in noms_elem:
                raise ProfilsError("%s : nom d'élément %r en double" % (ctx, nom_e))
            noms_elem.add(nom_e.lower())
            env = e.get("env", "")
            if mode == 4:
                if env != "":
                    raise ProfilsError("%s : le mode 4 (credentials) n'a pas de variable d'environnement" % ctx)
            elif env not in ENV_AUTORISEES:
                raise ProfilsError("%s : variable d'environnement %r non autorisée (permises : %s)"
                                   % (ctx, env, ", ".join(ENV_AUTORISEES)))
            elements.append({"nom": nom_e, "env": env, "chemin": _chemin(e["chemin"], mode, ctx), "mode": mode})
        resultat.append({"nom": nom, "coche_par_defaut": coche, "elements": elements})
    return resultat


################################################################################
# 3) Chargement : ne lève jamais d'exception
################################################################################
def charger(dossier: str, signature_obligatoire: bool = True,
            cle_pem: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Lit et contrôle profils.json (et profils.json.sig) dans `dossier`.

    Renvoie la liste de groupes validée, ou None (absent ou REFUSÉ : détail dans le log).
    Une signature présente doit toujours être valide ; une signature absente n'est
    tolérée que si signature_obligatoire est False (mode DEBUG).
    """
    chemin, chemin_sig = os.path.join(dossier, NOM_FICHIER), os.path.join(dossier, NOM_SIGNATURE)
    if not os.path.isfile(chemin):
        logging.info("Pas de fichier %s : définitions intégrées uniquement", NOM_FICHIER)
        return None
    try:
        if os.path.getsize(chemin) > TAILLE_MAX:
            raise ProfilsError("fichier trop volumineux")
        with open(chemin, "rb") as f:
            contenu = f.read()

        if os.path.isfile(chemin_sig):
            with open(chemin_sig, "rb") as f:
                verifier_signature(contenu, f.read(1000), cle_pem or CLE_PUBLIQUE)
        elif signature_obligatoire:
            raise ProfilsError("signature absente (%s)" % NOM_SIGNATURE)
        else:
            logging.warning("%s NON SIGNÉ accepté (mode test)", NOM_FICHIER)

        groupes = valider(json.loads(contenu.decode("utf-8")))
    except (ProfilsError, OSError, ValueError) as exc:      # ValueError : JSON ou UTF-8 invalide
        logging.error("%s REFUSÉ, définitions intégrées utilisées : %s", NOM_FICHIER, exc)
        return None

    logging.info("%s chargé : %d groupe(s)", NOM_FICHIER, len(groupes))
    return groupes
