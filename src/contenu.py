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
from typing import Optional, List, Dict
import datetime


# Modules "application"
from structure import *

################################################################################
class ProfilConfig(XMLMixin):
    def __init__(self, nom: str = "monProfil"):
        super(ProfilConfig, self).__init__()
        self.nom = nom
        self.date = ""
        self.lst_grp = list(PROFILS.values())

    ############################################################################
    def __repr__(self) -> str:
        return "ProfilConfig :\n\t" + "\n\t".join(g.__repr__() for g in self.lst_grp)
    
    ############################################################################
    def set_grps(self, lst_grp):
        self.lst_grp = []
        for g in lst_grp:
            self.add_grp(g)
            
    ############################################################################
    def add_grp(self, nom):
        if nom in PROFILS and not PROFILS[nom] in self.lst_grp:
            self.lst_grp.append(PROFILS[nom])
        
    ############################################################################
    def rmv_grp(self, nom):
        if PROFILS[nom] in self.lst_grp:
            self.lst_grp.remove(PROFILS[nom])
        
    ############################################################################
    def sauver(self, dest: str) -> List[str]:
        fail: List[List[str]] = []
        self.date = datetime.datetime.now().strftime('%m/%d/%Y')
        
        for g in self.lst_grp:
            subfolder = os.path.join(dest, g.nom)
            os.makedirs(subfolder)
            print("   ", g.nom, "-->", subfolder)
            fail.append(g.sauver(subfolder))
        print(fail)
        return fail
    
    ############################################################################
    def restaurer(self, source: str) -> List[str]:
        """ Restaure les fichiers du dossier source vers le dossier d'origine
            Renvoie la liste des fichiers qui n'ont pas été copiés
        """
        fail: List[List[str]] = []
        for e in self.lst_grp:
            fail.append(e.restaurer(source))
        return fail


################################################################################
class ProfilGroup(XMLMixin):
    """Un groupe de fichier 'profil' à sauvegarder."""

    def __init__(self, nom: str = ""):
        super(ProfilGroup, self).__init__()
        self.nom = nom
        self.lst_elem: List[ProfilElem] = []

    ############################################################################
    def __repr__(self) -> str:
        return "ProfilGroup :\n\t\t" + "\n\t\t".join(e.__repr__() for e in self.lst_elem)

    ############################################################################
    def add_elem(self, path: Optional[str] = None, mode: int = 0):
        self.lst_elem.append(ProfilElem(path, mode))

    ############################################################################
    def sauver(self, dest: str) -> List[str]:
        fail: List[List[str]] = []
        for e in self.lst_elem:
            fail.append(e.sauver(dest))
        return fail

    ############################################################################
    def restaurer(self, source: str) -> List[str]:
        """ Restaure les fichiers du dossier source vers le dossier d'origine
            Renvoie la liste des fichiers qui n'ont pas été copiés
        """
        fail: List[List[str]] = []
        for e in self.lst_elem:
            fail.append(e.restaurer(source))
        return fail
        
    


################################################################################
class ProfilElem(XMLMixin):
    """Un élément d'un profil à sauvegarder (fichier ou dossier)."""

    def __init__(self, path: Optional[str] = "", mode: int = 0):
        super(ProfilElem, self).__init__()

        self.path = path

        # Mode de copie :
        #  0 = fichier unique
        #  1 = dossier complet
        #  2 = linux-like
        #  3 = linux-like + recursif
        assert 0 <= mode <= 3, "Le mode de copie '%s' n'existe pas." % mode
        self.mode = mode



    ############################################################################
    def __repr__(self) -> str:
        return "ProfilElem : "+ self.path + " (mode " + str(self.mode)+")"

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
                
        elif self.mode == 3:
            for f in glob.glob(self.path, recursive = True):
                shutil.copy2(f, dest)

        return fail

    ############################################################################
    def restaurer(self, source: str) -> List[str]:
        """ Restaure les fichiers du dossier source vers le dossier d'origine
            Renvoie la liste des fichiers qui n'ont pas été copiés
        """
        fail: List[str] = []
        print("restaurer", source, self.path)
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
__FF.add_elem(os.path.join(os.environ['LOCALAPPDATA'], 'Mozilla','Firefox','Profiles'), 1)

__BUR = ProfilGroup("Bureau")
__BUR.add_elem(os.path.join(os.environ['USERPROFILE'], "Desktop","*.lnk"), 2)

__TEST = ProfilGroup("Test")
__TEST.add_elem(os.path.join(os.environ['USERPROFILE'], "Desktop", "Test"), 1)
# PROFILS = ProfilConfig()
# PROFILS.add_grp(__FF)
# PROFILS.add_grp(__BUR)
PROFILS = {"FireFox" : __FF,
            "Bureau" : __BUR,
            "Test" : __TEST}

################################################################################

if __name__ == "__main__":
    # base = os.path.join(os.environ['USERPROFILE'], "Desktop\\*lnk*")
    # pp = os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles')
    # print(pp)
    # print(os.listdir(pp))
    # e = ProfilElem(pp, 1)

    base = "C:\\Users\\Cedrick\\Documents\\Developp\\Profil"
    # pp = os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles')
    # print(pp)
    __FF.sauver_xml(os.path.join(base, "text.xml"))
