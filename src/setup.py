#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : setup = génération d'un executable
#
#
################################################################################


"""
Module Setup
************

Script pour générer un pack avec executable :
    .../python setup.py build
"""
    
#PATH_PYTHON36 = "C:/Users/Cedrick/AppData/Local/Programs/Python/Python37-32"

import sys, os

from version import version
    
## Remove the build folder, a bit slower but ensures that build contains the latest
import shutil


base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

# Inculsion des fichiers de données
#################################################################################################

includefiles = [os.path.join(base_path,'gui')]
includefiles.extend([(os.path.join(base_path, 'img','Icone_STP_v2.ico'), os.path.join('img','Icone_STP_v2.ico'))])
    

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {'build_exe': 'build/bin',
                     'include_msvcr': True,
                     'add_to_path': True,
                     "packages": ['tkinter', 'pyzipper', 'Cryptodome'],
                     "optimize" : 1,
                     #"namespace_packages" : [],
                     "excludes": ['pydoc', 'doctest', 'lief', 'test', 'cx_Freeze',
                                  'unittest', 'pydoc_data', 'idlelib', 'lib2to3', 'turtledemo',  # outils de développement
                                  'Cryptodome.SelfTest', 'Cryptodome.PublicKey',
                                  'Cryptodome.Signature', 'Cryptodome.IO',                       # inutiles pour l'AES
                                  ],
                     "include_files": includefiles,
                     "bin_path_includes": [],
                     "bin_path_excludes": ["C:/Windows/WinSxS","C:/Program Files"], # pour éviter qu'il prenne des dll 64 bits !!
                     'bin_excludes' : ["UxTheme.dll", "mswsock.dll", "POWRPROF.dll",
                                              "QtCore4.dll", "QtGui4.dll" ],
                   
                     }

name = "SauveTonProfil"
author = "NSI 2026"
author_email = "cedrick.faury#ac-clermont.fr".replace("#", '@')
description = "SauveTonProfil"
url = "https://info.blaisepascal.fr/nsi-prj-profil"
long_description = "sauvegarde et restauration des profils utilisateur"
lic = "GPL"

# Nettoyage (on enlève les python37.dll en trop
def supprimer(racine, nomFichier, parent = "", niveau = 0):
    # chemin absolu de la racine
    abspath = os.path.join(parent, racine)
    if os.path.isdir(abspath):
        for fd in os.listdir(abspath):
            supprimer(fd, nomFichier, abspath, niveau+1)
    elif os.path.split(abspath)[1] == nomFichier:
        os.remove(abspath)
        print(abspath)


def supprimer_doublons_dll(racine = 'build/bin'):
    """Supprime de lib/ les DLL identiques (octet pour octet) à celles déjà à côté de l'exécutable."""
    import hashlib
    sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
    reference = {f: sha(os.path.join(racine, f)) for f in os.listdir(racine) if f.lower().endswith('.dll')}
    for dp, _, fs in os.walk(os.path.join(racine, 'lib')):
        for f in fs:
            if f in reference and sha(os.path.join(dp, f)) == reference[f]:
                os.remove(os.path.join(dp, f))
                print(os.path.join(dp, f))

if __name__ == '__main__':
    shutil.rmtree("build", ignore_errors=True)
    if sys.platform == "win32":
        from cx_Freeze import setup, Executable
        cible = Executable( script = os.path.join(base_path,"stp.py"),
                            target_name="stp.exe",
                            base = "Win32GUI",
                            init_script = None,
                            icon = os.path.join(base_path, 'img','Icone_STP_v2.ico')
                            )
    
    
        setup(  name = name,
                version = version,
                author = author,
                author_email = author_email,
                url = url,
                description = description,
                long_description = long_description,
                license = lic,
                options = {"build_exe": build_exe_options,
                           #"build": {'build_exe': 'build'},
                           "install" : {'install_exe': 'build'},
                           },
        #        include-msvcr = True,
                executables = [cible])
    
    supprimer('build/bin/lib', 'python38.dll')
    supprimer('build/bin/lib', 'VCRUNTIME140.dll')
    supprimer_doublons_dll('build/bin')
            
