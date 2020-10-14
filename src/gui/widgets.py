#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : widgets
#
#
################################################################################
from contenu import ProfilGroup, PROFILS
from messages import msg
from archive import ArchiveManager
from tkinter import Button, Checkbutton, Entry, Frame, StringVar, BooleanVar, Label
from tkinter.filedialog import askdirectory
from typing import Dict, Callable, List


class ActionWidget(Frame):
    """Interface pour les actions de sauvegarde et de restauration."""

    def __init__(self, parent: Frame, save_fn: Callable[[], None], restore_fn: Callable[[], None]):
        Frame.__init__(self, parent)
        self.save_fn = save_fn
        self.restore_fn = restore_fn
        self.save_btn = Button(self, text=msg.get('save'), command=self.handle_save_click)
        self.save_btn.grid(row=0, column=1)
        self.restore_btn = Button(self, text=msg.get('restore'), command=self.handle_restore_click)
        self.restore_btn.grid(row=0, column=3)
        self.label = Label()
        self.label.pack()
        self.pack()

    def update_status(self, running: bool, text: str):
        for button in (self.save_btn, self.restore_btn):
            button['state'] = 'disabled' if running else 'normal'
        self.label['text'] = text

    def handle_save_click(self):
        self.save_fn()

    def handle_restore_click(self):
        self.restore_fn()


class ConfigWidget(Frame):
    """Interface pour configurer quels éléments seront sauvegardés."""

    def __init__(self, parent: Frame):
        Frame.__init__(self, parent)
        self.bool_vars: Dict[str, BooleanVar] = {}
        for application in PROFILS:
            bool_var = BooleanVar()
            checkbutton = Checkbutton(self, text=application, variable=bool_var)
            self.bool_vars[application] = bool_var
            checkbutton.pack()
        self.pack()

    def get_config(self) -> List[str]:
        profils: List[str] = []
        for key, var in self.bool_vars.items():
            if var.get():
                profils.append(key)
        return profils


class WorkplaceWidget(Frame):
    """Interface pour choisir le répertoire de sauvegarde."""

    def __init__(self, parent: Frame, manager: ArchiveManager):
        Frame.__init__(self, parent)
        self.manager = manager
        self.folder_path = StringVar(value=manager.dossier)
        self.entry = Entry(self, textvariable=self.folder_path)
        self.entry.grid(row=0, column=1)
        self.browse_btn = Button(self, text=msg.get('browse'), command=self.handle_browse_click)
        self.browse_btn.grid(row=0, column=3)
        self.pack()

    def handle_browse_click(self):
        directory = self.manager.set_dossier(askdirectory())
        self.folder_path.set(directory)
