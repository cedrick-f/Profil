#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : application (module de lancement GUI)
#
#
################################################################################
import os, sys, time
from tkinter import Frame, Tk, messagebox


# DEBUG = True  : lancé par "python stp.py"  (mode test, tout est redirigé vers test/)
# DEBUG = False : lancé par le .exe          (cx_Freeze définit sys.frozen)
DEBUG = not getattr(sys, "frozen", False)
if DEBUG:
    _home = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "test", "home")
    os.environ["USERPROFILE"] = _home
    os.environ["APPDATA"] = os.path.join(_home, "AppData", "Roaming")
    os.environ["LOCALAPPDATA"] = os.path.join(_home, "AppData", "Local")
    for _v in ("USERPROFILE", "APPDATA", "LOCALAPPDATA"):
        os.makedirs(os.environ[_v], exist_ok=True)
# ------------------------------------------------------------------------------


###############################################################################
# Modules "application"
from save_process import RestoreProcess, SaveProcess
from messages import msg
from archive import ArchiveManager, get_path_mesdocuments
from contenu import PROFILS
from gui.widgets import ActionWidget, ConfigWidget, WorkplaceWidget, Splash, PasswordWidget, StatusWidget
from gui.center_tk_window import *


import logging
LOG_FILE = os.path.join(get_path_mesdocuments(), 'stp.log')
logging.basicConfig(filename = LOG_FILE, 
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    encoding = "utf8")


base_path = os.path.dirname(os.path.abspath(sys.argv[0]))


class Application(Frame):
    """ Fenêtre principale de l'application
    """

    def __init__(self, master: Tk, auto_restore = False):
        super().__init__(master, borderwidth=5, relief="ridge")
        
        self.manager = ArchiveManager()
        self.profilConfigSave = PROFILS.copie()  # Par défaut : tous les éléments
        self.profilConfigRest = self.manager.get_profil_config()
        self.fichier_config = self.manager.get_most_recent_zip()
        
        if auto_restore:
            # Affichage d'un splash screen d'attente
            master.withdraw()
            splash = Splash(self, "auto_restore", path="")
            #center_on_screen(splash)
            splash.lift()

            self.handle_restore()
            time.sleep(10)
            splash.destroy()
            master.destroy()
            sys.exit()
            
            
        # Affichage d'un splash screen d'avertissement
        master.withdraw()
        splash = Splash(self)
        ##center_on_screen(splash)
        self.after(2000, splash.destroy)
        master.deiconify()
        splash.lift()
        
        
        #################################################################################
        # Tous les Widgets ...
        self.workplace = WorkplaceWidget(self, self.manager, self.update_profileR)
#         self.workplace.pack(fill=tkinter.BOTH, expand=1, padx = 5, pady = 5)
        self.workplace.pack(padx = 5, pady = 5, fill = tkinter.X)
        
        self.passwordWidget = PasswordWidget(self)
        self.passwordWidget.pack(padx = 5, pady = 5, fill = tkinter.X)

        self.statusWidget = StatusWidget(self, LOG_FILE)
        self.statusWidget.pack(padx = 5, pady = 5, fill = tkinter.X)

        f = Frame(self)
        f.columnconfigure((0, 1), weight = 1, uniform = "actions")   # 2 colonnes de même largeur
        f.rowconfigure(0, weight = 1)                                # et de même hauteur

        self.actionSave = ActionWidget(f, self.handle_save, 'save', self.profilConfigSave)
        self.actionSave.grid(row = 0, column = 0, sticky = "nsew", padx = 5, pady = 5)

        self.actionRestore = ActionWidget(f, self.handle_restore, 'restore', self.profilConfigRest)
        self.actionRestore.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)

        f.pack(fill = tkinter.BOTH, expand = 1)
        
        self.process = None
        self.pack(fill=tkinter.X, expand=1)
        
    def handle_save(self):
        self.actionSave.config.set_config()
        password = self._get_password()
        if not password and self.profilConfigSave.contient_mode(4):
            # identifiants Windows sans chiffrement : on demande confirmation (réponse par défaut : Non)
            if not messagebox.askyesno(msg.get('avert_titre'), msg.get('avert_mode4'),
                                       icon = "warning", default = "no"):
                logging.info('Sauvegarde annulée : credentials sans mot de passe')
                return
        self.process = SaveProcess(self.manager, 
                                   self.profilConfigSave, 
                                   password)
        logging.info('Saving ...')
        self.process.start()
        self.process.join()
        self.update_status()
        self.workplace.update()

    def handle_restore(self):
        if self.profilConfigRest is not None:
            interface = hasattr(self, 'actionRestore')
            if interface:
                self.actionRestore.config.set_config()
            self.process = RestoreProcess(self.manager, 
                                          self.profilConfigRest,
                                          self.fichier_config, 
                                          self._get_password())
            logging.info('Retoring ...')
            self.process.start()
            self.process.join()
            if interface:
                self.update_status()    
    
#     def handle_save(self, password = ""):
# #         self.profilConfigSave.set_grps(self.configS.get_config())
#         self.actionSave.config.set_config()
#         self.process = SaveProcess(self.manager, 
#                                    self.profilConfigSave, 
#                                    password)
#         logging.info('Saving ...')
#         self.process.start()
#         self.process.join()
#         self.update_status()
#         self.workplace.update()

#     def handle_restore(self, password = ""):
#         if self.profilConfigRest is not None:
# #           # En mode auto_restore, la méthode est appelée depuis __init__ :
#             # l'interface n'existe pas encore
#             interface = hasattr(self, 'actionRestore')
#             if interface:
#                 self.actionRestore.config.set_config()
#             self.process = RestoreProcess(self.manager, 
#                                           self.profilConfigRest,
#                                           self.fichier_config, 
#                                           password)
#             logging.info('Retoring ...')
#             self.process.start()
#             self.process.join()
#             if interface:
#                 self.update_status()

    def update_status(self):
        x = self.process.queue.get()
        if x is None:
            erreur = self.process.erreur
            self.process.join()
            self.process = None
            self.statusWidget.update_status(erreur if erreur else '100%')
            for button in (self.actionSave.btn, self.actionRestore.btn):
                button['state'] = 'normal'
        else:
            # le message d'erreur est affiché tel quel, sans "..."
            self.statusWidget.update_status(x if x == self.process.erreur else x + '...')
            self.master.after(150, self.update_status)
            for button in (self.actionSave.btn, self.actionRestore.btn):
                button['state'] = 'disabled'

    def update_profileR(self, fichier_config: str):
#         print("update_profileR_2", fichier_config)
        self.profilConfigRest = self.manager.get_profil_config(fichier_config = fichier_config)
        if self.profilConfigRest is not None:
#             print("   ", self.profilConfigRest)
            self.fichier_config = fichier_config
            self.actionRestore.config.setProfilConfig(self.profilConfigRest)
        self.actionRestore.config.update()
    

    def on_closing(self):
        if self.process is not None:
            if messagebox.askokcancel("Opération en cours", "Une opération est en cours....\nSouhaitez-vous réellement quitter l'application ?"):
                root.destroy()
            return
        root.destroy()
        
    def _get_password(self) -> str:
        """Mot de passe saisi ('' si l'interface n'existe pas encore : mode auto_restore)."""
        return self.passwordWidget.get_psw() if hasattr(self, 'passwordWidget') else ""


######################################################################################
if __name__ == '__main__':
    root = Tk()
    auto_restore = len(sys.argv) > 1 and sys.argv[1] == '-r' and not DEBUG
    if DEBUG: print("auto_restore :",auto_restore)
    app = Application(root, auto_restore = auto_restore)
    center_on_screen(root)
    if not auto_restore:
        root.title(msg.get('title'))
        root.geometry("")
        root.iconbitmap(os.path.join(base_path, 'img','Icone_STP_v2.ico'))
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
    else:
        logging.info('AutoRestore')
    app.mainloop()
