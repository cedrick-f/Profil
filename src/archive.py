#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : widgets
#
#
################################################################################

import glob
import os
import zipfile
from os.path import exists, expanduser, getmtime, splitext
from typing import Optional
from win32com.shell import shell, shellcon

def get_path_mesdocuments():
    #return os.path.join("U:", os.environ['USERNAME'], 'Mes documents')
    return shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)



class ArchiveManager:
    """Gère les archives des profils.

    :type dossier: str or None
    """

    def __init__(self):
        self.dossier = self.get_dossier_perso()

    def set_dossier(self, dossier: str) -> Optional[str]:
        """Change le répertoire de travail.
        
        :return: Ce dossier s'il est accessible sinon None (la modification n'est pas appliquée dans ce cas).
        """
        dossier = self._get_dossier(dossier)
        if dossier is None:
            return None

        self.dossier = dossier
        return self.dossier

    def get_dossier_perso(self) -> str:
        """Récupère le dossier personnel d'un utilisateur."""
        path = get_path_mesdocuments()
        if exists(path):
            return path
        return expanduser('~')

    def _get_dossier(self, dossier: str) -> Optional[str]:
        """Retourne le même dossier s'il est accessible en écriture, sinon None."""
        acces = os.access(dossier, os.W_OK)
        return dossier if acces else None

    def get_most_recent_zip(self, prefix: str) -> Optional[str]:
        """Récupère le fichier .zip de sauvegarde le plus récent."""
        max_mtime = 0
        file = None
        for filename in os.listdir(self.dossier):
            if not filename.startswith(prefix) or splitext(filename)[1] != '.zip':
                continue
            mtime = getmtime(os.path.join(self.dossier, filename))
            if mtime > max_mtime:
                file = filename
                max_mtime = mtime
        return file

    def to_zip(self, src_path: str, dest_zip: str) -> bool:
        """Archive un dossier dans un fichier .zip de destination.

        :param src_path: Chemin complet vers le répertoire à archiver
        :param dest_zip: Nom du fichier de destination
        """
        with zipfile.ZipFile(os.path.join(self.dossier, dest_zip), 'w') as myzip:
            for f in glob.iglob(os.path.join(src_path, "**"), recursive=True):
                myzip.write(f, os.path.relpath(f, start=src_path))
        return True

    def from_zip(self, src_zip: str, dest_path: str) -> bool:
        """Décompresse une archive .zip vers un dossier.

        :param src_zip: Nom du fichier d'origine
        :param dest_path: Chemin complet du répertoire dans lequel extraire les fichiers
        """
        with zipfile.ZipFile(os.path.join(self.dossier, src_zip), 'r') as myzip:
            myzip.extractall(dest_path)
        return True
