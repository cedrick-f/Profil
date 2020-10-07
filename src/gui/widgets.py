from src.messages import msg
from src.archive import ArchiveManager
from tkinter import Button, Checkbutton, Entry, Frame, StringVar
from tkinter.filedialog import askdirectory
from typing import List


class ActionWidget(Frame):
    """Interface pour les actions de sauvegarde et de restoration."""

    def __init__(self, parent: Frame):
        Frame.__init__(self, parent)
        self.save_btn = Button(self, text=msg.get('save'), command=self.handle_save_click)
        self.save_btn.grid(row=0, column=1)
        self.restore_btn = Button(self, text=msg.get('restore'), command=self.handle_restore_click)
        self.restore_btn.grid(row=0, column=3)
        self.pack()

    def handle_save_click(self):
        print(msg.get('save'))  # TODO

    def handle_restore_click(self):
        print(msg.get('restore'))  # TODO


class ConfigWidget(Frame):
    """Interface pour configurer quels éléments seront sauvegardés."""

    def __init__(self, parent: Frame):
        Frame.__init__(self, parent)
        self.checkboxes: List[Checkbutton] = []
        for application in ['firefox', 'icônes']:  # TODO
            checkbutton = Checkbutton(self, text=application)
            self.checkboxes.append(checkbutton)
            checkbutton.pack()
        self.pack()


class WorkplaceWidget(Frame):
    """Interface pour choisir le répertoire de sauvegarde."""

    def __init__(self, parent: Frame, manager: ArchiveManager):
        Frame.__init__(self, parent)
        self.folder_path = StringVar()
        self.folder_path.set(manager.dossier)
        self.entry = Entry(self, textvariable=self.folder_path)
        self.entry.grid(row=0, column=1)
        self.browse_btn = Button(self, text=msg.get('browse'), command=self.handle_browse_click)
        self.browse_btn.grid(row=0, column=3)
        self.pack()

    def handle_browse_click(self):
        self.folder_path.set(askdirectory())
