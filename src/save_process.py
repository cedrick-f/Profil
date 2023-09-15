#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : save_process (sauvegarde dans un thread)
#
#
################################################################################

from os.path import join
from queue import Queue
from shutil import rmtree
from tempfile import TemporaryDirectory
from threading import Thread
import logging, traceback

###############################################################################
# Modules "application"
from archive import ArchiveManager
from contenu import ProfilConfig, PROFILS, DEBUG
from messages import msg


CONFIG_FILE = 'config.xml'



class SaveProcess(Thread):
    """Définit un processus de sauvegarde."""
    

    def __init__(self, manager: ArchiveManager, 
                 profil_config: ProfilConfig, 
                 psw: str):
        super().__init__()
        self.profil_config = profil_config
        self.manager = manager
        self.psw = psw
        self.queue = Queue()

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
            self.manager.to_zip(temp.name, 
                                filename,
                                self.psw)
        except Exception as e:
            logging.info('ERROR : '+ traceback.format_exc())
            if DEBUG: print('ERROR : '+ traceback.format_exc())
        finally:
            self.queue.put(None)


class RestoreProcess(SaveProcess):
    """Définit un processus de restoration."""

    def __init__(self, manager: ArchiveManager, 
                 profil_config: ProfilConfig, 
                 fichier_config: str, 
                 psw: str):
        super().__init__(manager, profil_config, psw)
        self.profil_config = profil_config
        self.fichier_config = fichier_config
        if DEBUG: print("RestoreProcess", self.profil_config)
        self.manager = manager
        self.psw = psw

    def run(self):
        temp = TemporaryDirectory()
        #zip_path = self.manager.get_most_recent_zip()
        logging.info('Restoring : ' + str(self.profil_config))
        if DEBUG: print('Restoring : ' + str(self.profil_config))
        try:
            self.queue.put(msg.get('unzipping'))
            self.manager.from_zip(self.fichier_config, 
                                  temp.name,
                                  self.psw)
            if DEBUG: print("   ", temp.name)
                
            
#             self.queue.put(msg.get('parse'))
#             self.profil_config.restaurer_xml(join(temp.name, CONFIG_FILE))

            self.queue.put(msg.get('restoring'))
            self.profil_config.restaurer(temp.name)
        except Exception as e:
            logging.info('ERROR : '+ traceback.format_exc())
            if DEBUG: print('ERROR : '+ traceback.format_exc())
        finally:
            self.queue.put(None)




if __name__ == "__main__":
    process = SaveProcess(ArchiveManager(), PROFILS)
    process.run()
