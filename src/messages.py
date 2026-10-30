#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setup

msg = {
    'archive': 'Compression des dossiers',
    'title': f'Sauve Ton Profil - {setup.version}',
    'save': '\U0001F4BE Sauvegarder',
    'saving': 'Sauvegarde',
    'restore': '\u21BA Restaurer',
    'restoring': 'Restauration',
    'browse': 'Parcourir',
    'zipping': 'Compression de l\'archive',
    'unzipping': 'Décompression de l\'archive',
    'parse': 'Lecture des fichiers',
    'avertissement': f"""<h2>Sauve Ton Profil (STP)</h2><p>est une application
    de sauvegarde/restauration de profils utilisateur.</p>
    <p>STP a été réalisé par les élèves de Terminale Spécialité NSI,
    dans le cadre d'un projet.</p>
    
    <p>Son développement est encore en cours,
    merci de votre indulgence !</p>
    """,
    'nom_ws' : "Emplacement de sauvegarde",
    'password' : "Mot de passe (laisser vide pour ne pas chiffrer)",
    'auto_restore' : f"""<h1 style="color: red; text-align: center">STP</h1><p>Restauration automatique en cours ...</p><p>Patience !</p>""",
    'zip_corrompu': "Erreur : l'archive créée est corrompue, elle n'a pas été enregistrée",

    'voir_mdp': '\U0001F441',            # œil : afficher / masquer le mot de passe
    'voir_log': '\U0001F4C4 Journal',    # page : ouvrir le fichier stp.log
    
    'mdp_incorrect': "Erreur : mot de passe manquant ou incorrect, rien n'a été restauré",
    'avert_titre': "Sauvegarde non chiffrée",
    'avert_mode4': "Cette sauvegarde contient des identifiants Windows (mots de passe), "
                   "mais aucun mot de passe n'est saisi : l'archive ne sera PAS chiffrée "
                   "et ces identifiants seront lisibles par toute personne qui peut ouvrir le fichier.\n\n"
                   "Pour la chiffrer, annulez et saisissez un mot de passe dans le champ prévu.\n\n"
                   "Continuer sans chiffrement ?",
}
