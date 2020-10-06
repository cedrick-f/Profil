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


# Modules "application"
from structure_mixin import *

################################################################################
class ProfilGroup(XMLMixin):
    def __init__(self, nom = ""):
        self.nom = nom
        self.lst_elem = []


    def add_elem(self, path = None, mode = 0):
        self.lst_elem.append(path, mode)

    def sauver(self, dest):
        for e in self.lst_elem:
            e.sauver(dest)



################################################################################
class ProfilElem(XMLMixin):
    def __init__(self, path = None, mode = 0):

        self.path = path

        # Mode de copie :
        #  0 = fichier unique
        #  1 = dossier complet
        #  2 = linux-like
        #  3 = linux-like + recursif
        self.mode = mode


    ############################################################################
    def sauver(self, dest):
        """ Copie les fichiers du contenu vers le dossier dest

            FileExistsError si dest existe déjà

            Renvoie la liste des fichiers qui n'ont pas été copiés
        """
        fail = []
        if self.mode == 0:
            shutil.copy2(self.path, dest)

        elif self.mode == 1:
            try:
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
    def restaurer(self, source):
        """ Restaure les fichiers du dossier source vers le dossier d'origine
            Renvoie la liste des fichiers qui n'ont pas été copiés
        """
        fail = []
        try:
            shutil.copytree(source, self.path)
        except shutil.Error as exc:
            errors = exc.args[0]
            for error in errors:
                src, dst, msg = error
                fail.append(src)

        return fail






################################################################################
if __name__ == "__main__":
    base = "C:\\Users\\Cedrick\\Documents\\Developp\\Profil\\Test"
    pp = os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles')
    print(pp)
    print(os.listdir(pp))
    e = ProfilElem(pp, 1)
    print(e.sauver(base))