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
                    Label, Toplevel, ttk
from tkinter.filedialog import askdirectory
from typing import Dict, Callable, List
from save_process import SaveProcess


#################################################################################################
class ActionWidget(Frame):
    """Interface pour les actions de sauvegarde et de restauration."""
    def __init__(self, parent: Frame, save_fn: Callable[[], None], restore_fn: Callable[[], None]):
        Frame.__init__(self, parent)
        self.save_fn = save_fn
        self.restore_fn = restore_fn
        
        self.save_btn = Button(self, text=msg.get('save'), 
                               command=self.handle_save_click)
        self.save_btn.grid(row=0, column=0, 
                           ipadx = 5, ipady = 5, 
                           padx = 5, pady = 5,
                           sticky = "nsew")
        
        self.restore_btn = Button(self, text=msg.get('restore'), 
                                  command=self.handle_restore_click)
        self.restore_btn.grid(row=0, column=1, 
                              ipadx = 5, ipady = 5, 
                              padx = 5, pady = 5,
                              sticky = "nsew")
        
        self.status = Label(self, text = '...')
        self.lst_elem: List[ProfilElem] = []
        self.status.grid(row=1, column=0, columnspan = 2, 
                         sticky = "nsew")
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

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
        self.profilConfig = profilConfig
        
        self.bool_vars: Dict[str, List[BooleanVar, Dict[BooleanVar]]] = {}
        self.chk_btn: Dict[str, List[Checkbutton, Dict[Checkbutton]]] = {}
        
        # Les groupes ...
        for groupe in PROFILS.groups:
            bool_var = BooleanVar()
            checkbutton = Checkbutton(self, text=groupe.nom, 
                                      variable=bool_var,
                                      command = lambda n=groupe.nom: self.manage_buttons(n))
            self.bool_vars[groupe.nom] = [bool_var, {}]
            self.chk_btn[groupe.nom] = [checkbutton, {}]
            
#             if groupe.nom in self.profilConfig.get_names():
#                 checkbutton.configure(state='normal')
#                 bool_var.set(True)
#             else:
#                 checkbutton.configure(state='disabled')
               
            checkbutton.pack(anchor = "w")
            
            # Les éléments ...
            if len(groupe.lst_elem) > 1:
                for elem in groupe.lst_elem:
                    bool_var = BooleanVar()
                    checkbutton = Checkbutton(self, text=elem.name, 
                                              variable=bool_var,
                                              command = lambda: self.manage_buttons(elem.name))
                    self.bool_vars[groupe.nom][1][elem.name] = bool_var
                    self.chk_btn[groupe.nom][1][elem.name] = checkbutton
                    
                    #grp = self.profilConfig.get_group(groupe.nom)
#                     if grp is not None and elem.name in grp.get_names():
#                         checkbutton.configure(state='normal')
#                         bool_var.set(True)
#                     else:
#                         checkbutton.configure(state='disabled')
                      
                    checkbutton.pack(anchor = "w", padx = (20, 0))
        self.update()
        
        
    
    def manage_buttons(self, nom):
        for n, l in self.bool_vars.items():
            bv, d = l
            if len(d) > 0:
                if nom == n:
                    for b in d.values():
                        b.set(bv.get())
                elif any(b.get() for b in d.values()):
                    bv.set(True)
                elif not any(b.get() for b in d.values()):
                    bv.set(False)
        
        
#     def get_config(self) -> List[str]:
#         profils: List[str] = []
#         for key, var in self.bool_vars.items():
#             if var.get():
#                 profils.append(key)
#         return profils

    def get_config(self) -> Dict[str, List[str]]:
        """ Renvoie les éléments à sauvegarder/restaurer
            sous la forme :
            { 'nom_groupe1' : [],  
              'nom_groupe2' : ['nom_elem1', ' nomelem2']
            }
            (liste vide = tous les éléments du groupe)
        """
#         print("get_config")
        profils: Dict[str, List[str]] = {}
        for nom_grp, l in self.bool_vars.items():
            bv, d = l
            if bv.get():
                profils[nom_grp] = [] # = tous les éléments !!
            if len(d) > 1:
                for nom_elem, b in d.items():
                    if b.get():
                        profils[nom_grp].append(nom_elem)
#         print("  ", profils)
        return profils


    def set_config(self):
        self.profilConfig.set_config(self.get_config())


    def setProfilConfig(self, profilConfig:ProfilConfig):
        self.profilConfig = profilConfig
        
        
    def update(self):
        """ Mise à jour de l'état des checkbuttons
        """
#         print("update", self.profilConfig)
        for groupe in PROFILS.groups:
            if self.profilConfig is not None \
              and groupe.nom in self.profilConfig.get_names():
                self.chk_btn[groupe.nom][0].configure(state='normal')
                self.bool_vars[groupe.nom][0].set(True)
            else:
                self.chk_btn[groupe.nom][0].configure(state='disabled')
                self.bool_vars[groupe.nom][0].set(False)
            
            # Les éléments ...
            if len(groupe.lst_elem) > 1:
                for elem in groupe.lst_elem:
                    if self.profilConfig is not None:
                        grp = self.profilConfig.get_group(groupe.nom)
                    else:
                        grp = None
                    if grp is not None and elem.name in grp.get_names():
                        self.chk_btn[groupe.nom][1][elem.name].configure(state='normal')
                        self.bool_vars[groupe.nom][1][elem.name].set(True)
                    else:
                        self.chk_btn[groupe.nom][1][elem.name].configure(state='disabled')
                        self.bool_vars[groupe.nom][1][elem.name].set(False)
        

#################################################################################################
class WorkplaceWidget(Frame):
    """ Interface pour choisir le répertoire de sauvegarde
        et le fichier à restaurer
    """

    def __init__(self, parent: Frame, manager: ArchiveManager, update_fn: Callable[[], None]):
        Frame.__init__(self, parent)
        self.manager = manager
        self.update_fn = update_fn
        
        l = Label(self, text = msg.get('nom_ws'), justify = 'left')
        l.grid(row=0, column=0, columnspan = 2, sticky="nw")
        
        self.folder_path = StringVar(value=manager.dossier)
        self.entry = Entry(self, textvariable=self.folder_path)
        self.entry.bind('<Return>', (lambda _: self.handle_text_change()))
        self.entry.grid(row=1, column=0, padx = 5, sticky="nswe")
        
        self.browse_btn = Button(self, text=msg.get('browse'), command=self.handle_browse_click)
        self.browse_btn.grid(row=1, column=1, sticky="ne")
        
        
        self.lst_prof = ttk.Combobox(self, values=self.manager.get_all_zip())
        self.lst_prof.grid(row=2, column=0, columnspan = 2,
                           padx = 5, pady = 5,
                           sticky="nswe")
        self.lst_prof.current(0)
        self.lst_prof.bind("<<ComboboxSelected>>", lambda x: self.update_profileR())
        
        self.columnconfigure(0, weight=1)
        

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


    def update_profileR(self):
        """ Mise à jour du widget de configuration de restauration
        """
#         print("update_profileR", self.lst_prof.get())
        self.update_fn(fichier_config = self.lst_prof.get())


    def update(self):
        """ Mise à jour de liste déroulante
            puis du widget de configuration de restauration
        """
        print("update workplace")
        self.lst_prof['values'] = self.manager.get_all_zip()
        self.lst_prof.current(0)
        self.update_profileR()




#################################################################################################
class Splash(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        T = Label(self, text = msg.get('avertissement'))
        T.grid()
        self.overrideredirect(1)
        self.update()

        
    

