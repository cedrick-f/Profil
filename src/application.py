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
from gui.widgets import ActionWidget, ConfigWidget, WorkplaceWidget
from tkinter import Frame, Tk
from archive import ArchiveManager
from contenu import ProfilConfig

class Application(Frame):
    """Fenêtre principale de l'application."""

    def __init__(self, master: Tk):
        super().__init__(master)
        self.manager = ArchiveManager()
        self.actions = ActionWidget(self, self.handle_save, self.handle_restore)
        self.actions.pack()
        self.workplace = WorkplaceWidget(self, self.manager)
        self.workplace.pack()
        self.config = ConfigWidget(self)
        self.config.pack()
        self.process = None
        self.pack()
        
        self.profilConfig = ProfilConfig()
        
        
    def handle_save(self):
        self.profilConfig.set_grps(self.config.get_config())
        self.process = SaveProcess(self.profilConfig)
        self.process = SaveProcess(self.manager, self.config.get_config())
        self.process.start()
        self.update_status()

    def handle_restore(self):
        self.process = RestoreProcess(self.manager, self.config.get_config())
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
    app = Application(root)
    app.mainloop()
