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
import os
import time
from datetime import date
import zipfile
from os.path import exists, expanduser, getmtime, splitext
from typing import Optional, List
from contenu import ProfilConfig
from tempfile import TemporaryDirectory
import save_process

# bibliothèque à installer : pip install pywin32
from win32com.shell import shell, shellcon
from genericpath import isfile
from zipfile import BadZipfile

def get_path_mesdocuments():
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
    def get_profil_config(self, fichier_config: str = "") -> ProfilConfig:
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
#                 print("2ème essai lecture zip :", fichier_config)
                with zipfile.ZipFile(fichier_config, 'r') as myzip:
                    myzip.extract(save_process.CONFIG_FILE, temp.name)
            
        fichier_xml = os.path.join(temp.name, save_process.CONFIG_FILE)
#         print(fichier_xml)
        try:
            p.restaurer_xml(fichier_xml)
        except:
#             print("ERROR")
            return
        #print("   ", p)
        return p
    
    
    ############################################################################
    def to_zip(self, src_path: str, dest_zip: str) -> bool:
        """Archive un dossier dans un fichier .zip de destination.

        :param src_path: Chemin complet vers le répertoire à archiver
        :param dest_zip: Nom du fichier de destination
        """
        with zipfile.ZipFile(os.path.join(self.dossier, dest_zip), 'w') as myzip:
            for f in glob.iglob(os.path.join(src_path, "**"), recursive=True):
                myzip.write(f, os.path.relpath(f, start=src_path))
        return True


    ############################################################################
    def from_zip(self, src_zip: str, dest_path: str) -> bool:
        """Décompresse une archive .zip vers un dossier.

        :param src_zip: Nom du fichier d'origine
        :param dest_path: Chemin complet du répertoire dans lequel extraire les fichiers
        """
        with zipfile.ZipFile(os.path.join(self.dossier, src_zip), 'r') as myzip:
            myzip.extractall(dest_path)
        return True

