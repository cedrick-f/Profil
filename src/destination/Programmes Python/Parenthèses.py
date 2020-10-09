from Pile import *


def parenthesesdemesdeux(expression):
    p = Pile()
    for c in expression:
        if c in "([{":
            p.push(c)
        elif c in ")]}":
            if p.est_vide():
                return False
            else:
                f = p.pop()
                if c == ")" and f != "(":
                    return False
                elif c == "]" and f != "[":
                    return False
                elif c == "}" and f != "{":
                    return False
    
    return p.est_vide()
    
    
expression = "[-(b)+sqrt(4*(a*c))]/(2*a)"
print(parenthesesdemesdeux(expression))