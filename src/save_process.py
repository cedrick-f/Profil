from tempfile import TemporaryDirectory
from contenu import ProfilGroup, PROFILS
from typing import Dict

class SaveProcess:
    """Définit un processus de sauvegarde."""
    
    def __init__(self, profiles: Dict[str, ProfilGroup]):
        self.profiles = profiles
    
    def save(self):
        temp_files = []
        for name, group in self.profiles.items():
            temp_file = TemporaryDirectory()
            print(group.sauver(temp_file.name))
            temp_files.append(temp_file)
            

if __name__ == "__main__":
    process = SaveProcess(PROFILS)
    process.save()
