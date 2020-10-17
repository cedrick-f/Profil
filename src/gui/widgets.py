#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : widgets
#
#
################################################################################
from contenu import ProfilGroup, PROFILS, ProfilElem, ProfilConfig
from messages import msg
from archive import ArchiveManager
from tkinter import Button, Checkbutton, Entry, Frame, StringVar, BooleanVar, \
                    Label, Toplevel
from tkinter.filedialog import askdirectory
from typing import Dict, Callable, List



#################################################################################################
class ActionWidget(Frame):
    """Interface pour les actions de sauvegarde et de restauration."""
    def __init__(self, parent: Frame, save_fn: Callable[[], None], restore_fn: Callable[[], None]):
        Frame.__init__(self, parent)
        self.save_fn = save_fn
        self.restore_fn = restore_fn
        
        self.save_btn = Button(self, text=msg.get('save'), command=self.handle_save_click)
        self.save_btn.grid(row=0, column=0, ipadx = 5, ipady = 5)
        
        self.restore_btn = Button(self, text=msg.get('restore'), command=self.handle_restore_click)
        self.restore_btn.grid(row=0, column=1, ipadx = 5, ipady = 5)
        
        self.status = Label(self, text = '...')
        self.lst_elem: List[ProfilElem] = []
        self.status.grid(row=1, column=0, columnspan = 2)


    def update_status(self, running: bool, text: str):
        for button in (self.save_btn, self.restore_btn):
            button['state'] = 'disabled' if running else 'normal'
        self.status['text'] = text

    def handle_save_click(self):
        self.save_fn()

    def handle_restore_click(self):
        self.restore_fn()





#################################################################################################
class ConfigWidget(Frame):
    """Interface pour configurer quels éléments seront sauvegardés."""

    def __init__(self, parent: Frame, profilConfig: ProfilConfig):
        Frame.__init__(self, parent)
        self.bool_vars: Dict[str, List[BooleanVar, Dict[BooleanVar]]] = {}
        
        # Les groupes ...
        for nom_grp, groupe in PROFILS.items():
            bool_var = BooleanVar()
            checkbutton = Checkbutton(self, text=nom_grp, 
                                      variable=bool_var,
                                      command = lambda n=nom_grp: self.manage_buttons(n))
            self.bool_vars[nom_grp] = [bool_var, {}]
            checkbutton.pack(anchor = "w")
            
            # Les éléments ...
            if len(groupe.lst_elem) > 1:
                for elem in groupe.lst_elem:
                    bool_var = BooleanVar()
                    checkbutton = Checkbutton(self, text=elem.name, 
                                              variable=bool_var,
                                              command = lambda: self.manage_buttons(elem.name))
                    self.bool_vars[nom_grp][1][elem.name] = bool_var
                    checkbutton.pack(anchor = "w", padx = (20, 0))
    
    
    def manage_buttons(self, nom):
        print("click", nom)
        for n, l in self.bool_vars.items():
            print("  ", n)
            bv, d = l
            if len(d) > 0:
                if nom == n:
                    for b in d.values():
                        b.set(bv.get())
                elif any(b.get() for b in d.values()):
                    bv.set(True)
                elif not any(b.get() for b in d.values()):
                    bv.set(False)
        
        
    def get_config(self) -> List[str]:
        profils: List[str] = []
        for key, var in self.bool_vars.items():
            if var.get():
                profils.append(key)
        return profils






#################################################################################################
class WorkplaceWidget(Frame):
    """Interface pour choisir le répertoire de sauvegarde."""

    def __init__(self, parent: Frame, manager: ArchiveManager):
        Frame.__init__(self, parent)
        self.manager = manager
        
        l = Label(self, text = msg.get('nom_ws'), justify = 'left')
        l.grid(row=0, column=0, columnspan = 2, sticky="nw")
        
        self.folder_path = StringVar(value=manager.dossier)
        self.entry = Entry(self, textvariable=self.folder_path)
        self.entry.bind('<Return>', (lambda _: self.handle_text_change()))
        self.entry.grid(row=1, column=0, padx = 5, sticky="nswe")
        
        self.browse_btn = Button(self, text=msg.get('browse'), command=self.handle_browse_click)
        self.browse_btn.grid(row=1, column=1, sticky="ne")
        
        self.columnconfigure(0, weight=1)
        #self.columnconfigure(0, weight=1)
        
        #self.pack(expand=1, expand=1)

    def handle_browse_click(self):
        directory = askdirectory()
        if len(directory) > 0:
            self.check_dossier(directory)
        
    def handle_text_change(self):
        directory = self.folder_path.get()
        self.check_dossier(directory)
        
        
    def check_dossier(self, directory):
        d2 = self.manager.set_dossier(directory)
        if d2 is None:
            self.entry.configure(bg = 'LightPink')
        else:
            self.entry.configure(bg = 'white')
            self.folder_path.set(directory)






#################################################################################################
class Splash(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        T = Label(self, text = msg.get('avertissement'))
        T.grid()
        self.overrideredirect(1)
        self.update()

        
    

