#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : contenu
#
#
################################################################################

import glob
import shutil
import time
from typing import Dict
# Modules "python"
from os import path

# Modules "application"
from structure import *


################################################################################
class ProfilConfig(XMLMixin):
    def __init__(self, nom: str = "monProfil"):
        super(ProfilConfig, self).__init__()
        self.nom = nom
        self.groups: List[ProfilGroup] = []#list(PROFILS.values())

    ############################################################################
    def __repr__(self) -> str:
        return "ProfilConfig - "+self.nom+" :\n\t" + "\n\t".join(g.__repr__() for g in self.groups)
    
    
    ############################################################################
    def copie(self):
        pc = ProfilConfig(self.nom)
        for g in self.groups:
            pc.groups.append(g.copie())
        return pc
    
    ############################################################################
    def get_group(self, nom):
        for g in self.groups:
            if g.nom == nom:
                return g
    
    ############################################################################
    def get_names(self):
        return [g.nom for g in self.groups]
    
    
    
#     ############################################################################
#     def set_grps(self, lst_grp):
# #         print("set_grps", lst_grp)
#         self.groups = []
#         for g in lst_grp:
#             self.add_grp(PROFILS.get_group(g))
# #         print(">>>", self)
            
#     ############################################################################
#     def set_config(self, lst_grp):
#         self.groups = []
#         for g in lst_grp:
#             self.add_grp(g)
            
    ############################################################################
    def set_config(self, profils: Dict[str, List[str]]):
        """ Modifie la configuration (groupes et éléments sélectionnés)
            en utilisant la structure fournie par ConfigWidget.get_config()
        """
#         print("set_config")
        self.groups = []
        for grp in PROFILS.groups:
            if grp.nom in profils:
                pg = ProfilGroup(grp.nom)
                pg.set_config(profils[grp.nom])
                self.groups.append(pg)
#         print(">>>", self)
    
    
    ############################################################################
    def add_grp(self, grp):
        self.groups.append(grp)
    
    
    ############################################################################
    def rmv_grp(self, nom):
        if PROFILS[nom] in self.groups:
            self.groups.remove(PROFILS[nom])
    
    
    ############################################################################
    def sauver(self, dest: str) -> List[str]:
        fail: List[str] = []
#         print("Sauver Config:", self.nom)
        for g in self.groups:
            subfolder = os.path.join(dest, g.nom)
            os.makedirs(subfolder)
            fail.extend(g.sauver(subfolder))
        return fail
    
    
    ############################################################################
    def restaurer(self, source: str) -> List[str]:
        """ Restaure les fichiers du dossier source vers le dossier d'origine
            Renvoie la liste des fichiers qui n'ont pas été copiés
        """
        fail: List[str] = []
        for group in self.groups:
            fail.extend(group.restaurer(path.join(source, group.nom)))
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
        return "ProfilGroup - "+self.nom+" :\n\t\t" + "\n\t\t".join(e.__repr__() for e in self.lst_elem)


    ############################################################################
    def copie(self):
        pg = ProfilGroup(self.nom)
        for e in self.lst_elem:
            pg.lst_elem.append(e.copie())
        return pg
    
    
    ############################################################################
    def get_names(self):
        return [e.name for e in self.lst_elem]
    
    
    ############################################################################
    def set_config(self, profil: List[str]):
        """ Modifie la configuration (éléments sélectionnés)
            en utilisant la structure fournie par ConfigWidget.get_config()
        """
        self.lst_elem = []
        for elem in PROFILS.get_group(self.nom).lst_elem:
            if elem.name in profil or len(profil) == 0:
                pe = elem.copie()
                self.lst_elem.append(pe)
    
    
    ############################################################################
    def add_elem(self, name: Optional[str] = "", path: Optional[str] = None, mode: int = 0):
        self.lst_elem.append(ProfilElem(name, path, mode))


    ############################################################################
    def sauver(self, dest: str) -> List[str]:
        fail: List[str] = []
#         print("Sauver Groupe:", self.nom)
        for g in self.lst_elem:
#             print("  ", g.name)
            if g.name == "":
                fail.extend(g.sauver(dest))

            else:
                subfolder = os.path.join(dest, g.name)
                os.makedirs(subfolder)
                fail.extend(g.sauver(subfolder))

        return fail

    ############################################################################
    def restaurer(self, source: str) -> List[str]:
        """ Restaure les fichiers du dossier source vers le dossier d'origine
            Renvoie la liste des fichiers qui n'ont pas été copiés
        """
#         print("restaurer", self, source)
        fail: List[str] = []
        for group in self.lst_elem:
            if group.name is None:
                fail.extend(group.restaurer(source))
                
            else:
                subfolder = os.path.join(source, group.name)
                fail.extend(group.restaurer(subfolder))
                
        return fail
        
    


################################################################################
class ProfilElem(XMLMixin):
    """Un élément d'un profil à sauvegarder (fichier ou dossier)."""

    def __init__(self, name: Optional[str] = "", 
                 path: Optional[str] = "", 
                 mode: int = 0):
        super(ProfilElem, self).__init__()

        self.path = path
        self.name = name

        # Mode de copie :
        #  0 = fichier unique
        #  1 = dossier complet
        #  2 = linux-like
        #  3 = linux-like + recursif
        assert 0 <= mode <= 3, "Le mode de copie '%s' n'existe pas." % mode
        self.mode = mode



    ############################################################################
    def __repr__(self) -> str:
        return "ProfilElem - "+self.name+" : "+ self.path + " (mode " + str(self.mode)+")"


    ############################################################################
    def copie(self):
        pe = ProfilElem(self.name, self.path, self.mode)
        return pe
    
    ############################################################################
    def sauver(self, dest: str) -> List[str]:
        """Copie les fichiers du contenu vers le dossier de destination.

        :param dest: Dossier de destination
        :return: Renvoie la liste des fichiers qui n'ont pas été copiés
        :raises:
            FileExistsError: si dest existe déjà
        """
#         print("sauver Elem", self.path)
        fail: List[str] = []
        
        
        if self.mode == 0:
            shutil.copy2(self.path, dest)

        elif self.mode == 1:
            try:
                if not os.access(self.path, os.W_OK):
                    fail.append(self.path)
                    return fail
                shutil.rmtree(dest)
                shutil.copytree(self.path, dest)    # py3.8 : , dirs_exist_ok = True)
            except shutil.Error as exc:
                errors = exc.args[0]
                for error in errors:
                    src, dst, msg = error
                    fail.append(src)


        elif self.mode == 2:
            for f in glob.glob(self.path):
#                 print("   ", f)
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
#         print("restaurer", source, self.path)
        
        try:
            if path.exists(self.path):
                shutil.rmtree(self.path, True)
                time.sleep(0.1) # Pour éviter les erreurs d'accès refusé par copytree


            if self.mode == 0:
                shutil.copy2(source, self.path)

            elif self.mode == 1:
                shutil.copytree(source, self.path)

            elif self.mode == 2:
                for f in glob.glob(os.path.join(source, "**")):
#                     print(f, glob.glob(os.path.join(source, "**")))
                    shutil.copy2(f, self.path.split("*")[0])

            elif self.mode == 3:
                for f in glob.glob(source, recursive = True):
                    shutil.copy2(f, self.path)

        except shutil.Error as exc:
            errors = exc.args[0]
            for error in errors:
                src, dst, msg = error
                fail.append(src)

        return fail






################################################################################
# Constantes "application"
__FF = ProfilGroup("FireFox")
__FF.add_elem("Roaming", os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles'), 1)
__FF.add_elem("Local", os.path.join(os.environ['LOCALAPPDATA'], 'Mozilla','Firefox','Profiles'), 1)

__BUR = ProfilGroup("Bureau")
__BUR.add_elem("", os.path.join(os.environ['USERPROFILE'], "Desktop","*.lnk"), 2)


# Un dossier pour faire des tests en toute sécurité
__TEST = ProfilGroup("Test")
__TEST.add_elem("", os.path.join(os.environ['USERPROFILE'], "Desktop", "Test"), 1)


PROFILS = ProfilConfig()
PROFILS.add_grp(__FF)
PROFILS.add_grp(__BUR)
#PROFILS.add_grp(__TEST)
# PROFILS = {"FireFox" : __FF,
#             "Bureau" : __BUR,
#             "Test" : __TEST}

################################################################################

if __name__ == "__main__":
    # base = os.path.join(os.environ['USERPROFILE'], "Desktop\\*lnk*")
    # pp = os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles')
    # print(pp)
    # print(os.listdir(pp))
    # e = ProfilElem(pp, 1)

    #base = "C:\\Users\\Cedrick\\Documents\\Developp\\Profil"
    # pp = os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles')
    # print(pp)
    #__FF.sauver_xml(os.path.join(base, "text.xml"))
    print(PROFILS)
    
    # essai avec pickle
    import pickle
    
    with open('data.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(PROFILS, f, pickle.HIGHEST_PROTOCOL)
    
