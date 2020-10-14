#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : save_process (sauvegarde dans un thread)
#
#
################################################################################

from queue import Queue
from tempfile import TemporaryDirectory
from threading import Thread
from contenu import ProfilGroup, PROFILS, ProfilConfig
from archive import *
from typing import Dict, List
from os.path import dirname, join


class SaveProcess(Thread):
    """Définit un processus de sauvegarde."""

    def __init__(self, profilConfig: ProfilConfig):
        super().__init__()
        self.profilConfig = profilConfig
        self.queue = Queue()

    def run(self):
        temp = TemporaryDirectory()
        print("Sauvegarde dans ",temp)
        try:
            self.profilConfig.sauver(temp.name)
            self.queue.put(self.profilConfig.nom)
            #self.profilConfig.sauver_xml(join(dirname(temp.name), 'config.xml'))
            
#             for name, group in []:#self.profiles.items():
#                 self.queue.put(name)
#                 print(group.sauver(temp.name))
#                 group.sauver_xml(join(dirname(temp.name), 'config.xml'))
        finally:
            self.queue.put(None)


if __name__ == "__main__":
    process = SaveProcess(PROFILS)
    process.run()
