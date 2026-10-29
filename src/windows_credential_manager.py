"""
Windows Credential Manager - Gestion des informations d'identité génériques
Utilise l'API Windows via ctypes (pas de dépendance externe requise)
ou optionnellement la bibliothèque 'keyring' / 'pywin32'.

Nécessite : Windows uniquement
Dépendance optionnelle : pip install pywin32
"""

import ctypes
import ctypes.wintypes
import struct
from dataclasses import dataclass
from typing import Optional
import sys

# ──────────────────────────────────────────────────────────────────────────────
# Vérification plateforme
# ──────────────────────────────────────────────────────────────────────────────
if sys.platform != "win32":
    raise EnvironmentError("Ce script fonctionne uniquement sous Windows.")

# ──────────────────────────────────────────────────────────────────────────────
# Constantes Windows
# ──────────────────────────────────────────────────────────────────────────────
CRED_TYPE_GENERIC = 1          # "Informations d'identité génériques"
CRED_PERSIST_LOCAL_MACHINE = 2 # Persistance sur la machine locale
CRED_PERSIST_ENTERPRISE = 3    # Persistance enterprise (roaming)

# ──────────────────────────────────────────────────────────────────────────────
# Structures ctypes correspondant à la structure CREDENTIAL de l'API Windows
# ──────────────────────────────────────────────────────────────────────────────
class CREDENTIAL_ATTRIBUTE(ctypes.Structure):
    _fields_ = [
        ("Keyword",   ctypes.c_wchar_p),
        ("Flags",     ctypes.wintypes.DWORD),
        ("ValueSize", ctypes.wintypes.DWORD),
        ("Value",     ctypes.c_char_p),
    ]

class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ("Flags",                 ctypes.wintypes.DWORD),
        ("Type",                  ctypes.wintypes.DWORD),
        ("TargetName",            ctypes.c_wchar_p),
        ("Comment",               ctypes.c_wchar_p),
        ("LastWritten",           ctypes.wintypes.FILETIME),
        ("CredentialBlobSize",    ctypes.wintypes.DWORD),
        ("CredentialBlob",        ctypes.POINTER(ctypes.c_byte)),
        ("Persist",               ctypes.wintypes.DWORD),
        ("AttributeCount",        ctypes.wintypes.DWORD),
        ("Attributes",            ctypes.POINTER(CREDENTIAL_ATTRIBUTE)),
        ("TargetAlias",           ctypes.c_wchar_p),
        ("UserName",              ctypes.c_wchar_p),
    ]

# ──────────────────────────────────────────────────────────────────────────────
# Chargement de advapi32.dll
# ──────────────────────────────────────────────────────────────────────────────
_advapi32 = ctypes.windll.advapi32

_advapi32.CredReadW.restype   = ctypes.wintypes.BOOL
_advapi32.CredWriteW.restype  = ctypes.wintypes.BOOL
_advapi32.CredDeleteW.restype = ctypes.wintypes.BOOL
_advapi32.CredEnumerateW.restype = ctypes.wintypes.BOOL
_advapi32.CredFree.restype    = None

# ──────────────────────────────────────────────────────────────────────────────
# Dataclass résultat
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class CredentialEntry:
    target_name: str
    username:    str
    password:    str
    comment:     str = ""
    persist:     int = CRED_PERSIST_LOCAL_MACHINE
    blob:        bytes = b""        # contenu brut exact (pour sauvegarde/restauration fidèles)


# ──────────────────────────────────────────────────────────────────────────────
# Fonctions principales
# ──────────────────────────────────────────────────────────────────────────────

def write_credential(
    target_name: str,
    username: str,
    password: str,
    comment: str = "",
    persist: int = CRED_PERSIST_LOCAL_MACHINE,
    blob: Optional[bytes] = None,
) -> None:
    """
    Crée ou met à jour une information d'identité générique dans le
    Gestionnaire d'informations d'identification Windows.

    Args:
        target_name : Identifiant unique de l'entrée (ex: "MonApp/Serveur")
        username    : Nom d'utilisateur associé
        password    : Mot de passe (sera stocké chiffré par Windows)
        comment     : Commentaire optionnel visible dans le gestionnaire
        persist     : CRED_PERSIST_LOCAL_MACHINE (2) ou CRED_PERSIST_ENTERPRISE (3)
        blob        : Si fourni, octets écrits tels quels à la place de `password`
                      (restauration exacte, y compris des données non textuelles)
    Raises:
        OSError: En cas d'échec de l'API Windows
    """
    password_bytes = blob if blob is not None else password.encode("utf-16-le")
    blob = (ctypes.c_byte * len(password_bytes))(*password_bytes)

    cred = CREDENTIAL()
    cred.Flags             = 0
    cred.Type              = CRED_TYPE_GENERIC
    cred.TargetName        = target_name
    cred.Comment           = comment or None
    cred.CredentialBlobSize = len(password_bytes)
    cred.CredentialBlob    = blob
    cred.Persist           = persist
    cred.AttributeCount    = 0
    cred.Attributes        = None
    cred.TargetAlias       = None
    cred.UserName          = username

    success = _advapi32.CredWriteW(ctypes.byref(cred), 0)
    if not success:
        raise OSError(ctypes.FormatError(ctypes.GetLastError()))

    print(f"[OK] Credential '{target_name}' enregistrée avec succès.")


def read_credential(target_name: str) -> CredentialEntry:
    """
    Lit une information d'identité générique depuis le Gestionnaire Windows.

    Args:
        target_name : Identifiant de l'entrée à lire

    Returns:
        CredentialEntry avec les champs target_name, username, password, comment

    Raises:
        KeyError  : Si l'entrée n'existe pas
        OSError   : En cas d'autre erreur Windows
    """
    cred_ptr = ctypes.POINTER(CREDENTIAL)()

    success = _advapi32.CredReadW(
        target_name,
        CRED_TYPE_GENERIC,
        0,
        ctypes.byref(cred_ptr),
    )

    if not success:
        err = ctypes.GetLastError()
        if err == 1168:  # ERROR_NOT_FOUND
            raise KeyError(f"Credential introuvable : '{target_name}'")
        raise OSError(ctypes.FormatError(err))

    try:
        cred = cred_ptr.contents

        # Décodage du blob (mot de passe) stocké en UTF-16-LE
        blob_size = cred.CredentialBlobSize
        if blob_size > 0:
            raw = bytes(cred.CredentialBlob[:blob_size])
            password = raw.decode("utf-16-le")
        else:
            password = ""

        return CredentialEntry(
            target_name = cred.TargetName or "",
            username    = cred.UserName   or "",
            password    = password,
            comment     = cred.Comment    or "",
            persist     = cred.Persist,
        )
    finally:
        _advapi32.CredFree(cred_ptr)


def delete_credential(target_name: str) -> None:
    """
    Supprime une information d'identité générique.

    Args:
        target_name : Identifiant de l'entrée à supprimer

    Raises:
        KeyError : Si l'entrée n'existe pas
        OSError  : En cas d'autre erreur Windows
    """
    success = _advapi32.CredDeleteW(target_name, CRED_TYPE_GENERIC, 0)
    if not success:
        err = ctypes.GetLastError()
        if err == 1168:
            raise KeyError(f"Credential introuvable : '{target_name}'")
        raise OSError(ctypes.FormatError(err))

    print(f"[OK] Credential '{target_name}' supprimée.")


def list_credentials(filter_prefix: Optional[str] = None) -> list[CredentialEntry]:
    """
    Liste toutes les credentials génériques (optionnellement filtrées par préfixe).

    Args:
        filter_prefix : Si fourni, seules les entrées dont le TargetName
                        commence par ce préfixe sont retournées.
                        Ex: "MonApp*" (wildcard supporté par Windows)

    Returns:
        Liste de CredentialEntry
    """
    count    = ctypes.wintypes.DWORD(0)
    creds_ptr = ctypes.POINTER(ctypes.POINTER(CREDENTIAL))()

    filter_str = filter_prefix if filter_prefix else None

    success = _advapi32.CredEnumerateW(
        filter_str,
        0,
        ctypes.byref(count),
        ctypes.byref(creds_ptr),
    )

    if not success:
        err = ctypes.GetLastError()
        if err == 1168:  # Aucune correspondance
            return []
        raise OSError(ctypes.FormatError(err))

    results = []
    try:
        for i in range(count.value):
            cred = creds_ptr[i].contents
            if cred.Type != CRED_TYPE_GENERIC:
                continue

            blob_size = cred.CredentialBlobSize
            if blob_size > 0:
                raw = bytes(ctypes.cast(cred.CredentialBlob, ctypes.POINTER(ctypes.c_ubyte * blob_size)).contents)
                try:
                    password = raw.decode("utf-16-le")
                except UnicodeDecodeError:
                    try:
                        # Fallback UTF-8 (certaines apps tierces)
                        password = raw.decode("utf-8")
                    except UnicodeDecodeError:
                        # Donnée binaire brute → représentation hex
                        password = f"<binaire: {raw.hex()}>"

            else:
                password = ""

            results.append(CredentialEntry(
                target_name = cred.TargetName or "",
                username    = cred.UserName   or "",
                password    = password,
                comment     = cred.Comment    or "",
                persist     = cred.Persist,
                blob        = raw if blob_size > 0 else b"",
            ))
    finally:
        _advapi32.CredFree(creds_ptr)

    return results


# ──────────────────────────────────────────────────────────────────────────────
# Démonstration interactive
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    TARGET = "MonApplication/TestCredential"

    print("=" * 60)
    print("  Démonstration Credential Manager Windows")
    print("=" * 60)

    # 1. Écriture
    print("\n[1] Écriture de la credential...")
    write_credential(
        target_name = TARGET,
        username    = "jean.dupont@example.com",
        password    = "MotDePasseSecret123!",
        comment     = "Credential de test créée par le script Python",
    )

    # 2. Lecture
    print("\n[2] Lecture de la credential...")
    entry = read_credential(TARGET)
    print(f"    TargetName : {entry.target_name}")
    print(f"    Username   : {entry.username}")
    print(f"    Password   : {entry.password}")
    print(f"    Comment    : {entry.comment}")
    print(f"    Persist    : {entry.persist}")

    # 3. Mise à jour
    print("\n[3] Mise à jour du mot de passe...")
    write_credential(
        target_name = TARGET,
        username    = "jean.dupont@example.com",
        password    = "NouveauMotDePasse456!",
        comment     = "Mise à jour via script Python",
    )
    entry = read_credential(TARGET)
    print(f"    Nouveau mot de passe : {entry.password}")

    # 4. Listing
    print("\n[4] Liste des credentials génériques (préfixe 'MonApplication')...")
    entries = list_credentials("MonApplication*")
    for e in entries:
        print(f"    - {e.target_name} | user={e.username}")

    # 5. Suppression
    print("\n[5] Suppression de la credential de test...")
    delete_credential(TARGET)

    print("\n[Terminé] Toutes les opérations ont réussi.")
