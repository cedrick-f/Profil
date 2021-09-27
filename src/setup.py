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
    
PATH_PYTHON36 = "C:/Users/Cedrick/AppData/Local/Programs/Python/Python37-32"

import sys, os
    
## Remove the build folder, a bit slower but ensures that build contains the latest
import shutil
shutil.rmtree("build", ignore_errors=True)


# Inculsion des fichiers de données
#################################################################################################

includefiles = ['gui/']
includefiles.extend(["../VCRUNTIME140.dll",
                     ("img/Icone_STP_v2.ico", "img/Icone_STP_v2.ico")])
    

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {'build_exe': 'build/bin',
                     'include_msvcr': True,
                     'add_to_path': True,
                     "packages": ['tkinter'],
                     "optimize" : 1,
                     "namespace_packages" : [],
                     "excludes": ['pydoc', 'doctest',
                                  "PyQt4", "PyQt4.QtGui","PyQt4._qt",
                                  "matplotlib",
                                  "numpy",
                                  ],
                     "include_files": includefiles,
                     "bin_path_includes": [],
                     "bin_path_excludes": ["C:/Windows/WinSxS","C:/Program Files"], # pour éviter qu'il prenne des dll 64 bits !!
                     'bin_excludes' : ["UxTheme.dll", "mswsock.dll", "POWRPROF.dll",
                                              "QtCore4.dll", "QtGui4.dll" ],
                   
                     }



name = "SauveTonProfil"
version = "1.2"
author = "NSI 2020"
author_email = "cedrick.faury#ac-clermont.fr".replace("#", '@')
description = "SauveTonProfil"
url = "https://info.blaisepascal.fr/nsi-prj-profil"
long_description = "sauvegarde et restauration des profils utilisateur"
lic = "GPL"

if __name__ == '__main__':
    if sys.platform == "win32":
        from cx_Freeze import setup, Executable
        cible = Executable( script = "application.py",
                            targetName="stp.exe",
                            base = "Win32GUI",
                            initScript = None,
                            icon="img/Icone_STP_v2.ico"
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
                           "build": {'build_exe': 'build'},
                           "install" : {'install_exe': 'build'},
                           },
        #        include-msvcr = True,
                executables = [cible])
    
    



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
supprimer('build/bin/lib', 'python37.dll')
supprimer('build/bin/lib', 'VCRUNTIME140.dll')
            
