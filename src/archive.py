'''
Copier un fichier dans un dossier : fonction copier_fichier(chemin_fichier, chemin_destination)

   - renvoie True si tout s’est passé correctement
   - interception de toute erreur possible
   
'''

from typing import Optional
import os, glob
import zipfile
import shutil

#ZIP_PATH_DEFAUT = os.path.join(os.environ['USERPROFILE'], 'Mes documents')
ZIP_PATH_DEFAUT = os.path.join("U:", os.environ['USERNAME'], 'Mes documents')
ZIP_FILE_DEFAUT = "profil.zip"

class ArchiveManager:
    '''
    gere le processus de sauvegarde
    - récupère le dossier personnel comme dossier par défaut
    - peut analyser un fichier .zip
    - peut créer des archives
    '''
    def __init__(self):
        self.dossier = self.analyser()
        
    def analyser(self) -> Optional[str]:
        '''
        - récupère le dossier perso
        - renvoie None s'il est inaccessible
        '''
        self.chemin = os.path.join(os.environ['USERPROFILE'], 'Mes documents')
        self.acces = os.access(self.chemin, os.W_OK)
        
        if not self.acces:
            return None
    
        return self.chemin
    
    def to_zip(self, src_path, dest_zip):
        with zipfile.ZipFile(dest_zip, 'w') as myzip:
            print(os.path.join(src_path, "*.*"))
            for f in glob.iglob(os.path.join(src_path, "**"), recursive = True):
                print(f)
                myzip.write(f)
                
        # copier le fichier zip dans 
        return True
        
        
    '''
    def from_zip(self, destination, dossier):
        pass
       ''' 

"""
zipfile.is_zipfile(filename)
"""
if __name__ == "__main__":
    
    a = ArchiveManager()
    doss = "U:\marthe.vandenberg\Mes documents\Fritzing"
    a.to_zip(doss, os.path.join(ZIP_PATH_DEFAUT, ZIP_FILE_DEFAUT))
    print(a.chemin)