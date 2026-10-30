#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Boîtes de dialogue avec la même interface que tkinter.messagebox,
mais qui portent l'icône de l'application.

Les boîtes de tkinter.messagebox sont des boîtes NATIVES de Windows : leur barre de titre
ne peut pas recevoir l'icône de l'application. Celles-ci sont de simples fenêtres Tk
(Toplevel) : elles héritent de l'icône définie par  root.iconbitmap(default = ...)

Utilisation :  from gui import dialogues as messagebox
"""
import tkinter
from tkinter import Button, Frame, Label, Toplevel


# Icônes 32x32 fournies par Tk lui-même (images prédéfinies, identiques sur toutes les plateformes)
_ICONES = {"info": "::tk::icons::information",
           "warning": "::tk::icons::warning",
           "error": "::tk::icons::error",
           "question": "::tk::icons::question"}


################################################################################
class _Dialogue(Toplevel):
    """Fenêtre modale : un texte, un symbole, et une rangée de boutons."""

    def __init__(self, parent, titre, texte, boutons, defaut, annuler, symbole):
        """
        :param boutons: liste de (libellé, valeur renvoyée)
        :param defaut: valeur du bouton activé par Entrée
        :param annuler: valeur renvoyée par Échap ou la fermeture de la fenêtre
        :param symbole: "info", "warning", "error" ou "question"
        """
        super().__init__(parent)
        self.resultat = annuler
        self.title(titre or "")
        self.resizable(False, False)
        if parent is not None and parent.winfo_toplevel().winfo_viewable():
            self.transient(parent.winfo_toplevel())

        corps = Frame(self)
        corps.pack(padx = 15, pady = 15)
        Label(corps, image = _ICONES[symbole]).grid(row = 0, column = 0, padx = (0, 15), sticky = "n")
        Label(corps, text = texte or "", justify = "left", wraplength = 420).grid(row = 0, column = 1, sticky = "w")

        ligne = Frame(self)
        ligne.pack(pady = (0, 12))
        for libelle, valeur in boutons:
            b = Button(ligne, text = libelle, width = 10, command = lambda v = valeur: self._fermer(v))
            b.pack(side = "left", padx = 5)
            if valeur == defaut:
                b.focus_set()
                self.bind("<Return>", lambda e, v = valeur: self._fermer(v))
        self.bind("<Escape>", lambda e: self._fermer(annuler))
        self.protocol("WM_DELETE_WINDOW", lambda: self._fermer(annuler))

        self._centrer(parent)
        self.wait_visibility()
        self.grab_set()                 # modale : bloque les autres fenêtres
        self.wait_window()


    def _fermer(self, valeur):
        self.resultat = valeur
        self.destroy()


    def _centrer(self, parent):
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        if parent is not None:
            top = parent.winfo_toplevel()
            x = top.winfo_rootx() + (top.winfo_width() - w) // 2
            y = top.winfo_rooty() + (top.winfo_height() - h) // 2
        else:
            x = (self.winfo_screenwidth() - w) // 2
            y = (self.winfo_screenheight() - h) // 2
        self.geometry("+%d+%d" % (max(x, 0), max(y, 0)))


################################################################################
def _boite(options, titre, texte, boutons, defaut, annuler, symbole):
    parent = options.get("parent") or tkinter._default_root
    return _Dialogue(parent, titre, texte, boutons, defaut, annuler, options.get("icon", symbole)).resultat


def showinfo(title = None, message = None, **options):
    _boite(options, title, message, [("OK", True)], True, True, "info")
    return "ok"

def showwarning(title = None, message = None, **options):
    _boite(options, title, message, [("OK", True)], True, True, "warning")
    return "ok"

def showerror(title = None, message = None, **options):
    _boite(options, title, message, [("OK", True)], True, True, "error")
    return "ok"

def askyesno(title = None, message = None, **options):
    """options : parent, icon ("question" par défaut), default ("yes" ou "no")"""
    defaut = options.get("default", "yes") == "yes"
    return _boite(options, title, message, [("Oui", True), ("Non", False)], defaut, False, "question")

def askokcancel(title = None, message = None, **options):
    """options : parent, icon ("question" par défaut), default ("ok" ou "cancel")"""
    defaut = options.get("default", "ok") == "ok"
    return _boite(options, title, message, [("OK", True), ("Annuler", False)], defaut, False, "question")
