'''
Copier un fichier dans un dossier : fonction copier_fichier(chemin_fichier, chemin_destination)

   - renvoie True si tout s’est passé correctement
   - interception de toute erreur possible
   
'''

from typing import Optional
import os


class ArchiveManager:
    '''
    gere le processus de sauvegarde
    - récupère le dossier personnel comme dossier par défaut
    - peut analyser un fichier .zip
    - peut créer des archives
    '''
    def __init__(self):
        self.dossier = self.get_dossier_perso()
        
    def get_dossier_perso(self) -> Optional[str]:
        '''
        - récupère le dossier perso
        - renvoie None s'il est inaccessible
        '''
        chemin = os.path.join('U:\\', os.environ['USERNAME'], 'Mes documents')
        acces = os.access(chemin, os.W_OK)
        
        if not acces:
            return None
    
        return chemin
