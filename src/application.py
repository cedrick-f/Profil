#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : application (module de lancement GUI)
#
#
################################################################################

from save_process import RestoreProcess, SaveProcess
from messages import msg
from gui.widgets import ActionWidget, ConfigWidget, WorkplaceWidget, Splash
from gui.center_tk_window import *
from tkinter import Frame, Tk
from archive import ArchiveManager
from contenu import PROFILS
import os, sys
from tkinter import messagebox



class Application(Frame):
    """ Fenêtre principale de l'application
    """

    def __init__(self, master: Tk, auto_restore = False):
        super().__init__(master)
        
        self.manager = ArchiveManager()
        self.profilConfigSave = PROFILS.copie()  # Par défaut : tous les éléments
        self.profilConfigRest = self.manager.get_profil_config()
        self.fichier_config = self.manager.get_most_recent_zip()
        
        
        #################################################################################
        # Tous les Widgets ...
        self.workplace = WorkplaceWidget(self, self.manager, self.update_profileR)
#         self.workplace.pack(fill=tkinter.BOTH, expand=1, padx = 5, pady = 5)
        self.workplace.grid(row=0, column=0, columnspan = 2, 
                            padx = 5, pady = 5,
                            sticky = "nsew")
        
        self.actions = ActionWidget(self, self.handle_save, self.handle_restore)
#         self.actions.pack(fill=tkinter.BOTH, expand=1, padx = 5, pady = 5)
        self.actions.grid(row=1, column=0, columnspan = 2, 
                          padx = 5, pady = 5,
                          sticky = "nsew")
        
        self.configS = ConfigWidget(self, self.profilConfigSave)
#         self.config.pack(fill=tkinter.BOTH, expand=1, padx = 5, pady = 5)
        self.configS.grid(row=2, column=0,
                          padx = 5, pady = 5,
                          sticky = "nsew")
        
        self.configR = ConfigWidget(self, self.profilConfigRest)
#         self.config.pack(fill=tkinter.BOTH, expand=1, padx = 5, pady = 5)
        self.configR.grid(row=2, column=1, 
                          padx = 5, pady = 5,
                          sticky = "nsew")
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        self.process = None
        self.pack(fill=tkinter.X, expand=1)
        
        if auto_restore:
            self.handle_restore()
            master.destroy()
        else:
            # Affichage d'un splash screen d'avertissement
            master.withdraw()
            splash = Splash(self)
            
            self.after(2000, splash.destroy)
            master.deiconify()
            splash.lift()
            center_on_screen(splash)
            #self.after(100, self.pack)
    
    
    def handle_save(self):
#         self.profilConfigSave.set_grps(self.configS.get_config())
        self.configS.set_config()
        self.process = SaveProcess(self.manager, self.profilConfigSave)
        self.process.start()
        self.process.join()
        self.update_status()
        self.workplace.update()

    def handle_restore(self):
        if self.profilConfigRest is not None:
#             print("Restore :", self.profilConfigRest)
            self.profilConfigRest.set_config(self.configR.get_config())
            self.process = RestoreProcess(self.manager, 
                                          self.profilConfigRest,
                                          self.fichier_config)
            self.process.start()
            self.process.join()
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


    def update_profileR(self, fichier_config: str):
#         print("update_profileR_2", fichier_config)
        self.profilConfigRest = self.manager.get_profil_config(fichier_config = fichier_config)
        if self.profilConfigRest is not None:
#             print("   ", self.profilConfigRest)
            self.fichier_config = fichier_config
            self.configR.setProfilConfig(self.profilConfigRest)
        self.configR.update()
    

    def on_closing(self):
        if self.process is not None:
            if messagebox.askokcancel("Opération en cours", "Une opération est en cours....\nSouhaitez-vous réellement quitter l'application ?"):
                root.destroy()
            return
        root.destroy()
        
    def testRetore(self):
        print("restore")




if __name__ == '__main__':
    root = Tk()
    app = Application(root)
    if len(sys.argv) > 1 and sys.argv[1] == '-r': # Lancement automatique d'une restauration
        app.handle_restore()
        #app.testRetore()
        root.destroy()
        sys.exit()
    
    center_on_screen(root)
    root.title(msg.get('title'))
    root.geometry("")
    root.iconbitmap(os.path.join('img','Icone_STP_v2.ico'))
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
