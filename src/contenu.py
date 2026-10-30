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
import sys
import shutil
import time
from typing import Dict
# Modules "python"
from os import path
from pathlib import Path
import logging, traceback
import configparser
import base64, fnmatch, json

# DEBUG = True  : lancé par "python stp.py"  (mode test, tout est redirigé vers test/)
# DEBUG = False : lancé par le .exe          (cx_Freeze définit sys.frozen)
DEBUG = not getattr(sys, "frozen", False)
# Restauration d'un dossier (mode 1) : supprimer ce qui n'existe pas dans la sauvegarde ?
RESTAURATION_SUPPRIME_EXTRAS = True
# Mode 4 (credentials Windows)
CREDENTIALS_FILE = "credentials.json"       # fichier créé dans le dossier de l'élément
CREDENTIAL_PREFIXE_TEST = "STP_TEST_"       # en DEBUG, seules les credentials de ce préfixe sont touchées

###############################################################################
# Modules "application"
from structure import *
from windows_credential_manager import list_credentials, write_credential, CRED_PERSIST_LOCAL_MACHINE




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
    
    
    ############################################################################
    def contient_mode(self, mode: int) -> bool:
        """True si au moins un élément de la configuration utilise ce mode de copie."""
        return any(e.mode == mode for g in self.groups for e in g.lst_elem)

            
    ############################################################################
    def set_config(self, profils: Dict[str, List[str]]):
        """ Modifie la configuration (groupes et éléments sélectionnés)
            en utilisant la structure fournie par ConfigWidget.get_config()
        """
        if DEBUG: print("set_config")
        self.groups = []
        for grp in PROFILS.groups:
            if grp.nom in profils:
                pg = ProfilGroup(grp.nom)
                pg.set_config(profils[grp.nom])
                self.groups.append(pg)
        if DEBUG: print(">>>", self)
    
    
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
            if DEBUG: print("       ", group.nom)
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
    def add_elem(self, name: Optional[str] = "", 
                       envpath: Optional[str] = "", 
                       path: Optional[str] = None, 
                       mode: int = 0):
        if DEBUG: print("add_elem", name)
        self.lst_elem.append(ProfilElem(name, envpath, path, mode))


    ############################################################################
    def sauver(self, dest: str) -> List[str]:
        fail: List[str] = []
        if DEBUG: print("  Sauver Groupe:", self.nom)
        for g in self.lst_elem:
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

        fail: List[str] = []
        for group in self.lst_elem:
            if group.name is None:
                fail.extend(group.restaurer(source))
                
            else:
                subfolder = os.path.join(source, group.name)
                fail.extend(group.restaurer(subfolder))
                
        return fail
        
    

################################################################################
################################################################################
def _trace(niveau: int, message: str):
    """Écrit un message dans le log (et à l'écran en mode DEBUG)."""
    logging.log(niveau, message)
    if DEBUG: print("   ", logging.getLevelName(niveau), ":", message)


def _est_dans(enfant: str, parent: str) -> bool:
    """True si `enfant` est le dossier `parent` ou se trouve à l'intérieur."""
    enfant = os.path.normcase(os.path.realpath(enfant))
    parent = os.path.normcase(os.path.realpath(parent))
    try:
        return os.path.commonpath([enfant, parent]) == parent
    except ValueError:      # lecteurs différents (C: et D:) sous Windows
        return False

class ProfilElem(XMLMixin):
    """Un élément d'un profil à sauvegarder (fichier ou dossier)."""

    def __init__(self, name: Optional[str] = "", 
                 envpath: Optional[str] = "",
                 path: Optional[str] = "", 
                 mode: int = 0):
        super().__init__()
        #if DEBUG: print("ProfilElem", name, "\n", envpath, "\n", path, "\n", mode)
        
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
        assert 0 <= mode <= 4, "Le mode de copie '%s' n'existe pas." % mode
        self.mode = mode



    ############################################################################
    def __repr__(self) -> str:
        return "ProfilElem - "+self.name+" : "+ self.env + " "+ self.path + " (mode " + str(self.mode)+")"

    ############################################################################
    def getFullPath(self):
        #if DEBUG: print("getFullPath", self.env)
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
        """Copie les fichiers de l'élément vers le dossier de destination.

        Un fichier qui pose problème est consigné dans le log et dans la liste
        renvoyée, mais n'interrompt pas la sauvegarde des autres.

        :param dest: Dossier de destination (doit exister)
        :return: Renvoie la liste des fichiers qui n'ont pas été copiés
        """

        src = self.getFullPath()
        _trace(logging.INFO, "Sauver '%s' : %s (mode %d)" % (self.name, src, self.mode))

        # --- Destination : un dossier existant, où l'on peut écrire -----------
        if not os.path.isdir(dest) or not os.access(dest, os.W_OK):
            _trace(logging.ERROR, "Destination inaccessible en écriture : " + dest)
            return [src]

        if self.mode == 4:      # Credential : `path` est un filtre sur le nom, pas un chemin
            return self._sauver_credentials(dest)

        # --- Source : jamais de chemin relatif (il serait lu depuis le dossier
        #     courant), par ex. si la variable d'environnement n'existe pas ----
        if not os.path.isabs(src):
            _trace(logging.ERROR, "Chemin non absolu, ignoré : " + src)
            return [src]

        if self.mode == 0:
            return self._sauver_fichier(src, dest)
        if self.mode == 1:
            return self._sauver_dossier(src, dest)
        if self.mode in (2, 3):
            return self._sauver_filtre(src, dest, recursif = (self.mode == 3))

        _trace(logging.ERROR, "Mode de copie inconnu : %s" % self.mode)
        return [src]


    ############################################################################
    @staticmethod
    def _dossier_base(chemin: str) -> str:
        """Partie du chemin située avant le premier joker (* ? [)."""
        base = []
        for partie in Path(chemin).parts:
            if glob.has_magic(partie):
                break
            base.append(partie)
        return str(Path(*base)) if base else ""


    ############################################################################
    @staticmethod
    def _copier_fichier(f: str, dest: str, rel: Optional[str] = None) -> bool:
        """Copie le fichier `f` dans `dest`, sous le chemin relatif `rel`
        (par défaut : à plat, sous son seul nom). Renvoie True si réussi."""
        if not os.access(f, os.R_OK):
            _trace(logging.ERROR, "Fichier non lisible : " + f)
            return False

        # Deux fichiers de même nom s'écraseraient : on garde le premier,
        # et on signale le second.
        cible = os.path.join(dest, rel if rel else os.path.basename(f))
        if os.path.exists(cible):
            _trace(logging.WARNING, "Nom déjà présent, fichier non copié : " + f)
            return False

        # Ce try est volontaire : os.access ne détecte pas tout (surtout sous
        # Windows : fichier verrouillé par un autre programme, disque plein,
        # chemin trop long...). On intercepte donc l'erreur, fichier par fichier.
        try:
            os.makedirs(os.path.dirname(cible), exist_ok = True)
            shutil.copy2(f, cible)
        except OSError as exc:
            _trace(logging.ERROR, "Copie impossible : %s (%s)" % (f, exc))
            return False

        _trace(logging.INFO, "Sauvé : " + f)
        return True

    ############################################################################
    def _filtre_credentials_autorise(self) -> bool:
        """Mode 4 : en mode DEBUG, seules les credentials de test peuvent être lues/écrites.
        Le Gestionnaire d'informations d'identification est celui du VRAI compte Windows :
        la redirection vers test/ des variables d'environnement ne le concerne pas."""
        if DEBUG and not self.path.upper().startswith(CREDENTIAL_PREFIXE_TEST):
            _trace(logging.ERROR, "Mode DEBUG : seules les credentials '%s*' sont autorisées "
                                  "(filtre demandé : '%s')" % (CREDENTIAL_PREFIXE_TEST, self.path))
            return False
        return True


    ############################################################################
    def _sauver_credentials(self, dest: str) -> List[str]:
        """Mode 4 : sauvegarde les informations d'identité génériques Windows dont le nom
        correspond au filtre `self.path` (ex. "Nextcloud_*").
        Elles sont écrites dans dest/credentials.json (contenu brut codé en base64).
        ATTENTION : ce fichier contient des secrets. Ne JAMAIS les écrire dans le log."""
        if not self._filtre_credentials_autorise():
            return [self.path]

        try:
            entrees = list_credentials(self.path)
        except OSError as exc:
            _trace(logging.ERROR, "Lecture des credentials impossible (%s) : %s" % (self.path, exc))
            return [self.path]
        if len(entrees) == 0:
            _trace(logging.WARNING, "Aucune credential ne correspond à : " + self.path)
            return []

        donnees = {"version": 1,
                   "credentials": [{"target_name": e.target_name,
                                    "username": e.username,
                                    "comment": e.comment,
                                    "persist": e.persist,
                                    "blob": base64.b64encode(e.blob).decode("ascii")}
                                   for e in entrees]}
        try:
            with open(os.path.join(dest, CREDENTIALS_FILE), "w", encoding = "utf-8") as f:
                json.dump(donnees, f, indent = 2)
        except OSError as exc:
            _trace(logging.ERROR, "Écriture impossible (%s) : %s" % (CREDENTIALS_FILE, exc))
            return [self.path]

        for e in entrees:
            if len(e.blob) == 0:
                _trace(logging.WARNING, "Credential SANS contenu (mot de passe vide ou non lu) : " + e.target_name)
            else:
                _trace(logging.INFO, "Sauvé (credential) : " + e.target_name)    # le nom seulement

        return []


    ############################################################################
    def _restaurer_credentials(self, source: str) -> List[str]:
        """Mode 4 : restaure les credentials sauvegardées (celles qui existent déjà sont
        remplacées ; les autres ne sont pas touchées, rien n'est supprimé).
        Une credential dont le nom ne correspond pas au filtre de l'élément est refusée."""
        if not self._filtre_credentials_autorise():
            return [self.path]

        fichier = os.path.join(source, CREDENTIALS_FILE)
        if not os.path.isfile(fichier):
            _trace(logging.WARNING, "Absent de l'archive, credentials laissées intactes : " + self.path)
            return []
        try:
            with open(fichier, encoding = "utf-8") as f:
                entrees = json.load(f)["credentials"]
            if not isinstance(entrees, list):
                raise TypeError("liste attendue")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            _trace(logging.ERROR, "Fichier %s illisible : %s" % (CREDENTIALS_FILE, exc))
            return [self.path]

        fail: List[str] = []
        for e in entrees:
            cible = "?"
            try:
                cible = e["target_name"]
                if not fnmatch.fnmatchcase(cible.lower(), self.path.lower()):
                    raise ValueError("nom hors du filtre '%s'" % self.path)
                persist = e.get("persist", CRED_PERSIST_LOCAL_MACHINE)
                if persist not in (1, 2, 3):
                    persist = CRED_PERSIST_LOCAL_MACHINE
                write_credential(cible, e.get("username", ""), "", e.get("comment", ""),
                                 persist, blob = base64.b64decode(e.get("blob", "")))
            except (KeyError, TypeError, AttributeError, ValueError, OSError) as exc:
                fail.append(str(cible))
                _trace(logging.ERROR, "Restauration impossible (credential %s) : %s" % (cible, exc))
                continue
            _trace(logging.INFO, "Restauré (credential) : " + cible)
        return fail


    ############################################################################
    def _sauver_fichier(self, src: str, dest: str) -> List[str]:
        """Mode 0 : un fichier unique."""
        if not os.path.exists(src):
            _trace(logging.WARNING, "Absent, rien à sauver : " + src)
            return []
        if not os.path.isfile(src):
            _trace(logging.ERROR, "N'est pas un fichier : " + src)
            return [src]
        return [] if self._copier_fichier(src, dest) else [src]


    ############################################################################
    def _sauver_dossier(self, src: str, dest: str) -> List[str]:
        """Mode 1 : un dossier complet, avec ses sous-dossiers."""
        if not os.path.exists(src):
            _trace(logging.WARNING, "Absent, rien à sauver : " + src)
            if self.name:
                # Ne pas laisser de dossier vide dans l'archive : "absent" ne doit pas
                # être confondu avec "présent mais vide" (qui, lui, est sauvegardé)
                try:
                    os.rmdir(dest)
                except OSError:
                    pass
            return []
        if not os.path.isdir(src):
            _trace(logging.ERROR, "N'est pas un dossier : " + src)
            return [src]
        if not os.access(src, os.R_OK | os.X_OK):
            _trace(logging.ERROR, "Dossier non lisible : " + src)
            return [src]
        if _est_dans(dest, src):
            # ex. sauver tout AppData\Local alors que le dossier temporaire s'y trouve
            _trace(logging.ERROR, "Destination à l'intérieur de la source : " + src)
            return [src]
        if len(os.listdir(src)) == 0:
            _trace(logging.INFO, "Dossier vide, sauvé tel quel : " + src)
        fail: List[str] = []
        # Ici le try est indispensable : copytree continue après une erreur sur
        # un fichier, et ne les signale qu'à la fin, par une exception.
        try:
            shutil.copytree(src, dest, dirs_exist_ok = True, ignore_dangling_symlinks = True)
        except shutil.Error as exc:
            for erreur in exc.args[0]:
                fail.append(erreur[0])
                _trace(logging.ERROR, "Copie impossible : %s (%s)" % (erreur[0], erreur[2]))
        except OSError as exc:      # erreur sur le dossier lui-même
            fail.append(src)
            _trace(logging.ERROR, "Copie impossible : %s (%s)" % (src, exc))
        else:
            _trace(logging.INFO, "Sauvé : " + src)
        return fail


    ############################################################################
    def _sauver_filtre(self, src: str, dest: str, recursif: bool) -> List[str]:
        """Modes 2 et 3 : les fichiers qui correspondent à un filtre (*, ?, [..]).
        `src` peut être un motif, un fichier précis, ou un dossier (dont on prend
        alors tous les fichiers).
          mode 2 : fichiers copiés à plat
          mode 3 : sous-dossiers conservés (chemins relatifs au dossier de base)
        """
        if os.path.isdir(src):
            base = src
            joker = "**" if recursif else ""
            motif = os.path.join(glob.escape(src), joker, "*")  # "*" : y compris sans extension
        else:
            motif = src
            base = self._dossier_base(src)
            if not glob.has_magic(src):             # un fichier précis
                base = os.path.dirname(src)

        fichiers = glob.glob(motif, recursive = recursif, include_hidden = True)
        if len(fichiers) == 0:
            _trace(logging.WARNING, "Aucun fichier ne correspond à : " + motif)
            return []

        fail: List[str] = []
        for f in fichiers:
            if os.path.isdir(f):
                continue
            rel = os.path.relpath(f, base) if recursif else None
            if not self._copier_fichier(f, dest, rel):
                fail.append(f)
        return fail


    ############################################################################
    @staticmethod
    def _lister_fichiers(dossier: str) -> List[str]:
        """Chemins relatifs de tous les fichiers (cachés compris) d'un dossier.
        Renvoie [] si le dossier n'existe pas."""
        return [os.path.relpath(os.path.join(dp, nom), dossier)
                for dp, _, noms in os.walk(dossier) for nom in noms]


    ############################################################################
    @staticmethod
    def _dossier_cible_filtre(chemin: str, fichiers_sauves: List[str]) -> str:
        """Modes 2 et 3 : dossier dans lequel remettre les fichiers sauvegardés."""
        if os.path.isdir(chemin):
            return chemin
        if glob.has_magic(chemin):              # ex. ...\Desktop\*.lnk
            return ProfilElem._dossier_base(chemin)
        # Ni joker, ni dossier existant : un fichier précis (ex. .gitconfig),
        # ou un dossier qui n'a pas encore été recréé ?
        nom = os.path.basename(chemin).rstrip(".").lower()
        if len(fichiers_sauves) == 1 and os.path.basename(fichiers_sauves[0]).lower() == nom:
            return os.path.dirname(chemin)
        return chemin


    ############################################################################
    @staticmethod
    def _restaurer_fichier(f: str, cible: str) -> bool:
        """Copie le fichier sauvegardé `f` vers le fichier `cible`. Renvoie True si réussi."""
        # Même raison que pour la sauvegarde : seule la tentative révèle un
        # fichier verrouillé, un disque plein, un chemin trop long...
        try:
            os.makedirs(os.path.dirname(cible), exist_ok = True)
            shutil.copy2(f, cible)
        except OSError as exc:
            _trace(logging.ERROR, "Restauration impossible : %s (%s)" % (cible, exc))
            return False
        _trace(logging.INFO, "Restauré : " + cible)
        return True


    ############################################################################
    @staticmethod
    def _supprimer_extras(source: str, cible: str) -> List[str]:
        """Supprime de `cible` les fichiers (et dossiers devenus vides) qui n'existent
        pas dans `source`. À n'appeler QU'APRÈS une copie entièrement réussie."""
        fail: List[str] = []
        # topdown=False : on traite les sous-dossiers avant leur parent.
        # os.walk ne descend pas dans les liens / jonctions : rien n'y est supprimé.
        for dp, _, noms in os.walk(cible, topdown = False):
            ref = os.path.normpath(os.path.join(source, os.path.relpath(dp, cible)))
            for nom in noms:
                if not os.path.exists(os.path.join(ref, nom)):
                    f = os.path.join(dp, nom)
                    try:
                        os.remove(f)
                        _trace(logging.INFO, "Supprimé (absent de la sauvegarde) : " + f)
                    except OSError as exc:
                        fail.append(f)
                        _trace(logging.ERROR, "Suppression impossible : %s (%s)" % (f, exc))
            if dp != cible and not os.path.isdir(ref):
                try:
                    os.rmdir(dp)        # échoue (normalement) si le dossier n'est pas vide
                except OSError:
                    pass
        return fail


    ############################################################################
    def restaurer(self, source: str) -> List[str]:
        """ Restaure les fichiers du dossier source vers le dossier d'origine

            Précautions : rien n'est supprimé si la sauvegarde de cet élément est
            absente ou vide, ni si la cible sort du dossier désigné par la variable
            d'environnement ; les fichiers en trop ne sont supprimés qu'une fois
            tous les fichiers restaurés sans erreur.

            Renvoie la liste des fichiers qui n'ont pas été restaurés
        """
        if self.mode == 4:      # Credential
            return self._restaurer_credentials(source)

        cible = self.getFullPath()
        _trace(logging.INFO, "Restaurer '%s' : %s (mode %d)" % (self.name, cible, self.mode))

        # --- La sauvegarde de cet élément doit exister et contenir des fichiers.
        #     Sinon on ne touche à rien (l'ancienne version supprimait la cible
        #     AVANT de constater qu'il n'y avait rien à restaurer) -------------
        if not os.path.isdir(source):
            _trace(logging.WARNING, "Absent de l'archive, cible laissée intacte : " + cible)
            return []
        fichiers = self._lister_fichiers(source)
        if len(fichiers) == 0 and self.mode != 1:
            _trace(logging.WARNING, "Rien à restaurer (absent de l'archive ou vide), "
                                    "cible laissée intacte : " + cible)
            return []

        # --- La cible doit se trouver DANS le dossier de la variable d'environnement.
        #     La configuration vient de l'archive (config.xml) : on ne lui fait
        #     pas une confiance aveugle (chemin absolu, "..", etc.) ------------
        base = os.getenv(self.env) if self.env else None
        if not base or not os.path.isabs(cible):
            _trace(logging.ERROR, "Pas de variable d'environnement valide, restauration refusée : " + cible)
            return [cible]

        if self.mode == 0:
            dossier = os.path.dirname(cible)
        elif self.mode == 1:
            dossier = cible
        elif self.mode in (2, 3):
            dossier = self._dossier_cible_filtre(cible, fichiers)
        else:
            _trace(logging.ERROR, "Mode de copie inconnu : %s" % self.mode)
            return [cible]

        if not _est_dans(dossier, base):
            _trace(logging.ERROR, "Cible hors du dossier autorisé (%s), restauration refusée : %s" % (base, cible))
            return [cible]
        if self.mode == 1 and _est_dans(base, dossier):
            _trace(logging.ERROR, "Remplacer tout le dossier %s est refusé : %s" % (base, cible))
            return [cible]

        # --- Restauration -----------------------------------------------------
        if self.mode == 0:
            if len(fichiers) != 1:
                _trace(logging.ERROR, "Mode 0 : un seul fichier attendu dans la sauvegarde, %d trouvés" % len(fichiers))
                return [cible]
            return [] if self._restaurer_fichier(os.path.join(source, fichiers[0]), cible) else [cible]

        if self.mode == 1:
            return self._restaurer_dossier(source, cible, len(fichiers) > 0)

        fail = []       # modes 2 et 3 : on remet les fichiers sauvegardés, sans rien supprimer
        for rel in fichiers:
            if not self._restaurer_fichier(os.path.join(source, rel), os.path.join(dossier, rel)):
                fail.append(os.path.join(dossier, rel))
        return fail


    ############################################################################
    def _restaurer_dossier(self, source: str, cible: str, avec_fichiers: bool) -> List[str]:
        """ Mode 1 : le dossier cible redevient identique à la sauvegarde.
            Si la sauvegarde ne contient aucun fichier (dossier vide, éventuellement avec
            des sous-dossiers vides), on recrée ces dossiers mais on ne supprime rien.
        """
        fail: List[str] = []
        # copytree continue après une erreur sur un fichier et ne les signale
        # qu'à la fin, par une exception : ce try est indispensable.
        try:
            shutil.copytree(source, cible, dirs_exist_ok = True)
        except shutil.Error as exc:
            for erreur in exc.args[0]:
                fail.append(erreur[1])
                _trace(logging.ERROR, "Restauration impossible : %s (%s)" % (erreur[1], erreur[2]))
        except OSError as exc:
            fail.append(cible)
            _trace(logging.ERROR, "Restauration impossible : %s (%s)" % (cible, exc))

        if len(fail) > 0:
            _trace(logging.WARNING, "Erreurs de copie : les fichiers en trop ne sont pas supprimés dans " + cible)
            return fail

        _trace(logging.INFO, "Restauré : " + cible)
        if RESTAURATION_SUPPRIME_EXTRAS and avec_fichiers:
            fail.extend(self._supprimer_extras(source, cible))
        return fail



################################################################################
# Constantes "application"

# Modes de copie :
# 0: Tous les fichiers du dossier
# 1: Tous les fichiers du dossier et des sous dossiers
# 2: Tous les fichiers, filtrés (*, ?, [ranges])
# 3: Tous les fichiers et sous dossiers, filtrés (*, ?, [ranges])
# 4: credentials
    


PROFILS = ProfilConfig()

if DEBUG:
    dossier_test = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test")
        
    # Un dossier pour faire des tests en toute sécurité
    __TEST1 = ProfilGroup("Test1")  
    __TEST1.add_elem(".home", 'USERPROFILE', os.path.join(".test0"), 1)
    __TEST1.add_elem("home", 'USERPROFILE', os.path.join("test1"), 2)
    __TEST1.add_elem("roaming", 'APPDATA', os.path.join("test2"), 1)
    __TEST1.add_elem("local", 'LOCALAPPDATA', os.path.join("test3"), 1)
    __TEST1.add_elem("credentials", '', "STP_TEST_*", 4)

    __TEST2 = ProfilGroup("__Test2")
    __TEST2.add_elem(".home", 'USERPROFILE', os.path.join(".__test0"), 2)
    __TEST2.add_elem("home", 'USERPROFILE', os.path.join("__test1"), 3)
    __TEST2.add_elem("roaming", 'APPDATA', os.path.join("__test2"), 1)
    __TEST2.add_elem("autre", '', os.path.join(dossier_test, "__test3"), 1)
    
    
    PROFILS.add_grp(__TEST1)
    PROFILS.add_grp(__TEST2)
    
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

    __NXT = ProfilGroup("NextCloud")
    __NXT.add_elem("Roaming", 'APPDATA', os.path.join('Nextcloud'), 1)
    __NXT.add_elem("Local", 'LOCALAPPDATA', os.path.join('Nextcloud'), 1)

    #PROFILS.add_grp(__FF)
    PROFILS.add_grp(__BUR)
    PROFILS.add_grp(__NXT)
    PROFILS.add_grp(__GD)
    PROFILS.add_grp(__PYZ)
    PROFILS.add_grp(__VEY)
    PROFILS.add_grp(__TSK)
    PROFILS.add_grp(__STRT)
    PROFILS.add_grp(__GIT)
    PROFILS.add_grp(__SSH)
    PROFILS.add_grp(__PYT)
    #PROFILS.add_grp(__COD)



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
    
