# mode.py
import sys
EXE = getattr(sys, "frozen", False)   # True si lancé via le .exe (cx_Freeze)
TEST = not EXE                        # True si lancé via "python stp.py"