
from Pile import *

def rpn(expression):
    p = Pile
    for c in expression:
        if c.isnumeric():
            p.push(c)
        elif c in "+-*/":
            prems = get_dernier_r()
            deuxio = supprimer_fin(), get_dernier_r()


print(rpn("4 5 * 9 + 6 / 2 -"))