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
from shutil import rmtree
from tempfile import TemporaryDirectory
from threading import Thread
from contenu import ProfilGroup, PROFILS, ProfilConfig
from archive import *
from typing import Dict, List
from os.path import dirname, join
from typing import Dict
from os import listdir, makedirs
from os.path import isdir, join
from datetime import date
from archive import ArchiveManager
from contenu import ProfilGroup, PROFILS
from messages import msg


class SaveProcess(Thread):
    """Définit un processus de sauvegarde."""
    BASENAME = 'profile-save-'

    def __init__(self, profilConfig: ProfilConfig):
        super().__init__()
        self.profilConfig = profilConfig
    def __init__(self, manager: ArchiveManager, profiles: Dict[str, ProfilGroup]):
        super().__init__()
        self.manager = manager
        self.profiles = profiles
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
        filename = SaveProcess.BASENAME + str(date.today()) + '.zip'
        try:
            for name, group in self.profiles.items():
                self.queue.put(name)
                subfolder = join(temp.name, name)
                makedirs(subfolder)
                print(group.sauver(subfolder))
                group.sauver_xml(join(temp.name, name + '.xml'))

            self.queue.put(msg.get('archive'))
            self.manager.to_zip(temp.name, filename)
        finally:
            rmtree(temp.name)
            self.queue.put(None)


class RestoreProcess(SaveProcess):
    """Définit un processus de restoration."""

    def __init__(self, manager: ArchiveManager, profiles: Dict[str, ProfilGroup]):
        super().__init__(manager, profiles)

    def run(self):
        temp = TemporaryDirectory()
        zip_path = self.manager.get_most_recent_zip(SaveProcess.BASENAME)
        try:
            self.queue.put(msg.get('unzip'))
            self.manager.from_zip(zip_path, temp.name)

            self.queue.put(msg.get('parse'))
            for config_file in listdir(temp.name):
                if isdir(join(temp.name, config_file)):
                    continue
                group = ProfilGroup()
                group.restaurer_xml(join(temp.name, config_file))
                # TODO
        finally:
            rmtree(temp.name)
            self.queue.put(None)


if __name__ == "__main__":
    process = SaveProcess(ArchiveManager(), PROFILS)
    process.run()
