#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : archive = gestion de l'archivage (ZIP)
#
#
################################################################################

import glob
import os, sys
import time
from datetime import date
import zipfile
from os.path import exists, expanduser, getmtime, splitext
from typing import Optional, List
from tempfile import TemporaryDirectory
from pathlib import Path
import logging, traceback
import subprocess
# bibliothèque à installer : pip install pywin32
from win32com.shell import shell, shellcon
from genericpath import isfile
from zipfile import BadZipfile
#import pyminizip

# DEBUG = True  : lancé par "python stp.py"  (mode test, tout est redirigé vers test/)
# DEBUG = False : lancé par le .exe          (cx_Freeze définit sys.frozen)
DEBUG = not getattr(sys, "frozen", False)

###############################################################################
# Modules "application"
from contenu import ProfilConfig
import save_process


# import distutils.spawn
# HAS_7Z = bool(distutils.spawn.find_executable("7z.exe"))
# from shutil import which
# 
# HAS_7Z = which("7z.exe") is not None



def get_path_mesdocuments():
    """ Renvoie le chemin absolu du dossier personnel
         = "Mes documents" sous Windows
        
        Si l'application est lancée depuis les sources (python stp.py),
        renvoie à la place un dossier "test", frère du dossier "src",
        pour pouvoir essayer sauvegarde/restauration sans toucher aux vrais documents.
        (Version .exe générée par setup.py : sys.frozen est défini -> vrai dossier.)

    """
    # Si lancé depuis stp.py :
    if DEBUG:
        dossier_test = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test")
        os.makedirs(dossier_test, exist_ok=True)
        return dossier_test

    # Si lancé depuis stp.exe :
    try:
        return shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
    except:
        return os.path.join("U:", os.environ['USERNAME'], 'Mes documents')


class ArchiveManager:
    """Gère les archives des profils.

    :type dossier: str or None
    """
    BASENAME = 'profile-save-'
    
    
    def __init__(self):
        self.dossier = self.get_dossier_perso()

    ############################################################################
    def get_archive_name(self):
        return ArchiveManager.BASENAME + str(date.today()) + '.zip'
    
    
    ############################################################################
    def set_dossier(self, dossier: str) -> Optional[str]:
        """ Change le répertoire de travail.
        
        :return: Ce dossier s'il est accessible sinon None 
                 (la modification n'est pas appliquée dans ce cas).
        """
        dossier = self._get_dossier(dossier)
        if dossier is None:
            return None

        self.dossier = dossier
        return self.dossier


    ############################################################################
    def get_dossier_perso(self) -> str:
        """ Récupère le dossier personnel d'un utilisateur
        """
        path = get_path_mesdocuments()
        if exists(path):
            return path
        return expanduser('~')


    ############################################################################
    def _get_dossier(self, dossier: str) -> Optional[str]:
        """ Retourne le même dossier s'il est accessible en écriture, sinon None
        """
        acces = os.access(dossier, os.W_OK)
        return dossier if acces else None


    ############################################################################
    def get_most_recent_zip(self) -> Optional[str]:
        """ Récupère le fichier .zip de sauvegarde le plus récent
            
            Renvoie le nom du fichier
        """
        max_mtime = 0
        file = None
        for filename in os.listdir(self.dossier):
            if not filename.startswith(ArchiveManager.BASENAME) or splitext(filename)[1] != '.zip':
                continue
            mtime = getmtime(os.path.join(self.dossier, filename))
            if mtime > max_mtime:
                file = filename
                max_mtime = mtime
        return file

    ############################################################################
    def get_all_zip(self) -> List[str]:
        """ Récupère les fichiers .zip de sauvegarde
            
            Renvoie la liste des noms de fichier
        """
        lst_file = []
        for filename in os.listdir(self.dossier):
            if not filename.startswith(ArchiveManager.BASENAME) or splitext(filename)[1] != '.zip':
                continue
            mtime = getmtime(os.path.join(self.dossier, filename))
            lst_file.append((mtime, filename))
        lst_file.sort(reverse = True)
        return [f[1] for f in lst_file]
    
    
    ############################################################################
    def get_profil_config(self, fichier_config: str = "", psw: str = "") -> ProfilConfig:
        """ Ouvre un fichier de configuration
            et renvoie son ProfilConfig à partir du xml intégré
            
            Renvoie None si aucun fichier valide n'a  été trouvé.
        """
#         print("get_profil_config", fichier_config)
        if fichier_config == "" or not isfile(os.path.join(self.dossier, fichier_config)):
            fichier_config = self.get_most_recent_zip()
#         if fichier_config is None:
#             fichier_config = self.get_archive_name()
        
        temp = TemporaryDirectory()
        
        p = ProfilConfig()
#         time.sleep(0.1) # Pour éviter les erreurs ???
#         print("   ", fichier_config)
        if fichier_config is not None:
            fichier_config = os.path.join(self.dossier, fichier_config)
            try:
                with zipfile.ZipFile(fichier_config, 'r') as myzip:
                    myzip.extract(save_process.CONFIG_FILE, temp.name)
            except zipfile.BadZipfile: # Deuxième tentative ...
                if DEBUG: print("2ème essai lecture zip :", fichier_config)
                with zipfile.ZipFile(fichier_config, 'r') as myzip:
                    myzip.extract(save_process.CONFIG_FILE, temp.name)
            
            fichier_xml = os.path.join(temp.name, save_process.CONFIG_FILE)
    #         print(fichier_xml)
            try:
                p.restaurer_xml(fichier_xml)
            except Exception as e:
                logging.error("reading config : "+ fichier_xml + "\n" + traceback.format_exc())
                if DEBUG: print("ERROR reading config : "+ fichier_xml)
                return
            #print("   ", p)
            return p
    
    
    ############################################################################
    def to_zip(self, src_path: str, dest_zip: str, pwd = None) -> bool:
        """Archive un dossier dans un fichier .zip de destination.

        L'archive est d'abord écrite dans un fichier temporaire (.zip.tmp), vérifiée,
        puis renommée : en cas d'arrêt en cours d'écriture, l'éventuelle archive
        précédente du même nom reste intacte.

        :param src_path: Chemin complet vers le répertoire à archiver
        :param dest_zip: Nom du fichier de destination

        :return: True si l'archive a été créée, False si elle était corrompue (elle n'est alors pas conservée)
        """
        zipPath = os.path.join(self.dossier, dest_zip)
        tmpPath = zipPath + ".tmp"      # l'extension .tmp est ignorée par get_most_recent_zip / get_all_zip
        if DEBUG: print("to_zip", pwd)
        if DEBUG: print("     ", zipPath)

        # Fichiers temporaires laissés par un arrêt brutal précédent
        for ancien in glob.glob(os.path.join(glob.escape(self.dossier), ArchiveManager.BASENAME + "*.zip.tmp")):
            try:
                os.remove(ancien)
            except OSError:
                pass

        try:
            with open(tmpPath, 'wb') as fichier:
                with zipfile.ZipFile(fichier, 'w') as myzip:
                    if pwd is not None:
                        myzip.setpassword(pwd)
                    p = Path(src_path)
                    for f in p.rglob('*'):
                        if DEBUG: print(f)
                        myzip.write(f, os.path.relpath(f, start=src_path))
                fichier.flush()
                os.fsync(fichier.fileno())      # les données sont vraiment sur le disque

            # Relecture complète (contrôle des CRC) AVANT de remplacer l'ancienne archive
            with zipfile.ZipFile(tmpPath) as myzip:
                mauvais = myzip.testzip()
            if mauvais is not None:
                texte = "Archive corrompue (fichier : %s), non conservée : %s" % (mauvais, zipPath)
                logging.error(texte)
                if DEBUG: print("ERREUR :", texte)
                return False                    # le finally ci-dessous supprime le .tmp

            os.replace(tmpPath, zipPath)        # remplacement en une seule opération
        finally:
            if os.path.exists(tmpPath):         # échec : pas de fichier temporaire abandonné
                try:
                    os.remove(tmpPath)
                except OSError:
                    pass
        return True


    ############################################################################
    def from_zip(self, src_zip: str, dest_path: str, psw = None) -> bool:
        """Décompresse une archive .zip vers un dossier.

        :param src_zip: Nom du fichier d'origine
        :param dest_path: Chemin complet du répertoire dans lequel extraire les fichiers
        """
        with zipfile.ZipFile(os.path.join(self.dossier, src_zip), 'r') as myzip:
            myzip.extractall(dest_path)
        return True


