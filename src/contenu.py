#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : contenu
#
#
################################################################################

# Modules "python"
import os
import shutil
import glob
from typing import Optional, List


# Modules "application"
from structure import *

################################################################################
class ProfilGroup(XMLMixin):
    """Un groupe de fichier 'profil' à sauvegarder."""
    
    def __init__(self, nom: str = ""):
        self.nom = nom
        self.lst_elem: List[ProfilElem] = []


    def add_elem(self, path: Optional[str] = None, mode: int = 0):
        self.lst_elem.append(ProfilElem(path, mode))

    def sauver(self, dest: str) -> List[str]:
        fail: List[str] = []
        for e in self.lst_elem:
            fail.append(e.sauver(dest))
        return fail

    def __repr__(self) -> str:
        return "ProfilGroup[" + str(self.lst_elem) + "]"


################################################################################
class ProfilElem(XMLMixin):
    """Un élément d'un profil à sauvegarder (fichier ou dossier)."""
    
    def __init__(self, path: Optional[str] = None, mode: int = 0):

        self.path = path

        # Mode de copie :
        #  0 = fichier unique
        #  1 = dossier complet
        #  2 = linux-like
        #  3 = linux-like + recursif
        assert 0 <= mode <= 3, "Le mode de copie '%s' n'existe pas." % mode
        self.mode = mode
    
    def __repr__(self) -> str:
        return self.path + ", " + str(self.mode)

    ############################################################################
    def sauver(self, dest: str) -> List[str]:
        """Copie les fichiers du contenu vers le dossier de destination.

        :param dest: Dossier de destination
        :return: Renvoie la liste des fichiers qui n'ont pas été copiés
        :raises:
            FileExistsError: si dest existe déjà
        """
        fail: List[str] = []
        if self.mode == 0:
            shutil.copy2(self.path, dest)

        elif self.mode == 1:
            try:
                shutil.rmtree(dest)
                shutil.copytree(self.path, dest)    # py3.8 : , dirs_exist_ok = True)
            except shutil.Error as exc:
                errors = exc.args[0]
                for error in errors:
                    src, dst, msg = error
                    fail.append(src)


        elif self.mode == 2:
            for f in glob.glob(self.path):
                shutil.copy2(f, dest)

        return fail

    ############################################################################
    def restaurer(self, source: str) -> List[str]:
        """ Restaure les fichiers du dossier source vers le dossier d'origine
            Renvoie la liste des fichiers qui n'ont pas été copiés
        """
        fail: List[str] = []
        try:
            shutil.copytree(source, self.path)
        except shutil.Error as exc:
            errors = exc.args[0]
            for error in errors:
                src, dst, msg = error
                fail.append(src)

        return fail






################################################################################
# Constantes "application"
__FF = ProfilGroup("FireFox")
__FF.add_elem(os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles'), 1)

__BUR = ProfilGroup("Bureau")
__BUR.add_elem(os.path.join(os.environ['USERPROFILE'], ".TLPU664\\Desktop\\*lnk*"), 2)

PROFILS = {"FireFox" : __FF,
            "Bureau" : __BUR}

################################################################################

if __name__ == "__main__":
    base = os.path.join(os.environ['USERPROFILE'], ".TLPU664\\Desktop\\*lnk*")
    pp = os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles')
    print(pp)
    print(os.listdir(pp))
    e = ProfilElem(pp, 1)
