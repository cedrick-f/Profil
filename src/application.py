#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : application (module de lancement GUI)
#
#
################################################################################

from save_process import SaveProcess
from save_process import RestoreProcess, SaveProcess
from messages import msg
from gui.widgets import ActionWidget, ConfigWidget, WorkplaceWidget, Splash
from gui.center_tk_window import *
from tkinter import Frame, Tk
from archive import ArchiveManager
from contenu import PROFILS

class Application(Frame):
    """Fenêtre principale de l'application."""

    def __init__(self, master: Tk):
        super().__init__(master)
        
        self.manager = ArchiveManager()
        self.profilConfig = PROFILS.copie()  # Par défaut : tous les éléments
                
        self.workplace = WorkplaceWidget(self, self.manager)
        self.workplace.pack(fill=tkinter.BOTH, expand=1, padx = 5, pady = 5)
        
        self.actions = ActionWidget(self, self.handle_save, self.handle_restore)
        self.actions.pack(fill=tkinter.BOTH, expand=1, padx = 5, pady = 5)
        
        self.config = ConfigWidget(self, self.profilConfig)
        self.config.pack(fill=tkinter.BOTH, expand=1, padx = 5, pady = 5)
        
        self.process = None
        self.pack(fill=tkinter.X, expand=1)
        
        
        # Affichage d'un splash screen d'avertissement
        master.withdraw()
        splash = Splash(self)
        
        self.after(1000, splash.destroy)
        master.deiconify()
        splash.lift()
        center_on_screen(splash)
        #self.after(100, self.pack)
    
    def handle_save(self):
        self.profilConfig.set_grps(self.config.get_config())
        self.process = SaveProcess(self.manager, self.profilConfig)
        self.process.start()
        self.update_status()


    def handle_restore(self):
        self.profilConfig.set_grps(self.config.get_config()) ## ne sert à rien ... à revoir
        self.process = RestoreProcess(self.manager, self.profilConfig)
        self.process.start()
        self.update_status()


    def update_status(self):
        x = self.process.queue.get()
        if x is None:
            self.process.join()
            self.process = None
            self.actions.update_status(False, '100%')
        else:
            self.actions.update_status(True, x + '...')
            self.master.after(150, self.update_status)


    
    
if __name__ == '__main__':
    root = Tk()
    root.title(msg.get('title'))
    center_on_screen(root)
    app = Application(root)
    root.geometry("")
    app.mainloop()
