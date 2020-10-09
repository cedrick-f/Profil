from queue import Queue
from tempfile import TemporaryDirectory
from threading import Thread
from contenu import ProfilGroup, PROFILS
from typing import Dict, List
from os.path import dirname, join


class SaveProcess(Thread):
    """Définit un processus de sauvegarde."""

    def __init__(self, profiles: Dict[str, ProfilGroup]):
        super().__init__()
        self.profiles = profiles
        self.queue = Queue()

    def run(self):
        temp = TemporaryDirectory()
        try:
            for name, group in self.profiles.items():
                self.queue.put(name)
                print(group.sauver(temp.name))
                group.sauver_xml(join(dirname(temp.name), 'config.xml'))
        finally:
            self.queue.put(None)


if __name__ == "__main__":
    process = SaveProcess(PROFILS)
    process.run()
