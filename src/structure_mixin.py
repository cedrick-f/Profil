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
import xml.etree.ElementTree as ET
import os


# Modules "application"



################################################################################
class XMLMixin:

    def get_elem(self):
        """ Renvoie la liste des noms des attributs
            devant figurer dans le fichier de structure

            Par défaut, tous les attributs sauf les attributs privés "_"

            A surcharger pour personnaliser
        """
        return [attr for attr in self.__dict__ if attr[0] != "_"]


    def to_xml(self):
        """ Renvoie la branche xml (ET.Element)
            contenant les attributs à integrer à la structure
            obtenus par get_elem()

            Fonction récursive si l'attribut est un XMLMixin
        """
        branche = ET.Element("tt")
        for attr in self.get_elem():
            e = getattr(self, attr)  # Équivalent à self.attr (mais attr est ici un str)
            if isinstance(e, XMLMixin):
                branche.append(e.to_xml())
            elif isinstance(e, str):
                branche.set(attr, e)
            ## .....

        return branche


    def from_xml(self, branche):
        """ Modifie la valeur des attributs intégrés à la structure
            obtenus par get_elem()
            et enregistrés ddans la branche (ET.Element)

            Fonction récursive si l'attribut est un XMLMixin
        """
        pass


    def sauve(self, nom_fichier):
        tree = ET.ElementTree(self.to_xml())
        tree.write(nom_fichier, encoding = "utf-8", xml_declaration = True)



















class XMLMixin():
    """ Classe Mixin pour permettre l'enregistrement et la restauration des objets
        au format XML
    """



    def __init__(self, code = None):
        super(XMLMixin, self).__init__()
        if code is None:
            code = type(self).__name__
        self._codeXML = code





    ######################################################################################
    def get_elem(self):
        """ Renvoie la liste des noms des attributs
            devant figurer dans le fichier de structure

            Par défaut, tous les attributs sauf les attributs privés "_"

            A surcharger pour personnaliser
        """
        return [attr for attr in self.__dict__ if attr[0] != "_"]



    ######################################################################################
    def to_xml(self):
        """ Renvoie la branche xml (ET.Element)
            contenant les attributs à integrer à la structure
            obtenus par get_elem()

            Fonction récursive si l'attribut est un XMLMixin
        """

        ref = ET.Element(self._codeXML)

        def sauv(branche, val, nom = None):
            if type(val) == str:
                branche.set("S_"+nom, val)

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
                branche.append(val.to_xml(nom))


        for attr in self.get_elem():
            val = getattr(self, attr)
            sauv(ref, val, attr)

        return ref




    ######################################################################################
    def from_xml(self, branche, module = ""):
        """ Modifie la valeur des attributs intégrés à la structure
            obtenus par get_elem()
            et enregistrés ddans la branche (ET.Element)

            Fonction récursive si l'attribut est un XMLMixin
        """


        nomerr = []

        def lect(branche, nom = ""):
            if nom[:2] == "S_":
                return str(branche.get(nom)).replace("--", "\n")

            elif nom[:2] == "I_":
                return int(branche.get(nom))


            elif nom[:2] == "F_":
                return float(branche.get(nom))

            elif nom[:2] == "B_":
                return branche.get(nom)[0] == "T"

            elif nom[:2] == "l_":
                sbranche = branche.find(nom)
                if sbranche == None: return []
                dic = {}

                # éléments "simples" : dans les items
                for k, sb in sbranche.items():
                    _k = k.split("_")[-1]
                    dic[_k] = lect(sbranche, k)


                # éléments plus complexes : comme sous-élément
                for sb in sbranche:
                    k = sb.tag
                    _k = k.split("_")[-1]
                    dic[_k] = lect(sbranche, k)
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
                sbranche = branche.find(nom)
                classe = get_class(nom.split("_")[0], module = module)
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

            if _attr != None:
                v = lect(branche, _attr)
                setattr(self, attr, v)

        return self, nomerr



    ######################################################################################
    def sauver(self, nom_fichier):
        tree = ET.ElementTree(self.to_xml())
        tree.write(nom_fichier, encoding = "utf-8", xml_declaration = True)



    ######################################################################################
    def restaurer(self, nom_fichier):
        tree = ET.parse(nom_fichier)
        self.from_xml(tree.getroot())






def get_class( kls ,module = ""):
    parts = kls.split('.')
    if module == "":
        module = ".".join(parts[:-1])
        parts = parts[1:]

#     print("  ", parts)

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
            #self.attr_4 = Test()


    base = "C:\\Users\\Cedrick\\Documents\\Developp\\Profil"
    test = Test()
    test.attr1 = 2
    test.attr2 = "bingo !"
    #print(test.get_elem())
    #print(vars(test))


    test.sauver(os.path.join(base, "text.xml"))

    test2 = Test()
    print(vars(test2))
    test2.restaurer(os.path.join(base, "text.xml"))
    print(vars(test2))
