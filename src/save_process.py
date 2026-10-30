#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : save_process (sauvegarde dans un thread)
#
#
################################################################################

from os.path import join, splitext
from queue import Queue
from shutil import rmtree
from tempfile import TemporaryDirectory
from threading import Thread
import logging, traceback, sys
from typing import Optional

# DEBUG = True  : lancé par "python stp.py"  (mode test, tout est redirigé vers test/)
# DEBUG = False : lancé par le .exe          (cx_Freeze définit sys.frozen)
DEBUG = not getattr(sys, "frozen", False)

###############################################################################
# Modules "application"
from archive import ArchiveManager, MotDePasseError
from contenu import ProfilConfig, PROFILS
from messages import msg


CONFIG_FILE = 'config.xml'



class SaveProcess(Thread):
    """Définit un processus de sauvegarde."""
    

    def __init__(self, manager: ArchiveManager, 
                 profil_config: ProfilConfig, 
                 password: str):
        super().__init__()
        self.profil_config = profil_config
        self.manager = manager
        self.password = password
        self.queue = Queue()
        self.erreur: Optional[str] = None       # message d'erreur à afficher à l'utilisateur


    def run(self):
        temp = TemporaryDirectory()
        filename = self.manager.get_archive_name()
        logging.info('Saving : ' + str(self.profil_config))
        if DEBUG: print('Saving : ' + str(self.profil_config))
        try:
            self.queue.put(msg.get('saving'))
            self.profil_config.sauver(temp.name)
            self.profil_config.sauver_xml(join(temp.name, CONFIG_FILE))
            self.queue.put(msg.get('unzipping'))
            if self.manager.to_zip(temp.name, 
                                   filename,
                                   self.password):
                if DEBUG:
                    dossier_dezip = join(self.manager.dossier, splitext(filename)[0])
                    rmtree(dossier_dezip, ignore_errors=True)           # repartir d'un dossier vide
                    self.manager.from_zip(filename, dossier_dezip, self.password)      # décompression de l'archive
            else:
                self.erreur = msg.get('zip_corrompu')
                self.queue.put(self.erreur)

        except Exception as e:
            logging.info('ERROR : '+ traceback.format_exc())
            if DEBUG: print('ERROR : '+ traceback.format_exc())
            self.erreur = "Erreur : l'opération a échoué (voir stp.log)"
            self.queue.put(self.erreur)
        finally:
            self.queue.put(None)


class RestoreProcess(SaveProcess):
    """Définit un processus de restoration."""

    def __init__(self, manager: ArchiveManager, 
                 profil_config: ProfilConfig, 
                 fichier_config: str, 
                 password: str):
        super().__init__(manager, profil_config, password)
        self.profil_config = profil_config
        self.fichier_config = fichier_config
        if DEBUG: print("RestoreProcess", self.profil_config)
        self.manager = manager
        self.password = password

    def run(self):
        temp = TemporaryDirectory()
        #zip_path = self.manager.get_most_recent_zip()
        logging.info('Restoring : ' + str(self.profil_config))
        if DEBUG: print('Restoring : ' + str(self.profil_config))
        try:
            self.queue.put(msg.get('unzipping'))
            self.manager.from_zip(self.fichier_config, 
                                  temp.name,
                                  self.password)
            if DEBUG: print("   ", temp.name)
                
            
#             self.queue.put(msg.get('parse'))
#             self.profil_config.restaurer_xml(join(temp.name, CONFIG_FILE))

            self.queue.put(msg.get('restoring'))
            self.profil_config.restaurer(temp.name)
        
        except MotDePasseError as e:
            logging.error('Restauration impossible : ' + str(e))
            if DEBUG: print('ERREUR :', e)
            self.erreur = msg.get('mdp_incorrect')
            self.queue.put(self.erreur)

        except Exception as e:
            logging.info('ERROR : '+ traceback.format_exc())
            if DEBUG: print('ERROR : '+ traceback.format_exc())
            self.erreur = "Erreur : l'opération a échoué (voir stp.log)"
            self.queue.put(self.erreur)
        finally:
            self.queue.put(None)




if __name__ == "__main__":
    process = SaveProcess(ArchiveManager(), PROFILS)
    process.run()
