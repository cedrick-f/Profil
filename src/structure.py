#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#
#   module : structure
#
#
################################################################################

# Modules "python"
from typing import Any, List, Optional, Tuple
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, unescape
import os, sys


# Modules "application"



################################################################################
class XMLMixin:
    """ Classe Mixin pour permettre l'enregistrement et la restauration des objets
        au format XML
    """
    def __init__(self, code: Optional['XMLMixin'] = None):
        #print("__init__XMLMixin :", code)
        if code is None:
            code = self.__class__.__name__
            #print(type(code))
        self._codeXML = code
        #
        super(XMLMixin, self).__init__()



    ############################################################################
    def get_elem(self) -> List[str]:
        """ Renvoie la liste des noms des attributs
            devant figurer dans le fichier de structure

            Par défaut, tous les attributs sauf les attributs privés "_"

            A surcharger pour personnaliser
        """
        return [attr for attr in self.__dict__ if attr[0] != "_"]


    ############################################################################
    def to_xml(self) -> ET.Element:
        """ Renvoie la branche xml (ET.Element)
            contenant les attributs à integrer à la structure
            obtenus par get_elem()

            Fonction récursive si l'attribut est un XMLMixin
        """
        #print('to_xml', self._codeXML)

        ref = ET.Element(self._codeXML)

        def sauv(branche: ET.Element, val: Any, nom: Optional[str] = None):
            #print("   ", nom, type(val))
            if type(val) == str:
                #print('!!!', ("S_"+nom, escape(val)))
                branche.set("S_"+nom, escape(val))

            elif type(val) == int:
                branche.set("I_"+nom, str(val))

            elif type(val) == float:
                branche.set("F_"+nom, str(val))

            elif type(val) == bool:
                branche.set("B_"+nom, str(val))

            elif type(val) == list or type(val) == tuple:
                sub = ET.SubElement(branche, "l_"+nom)
                for i, sv in enumerate(val):
                    sauv(sub, sv, format(i, "02d"))

            elif type(val) == dict:
                sub = ET.SubElement(branche, "d_"+nom)
                for k, sv in val.items():
                    if type(k) != str: # c'est un entier
                        k = "_"+format(k, "02d")
                    sauv(sub, sv, k)

            elif isinstance(val, XMLMixin):
                branche.append(val.to_xml())


        for attr in self.get_elem():
            val = getattr(self, attr)
            sauv(ref, val, attr)

        return ref




    ############################################################################
    def from_xml(self, branche: ET.Element) -> Tuple['XMLMixin', List[str]]:
        """ Modifie la valeur des attributs intégrés à la structure
            obtenus par get_elem()
            et enregistrés ddans la branche (ET.Element)

            Fonction récursive si l'attribut est un XMLMixin
        """

        nomerr: List[str] = []

        def lect(branche: ET.Element, nom: str = "", num: int = -1):
            if nom[:2] == "S_":
                return unescape(branche.get(nom))

            elif nom[:2] == "I_":
                return int(branche.get(nom))


            elif nom[:2] == "F_":
                return float(branche.get(nom))

            elif nom[:2] == "B_":
                return branche.get(nom)[0] == "T"

            elif nom[:2] == "l_":
                sbranche = branche.find(nom)
                if sbranche is None:
                    return []
                dic = {}
                
                # éléments "simples" : dans les items
                for k, sb in sbranche.items():
                    _k = k.split("_")[-1]
                    dic[_k] = lect(sbranche, k)

                # éléments plus complexes : comme sous-élément
                for n, sb in enumerate(sbranche):
                    k = sb.tag
                    _k = k.split("_")[-1]
                    dic[_k+str(n)] = lect(sbranche, k, num = n)
                
                return [dic[v] for v in sorted(dic)]

            elif nom[:2] == "d_":
                sbranche = branche.find(nom)
                d = {}
                if sbranche != None:
                    for k, sb in sbranche.items():
                        _k = k.split("_")[1]
                        d[_k] = lect(sbranche, k)

                    for sb in sbranche:
                        k = sb.tag
                        _k = k.split("_")
                        if len(_k) == 3:
                            try:
                                _k = int(_k[2])
                            except:
                                _k = "_".join(_k[1:])
                        else:
                            _k = _k[1]
                        d[_k] = lect(sbranche, k)
                return d

            else:
                if num >= 0:
                    sbranche = branche.findall(nom)[num]
                else:
                    sbranche = branche.find(nom)
                classe = get_class(nom.split("_")[0], "contenu")
                obj, err = classe().from_xml(sbranche)
                nomerr.extend(err)
                return obj



        for attr in self.get_elem():
            val = getattr(self, attr)
            if type(val) == str:
                _attr = "S_"+attr

            elif type(val) == int:
                _attr = "I_"+attr

            elif type(val) == float:
                _attr = "F_"+attr

            elif type(val) == bool:
                _attr = "B_"+attr

            elif type(val) == list:
                _attr = "l_"+attr

            elif type(val) == dict:
                _attr = "d_"+attr

            else:
                _attr = None

            if _attr is not None:
                v = lect(branche, _attr)
                setattr(self, attr, v)

        return self, nomerr



    ############################################################################
    def sauver_xml(self, nom_fichier: str):
        tree = ET.ElementTree(self.to_xml())
        tree.write(nom_fichier, encoding = "utf-8", xml_declaration = True)



    ############################################################################
    def restaurer_xml(self, nom_fichier: str):
        tree = ET.parse(nom_fichier)
        self.from_xml(tree.getroot())



def get_class( kls ,module = "" ):
    """ Renvoie l'objet class de nom kls
        depuis le module spécifié
    """
    parts = kls.split('.')
    if module == "":
        module = ".".join(parts[:-1])
        parts = parts[1:]
    m = __import__( module )
    for comp in parts:
        m = getattr(m, comp)            
    return m



################################################################################
if __name__ == "__main__":
    class Test(XMLMixin):
        def __init__(self):
            super(Test, self).__init__()
            self.attr1 = 1
            self.attr2 = "coucou"
            self._attr3 = "NON"
            self.attr_4 = ssTest()

    class ssTest(XMLMixin):
        def __init__(self):
            super(ssTest, self).__init__()
            self.attr01 = 100
            self.attr02 = "hello <>"



    base = "C:\\Users\\Cedrick\\Documents\\Developp\\Profil"
    test = Test()
    test.attr1 = 2
    test.attr2 = "bin\ngo !"
    #print(test.get_elem())
    #print(vars(test))


    test.sauver_xml(os.path.join(base, "text.xml"))

    test2 = Test()
    print(vars(test2))
    test2.restaurer_xml(os.path.join(base, "text.xml"))
    print(vars(test2))
    print(test2.attr2)

    # from contenu import *
    #
    # pp = os.path.join(os.getenv('APPDATA'), 'Mozilla','Firefox','Profiles')
    # print(pp)
    # contenu.__FF.sauver_xml(os.path.join(base, "text.xml"))
