#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : save_process (sauvegarde dans un thread)
#
#
################################################################################

from datetime import date
from os.path import join
from queue import Queue
from shutil import rmtree
from tempfile import TemporaryDirectory
from threading import Thread

from archive import ArchiveManager
from contenu import PROFILS
from contenu import ProfilConfig
from messages import msg

CONFIG_FILE = 'config.xml'


class SaveProcess(Thread):
    """Définit un processus de sauvegarde."""
    BASENAME = 'profile-save-'

    def __init__(self, manager: ArchiveManager, profil_config: ProfilConfig):
        super().__init__()
        self.profil_config = profil_config
        self.manager = manager
        self.queue = Queue()

    def run(self):
        temp = TemporaryDirectory()
        filename = SaveProcess.BASENAME + str(date.today()) + '.zip'
        print("Sauvegarde dans", temp.name)
        try:
            self.queue.put(msg.get('save'))
            self.profil_config.sauver(temp.name)
            self.profil_config.sauver_xml(join(temp.name, CONFIG_FILE))
            self.manager.to_zip(temp.name, filename)
        finally:
            rmtree(temp.name)
            self.queue.put(None)


class RestoreProcess(SaveProcess):
    """Définit un processus de restoration."""

    def __init__(self, manager: ArchiveManager, profil_config: ProfilConfig):
        super().__init__(manager, profil_config)
        self.manager = manager

    def run(self):
        temp = TemporaryDirectory()
        zip_path = self.manager.get_most_recent_zip(SaveProcess.BASENAME)
        try:
            self.queue.put(msg.get('unzip'))
            self.manager.from_zip(zip_path, temp.name)

            self.queue.put(msg.get('parse'))
            self.profil_config.restaurer_xml(join(temp.name, CONFIG_FILE))

            self.queue.put(msg.get('restore'))
            self.profil_config.restaurer(temp.name)
        finally:
            rmtree(temp.name)
            self.queue.put(None)


if __name__ == "__main__":
    process = SaveProcess(ArchiveManager(), PROFILS)
    process.run()
