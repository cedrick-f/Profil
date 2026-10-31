#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyse_build.py : où passe la place dans la distribution générée par cx_Freeze ?

    python analyse_build.py                 # analyse build/bin
    python analyse_build.py chemin/du/dossier

Affiche : taille totale, répartition par dossier, contenu de library.zip (par paquet),
les plus gros fichiers, les fichiers en double, et la présence de paquets suspects
(tests, outils de compilation, bibliothèques inutiles...).
Ne modifie rien.
"""
import collections
import hashlib
import os
import sys
import zipfile

SUSPECTS = ["cx_Freeze", "setuptools", "pkg_resources", "pip", "wheel", "distutils", "lief",
            "PIL", "requests", "urllib3", "numpy", "markdown", "tkhtmlview",
            "unittest", "test", "tests", "SelfTest", "idlelib", "lib2to3", "turtledemo",
            "pydoc_data", "doctest", "tkinter/test"]


def mo(n):
    return "%7.2f Mo" % (n / 1e6)


def fichiers(racine):
    for dp, _, fs in os.walk(racine):
        for f in fs:
            p = os.path.join(dp, f)
            try:
                yield p, os.path.getsize(p)
            except OSError:
                pass


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def main(racine):
    if not os.path.isdir(racine):
        sys.exit("Dossier introuvable : " + racine)
    liste = list(fichiers(racine))
    total = sum(t for _, t in liste)
    print("DISTRIBUTION : %s\n  %s en %d fichiers\n" % (os.path.abspath(racine), mo(total).strip(), len(liste)))

    print("-- Par dossier de premier niveau " + "-" * 30)
    par = collections.Counter()
    for p, t in liste:
        par[os.path.relpath(p, racine).split(os.sep)[0]] += t
    for nom, t in par.most_common(12):
        print("  %s  %5.1f %%  %s" % (mo(t), 100 * t / total, nom))

    print("\n-- Dans lib/ " + "-" * 50)
    lib = os.path.join(racine, "lib")
    if os.path.isdir(lib):
        sous = collections.Counter()
        for p, t in fichiers(lib):
            sous[os.path.relpath(p, lib).split(os.sep)[0]] += t
        for nom, t in sous.most_common(15):
            print("  %s  %s" % (mo(t), nom))

    noms_zip = []
    for p, _ in liste:
        if p.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(p) as z:
                    infos = z.infolist()
            except zipfile.BadZipFile:
                continue
            print("\n-- Contenu de %s (octets non compressés / compressés) %s" % (os.path.relpath(p, racine), "-" * 5))
            gros, comp = collections.Counter(), collections.Counter()
            for i in infos:
                tete = i.filename.split("/")[0]
                gros[tete] += i.file_size
                comp[tete] += i.compress_size
                noms_zip.append(i.filename)
            for nom, t in gros.most_common(12):
                print("  %s / %s  %s" % (mo(t), mo(comp[nom]).strip(), nom))

    print("\n-- 20 plus gros fichiers " + "-" * 38)
    for p, t in sorted(liste, key=lambda x: -x[1])[:20]:
        print("  %s  %s" % (mo(t), os.path.relpath(p, racine)))

    print("\n-- Fichiers en double (même contenu, > 50 Ko) " + "-" * 18)
    par_taille = collections.defaultdict(list)
    for p, t in liste:
        if t > 50_000:
            par_taille[t].append(p)
    groupes, gaspille = [], 0
    for t, ps in par_taille.items():
        if len(ps) > 1:
            par_hash = collections.defaultdict(list)
            for p in ps:
                par_hash[sha(p)].append(p)
            for h, g in par_hash.items():
                if len(g) > 1:
                    groupes.append((t, g)); gaspille += t * (len(g) - 1)
    for t, g in sorted(groupes, reverse=True)[:10]:
        print("  %s x %d :" % (mo(t), len(g)))
        for p in g:
            print("        " + os.path.relpath(p, racine))
    print("  => place gaspillée par les doublons : %s" % mo(gaspille).strip() if groupes else "  aucun doublon")

    print("\n-- Paquets / dossiers à examiner (présents dans la distribution) " + "-" * 5)
    vus = collections.defaultdict(int)
    chemins = [os.path.relpath(p, racine).replace(os.sep, "/") for p, _ in liste] + noms_zip
    for c in chemins:
        morceaux = c.split("/")
        for s in SUSPECTS:
            if "/" in s:
                if s in c:
                    vus[s] += 1
            elif s in morceaux[:-1] or (morceaux[0] == s) or morceaux[-1].split(".")[0] == s:
                vus[s] += 1
    if vus:
        for s, n in sorted(vus.items()):
            print("  %-14s %5d fichiers" % (s, n))
    else:
        print("  aucun")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join("build", "bin"))
