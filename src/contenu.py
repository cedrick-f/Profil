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
from pathlib import Path
import logging, traceback
import configparser

###############################################################################
# Modules "application"
from structure import *


DEBUG = False


################################################################################
class ProfilConfig(XMLMixin):
    def __init__(self, nom: str = "monProfil"):
        super().__init__()
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
        if DEBUG: print("Sauver Config:", self.nom)
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
#             print("       ", group.nom)
            fail.extend(group.restaurer(path.join(source, group.nom)))
        return fail




################################################################################
class ProfilGroup(XMLMixin):
    """Un groupe de fichier 'profil' à sauvegarder."""

    def __init__(self, nom: str = ""):
        super().__init__()
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
    def add_elem(self, name: Optional[str] = "", envpath: Optional[str] = "", path: Optional[str] = None, mode: int = 0):
        if DEBUG: print("add_elem", name)
        self.lst_elem.append(ProfilElem(name, envpath, path, mode))


    ############################################################################
    def sauver(self, dest: str) -> List[str]:
        fail: List[str] = []
        if DEBUG: print(" Sauver Groupe:", self.nom)
        for g in self.lst_elem:
#             print("  ", g.name)
            if g.name == "":
                fail.extend(g.sauver(dest))

            else:
                subfolder = os.path.join(dest, g.name)
                if not os.path.exists(subfolder):
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
                 envpath: Optional[str] = "",
                 path: Optional[str] = "", 
                 mode: int = 0):
        super().__init__()
        if DEBUG: print("ProfilElem", name, "\n", envpath, "\n", path, "\n", mode)
        
        if envpath is not None and len(envpath) > 0 and os.getenv(envpath) is not None:
            self.env = envpath
        else:
            self.env = ""
        
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
        return "ProfilElem - "+self.name+" : "+ self.env + " "+ self.path + " (mode " + str(self.mode)+")"

    ############################################################################
    def getFullPath(self):
        if DEBUG: print("getFullPath", self.env)
        logging.info("getFullPath :"+ self.env + " --- "+self.path)
        if len(self.env) > 0:
            return os.path.join(os.getenv(self.env), self.path)
        return self.path
            
            
    ############################################################################
    def copie(self):
        if DEBUG: print("copie", self.name)
        pe = ProfilElem(self.name, self.env, self.path, self.mode)
        return pe
    
    ############################################################################
    def sauver(self, dest: str) -> List[str]:
        """Copie les fichiers du contenu vers le dossier de destination.

        :param dest: Dossier de destination
        :return: Renvoie la liste des fichiers qui n'ont pas été copiés
        :raises:
            FileExistsError: si dest existe déjà
        """
        
        fail: List[str] = []
        
        path = self.getFullPath()
        if DEBUG: print("  Sauver Elem", self.path, "("+path+")")
        
        if self.mode == 0:
            shutil.copy2(path, dest)

        elif self.mode == 1:
            try:
                if not os.access(path, os.W_OK):
                    fail.append(path)
                    logging.error("  Save ERROR (access): "+ path)
                    if DEBUG: print("  Save ERROR (access):"+ path)
                    return fail
                shutil.rmtree(dest)
                shutil.copytree(path, dest)    # py3.8 : , dirs_exist_ok = True)
                logging.info('  Saved 1 :'+ path)
                if DEBUG: print('  Saved 1 :'+ path)
            except shutil.Error as exc:
                errors = exc.args[0]
                for error in errors:
                    src, dst, msg = error
                    fail.append(src)
                    logging.error("  Save ERROR :"+ src+" "+ msg)
                    if DEBUG: print("  Save ERROR :"+ src, msg)

        elif self.mode == 2:
            for f in glob.glob(path):
#                 print("+++", f, self.path)
                # Astuce pour copier les fichier "cachés"
                if os.path.basename(f).startswith('.'):
                    #cwd = os.getcwd()
#                     print("!!!!", os.path.basename(f))
                    e = shutil.copyfile(f, os.path.join(dest, "_"+os.path.basename(f)))
                    if DEBUG: print("  Err:",e)
#                     p = Path(dest)
#                     for ff in p.glob('**/*.*'):
#                         print("???1", ff)
#                     os.chdir(dest)
                    
                    os.rename(os.path.join(dest,"_"+os.path.basename(f)), 
                              os.path.join(dest, os.path.basename(f)))
#                     os.chdir(cwd)
#                     for ff in p.glob('**/*.*'):
#                         print("???2", ff)
#                 pp, ff = os.path.split(f)
#                 fff, eee = os.path.splitext(ff)
#                 print(pp, " - ", fff, " - ", eee)
#                 if eee == '':
#                     print("   xxx-", fff)
#                     os.rename(f, os.path.join(pp, "_"+fff))
#                     shutil.copy2(os.path.join(pp, "_"+fff), dest)
#                     os.rename(os.path.join(dest, "_"+fff), os.path.join(dest, fff))
                else:
                    shutil.copy2(f, dest)
                
                logging.info('  Saved 2 :'+ f)
                if DEBUG: print('  Saved 2 :'+ f)
            
                
        elif self.mode == 3:
            for f in glob.glob(path, recursive = True):
                shutil.copy2(f, dest)
                logging.info('  Saved 3 :'+ f)
                if DEBUG: print('  Saved 3 :'+ f)
                
        return fail

    ############################################################################
    def restaurer(self, source: str) -> List[str]:
        """ Restaure les fichiers du dossier source vers le dossier d'origine
            Renvoie la liste des fichiers qui n'ont pas été copiés
        """
        fail: List[str] = []
#         print("restaurer", source, self.path)
        
        path = self.getFullPath()
        logging.info("Restore process : " + source + " --> "+ path)
        try:
            if os.path.exists(path):
                shutil.rmtree(path, True)
                time.sleep(0.1) # Pour éviter les erreurs d'accès refusé par copytree

            if self.mode == 0:      # Tous les fichiers du dossier
                shutil.copy2(source, path)

            elif self.mode == 1:    # Tous les fichiers du dossier et des sous dossiers
                shutil.copytree(source, path)

            elif self.mode == 2:    # Tous les fichiers du dossier, filtrés
                p = Path(source)
                for f in p.glob('**/*.*'):
#                     print("???3", f)
#                 for f in glob.glob(os.path.join(source, "**")):
#                     print(f, self.path)
                    
#                     print(f, glob.glob(os.path.join(source, "**")))
                    shutil.copy2(f, path.split("*")[0])
                    logging.info("    File Restore SUCCESS : "+str(f))

            elif self.mode == 3:    # Tous les fichiers du dossier et des sous dossiers, filtrés
                for f in glob.glob(source, recursive = True):
                    shutil.copy2(f, path)

        except Exception as exc:
            logging.info('ERROR : '+ traceback.format_exc())
#             errors = exc.args[0]
#             for error in errors:
#                 src, dst, msg = error
#                 fail.append(src)
#                 logging.error("Restore ERROR : "+src)
                
        return fail






################################################################################
# Constantes "application"

# Modes de copie :
# 0: Tous les fichiers du dossier
# 1: Tous les fichiers du dossier et des sous dossiers
# 2: Tous les fichiers du dossier, filtrés
# 3: Tous les fichiers du dossier et des sous dossiers, filtrés
    


PROFILS = ProfilConfig()

if DEBUG:
    # Un dossier pour faire des tests en toute sécurité
    __TEST = ProfilGroup("Test")
    __TEST.add_elem("f", 'USERPROFILE', os.path.join(".test"), 2)
    __TEST.add_elem("d", 'USERPROFILE', os.path.join(".dtest"), 1)
    __TEST.add_elem("a", 'APPDATA', os.path.join("atest"), 1)
    PROFILS.add_grp(__TEST)
    
else:
    mozilla_profile = os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox')
    mozilla_profile_ini = os.path.join(mozilla_profile, 'profiles.ini')
    profile = configparser.ConfigParser()
    profile.read(mozilla_profile_ini)
    profile_path = profile.get('Profile0', 'Path').split('/')[-1]
    for section in profile.sections():
        if section.startswith("Install"):
            profile_path = profile.get(section, "Default").split('/')[-1]
            break
    #print(profile_path)

    __FF = ProfilGroup("FireFox")
    __FF.add_elem("Roaming", 'APPDATA', os.path.join('Mozilla','Firefox', 'Profiles', profile_path), 1)
    __FF.add_elem("Local", 'LOCALAPPDATA', os.path.join('Mozilla','Firefox', 'Profiles', profile_path), 1)
    __FF.add_elem("profiles.ini", 'APPDATA', os.path.join('Mozilla','Firefox','*profiles.ini'), 2)
    #__FF.add_elem("Local", 'LOCALAPPDATA', os.path.join('Mozilla','Firefox','Profiles'), 1)
    #__FF.add_elem("Roaming", 'APPDATA', local_data_path, 1)
    #__FF.add_elem("profile.ini", 'LOCALAPPDATA', os.path.join('Mozilla','Firefox', 'profiles.ini'), 2)
    
    __BUR = ProfilGroup("Bureau")
    __BUR.add_elem("", 'USERPROFILE', os.path.join("Desktop","*.lnk"), 2)
    
    __TSK = ProfilGroup("Barre des tâches")
    __TSK.add_elem("", 'APPDATA', os.path.join("Microsoft", "Internet Explorer", "Quick Launch", "User Pinned", "TaskBar", "*.lnk"), 2)
    
    __STRT = ProfilGroup("Menu Démarrer")
    __STRT.add_elem("", 'APPDATA', os.path.join("Microsoft", "Internet Explorer", "Quick Launch", "User Pinned", "StartMenu", "*.lnk"), 3)
    
    __GD = ProfilGroup("GitHub Desktop")
    __GD.add_elem("Roaming", 'APPDATA', os.path.join('GitHub Desktop'), 1)
    __GD.add_elem("Local", 'LOCALAPPDATA', os.path.join('GitHub Desktop'), 1)
    
    __PYZ = ProfilGroup("Pyzo")
    __PYZ.add_elem("Roaming", 'APPDATA', os.path.join('pyzo'), 1)
    __PYZ.add_elem("Local", 'LOCALAPPDATA', os.path.join('pyzo'), 1)

    __PYT = ProfilGroup("Python")
    __PYT.add_elem("Local", 'LOCALAPPDATA', os.path.join('Programs', 'Python'), 1)
    
    __VEY = ProfilGroup("Veyon")
    __VEY.add_elem("Roaming", 'APPDATA', os.path.join('veyon'), 1)
    
    # __VSC = ProfilGroup("Visual Studio Code")
    # __VSC.add_elem("Settings", 'APPDATA', os.path.join('Code','User'), 1)
    # __VSC.add_elem("Extensions", 'USERPROFILE', os.path.join('.vscode.','extensions'), 1) #%USERPROFILE%\.vscode\extensions
    
    __COD = ProfilGroup("VSCodium")
    __COD.add_elem("Local", 'LOCALAPPDATA', os.path.join('Programs','VSCodium'), 1)
    __COD.add_elem("Roaming", 'APPDATA', os.path.join('VSCodium'), 1)
    __COD.add_elem("Extensions", 'USERPROFILE', os.path.join('.vscode-oss'), 1)
    
    __GIT = ProfilGroup("Git")
    __GIT.add_elem("Config", 'USERPROFILE', os.path.join(".gitconfig."), 2)
    __GIT.add_elem("Credentials", 'USERPROFILE', os.path.join(".git-credentials."), 2)
    
    __SSH = ProfilGroup("Clés SSH")
    __SSH.add_elem("", 'USERPROFILE', os.path.join(".ssh."), 1)

    PROFILS.add_grp(__FF)
    PROFILS.add_grp(__BUR)
    PROFILS.add_grp(__GD)
    PROFILS.add_grp(__PYZ)
    PROFILS.add_grp(__VEY)
    PROFILS.add_grp(__TSK)
    PROFILS.add_grp(__STRT)
    PROFILS.add_grp(__GIT)
    PROFILS.add_grp(__SSH)
    PROFILS.add_grp(__PYT)
    PROFILS.add_grp(__COD)



################################################################################

#if __name__ == "__main__":
    # base = os.path.join(os.environ['USERPROFILE'], "Desktop\\*lnk*")
    # pp = os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles')
    # print(pp)
    # print(os.listdir(pp))
    # e = ProfilElem(pp, 1)

    #base = "C:\\Users\\Cedrick\\Documents\\Developp\\Profil"
    # pp = os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles')
    # print(pp)
    #__FF.sauver_xml(os.path.join(base, "text.xml"))
    #print(PROFILS)
    
    # essai avec pickle
    # import pickle
    
    # with open('data.pickle', 'wb') as f:
    #     # Pickle the 'data' dictionary using the highest protocol available.
    #     pickle.dump(PROFILS, f, pickle.HIGHEST_PROTOCOL)
    
