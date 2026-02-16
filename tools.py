from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from pyopenxlsx import Alignment, Border, Side






def union(periodes:list[tuple]):
    if not periodes:return []

    # 1. Trier les périodes par la borne de début
    # Complexité: O(n log n)
    periodes_triees = sorted(periodes, key=lambda x: x[0])

    fusionnees = []

    # 2. Initialiser avec la première période
    debut_actuel, fin_actuelle = periodes_triees[0]

    for i in range(1, len(periodes_triees)):
        prochain_debut, prochaine_fin = periodes_triees[i]

        # Si le début de la période suivante est avant ou égal à la fin de l'actuelle
        if prochain_debut <= fin_actuelle:
            # On fusionne en prenant la fin la plus éloignée
            fin_actuelle = max(fin_actuelle, prochaine_fin)
        else:
            # Pas de chevauchement, on ajoute la période précédente et on bascule
            fusionnees.append((debut_actuel, fin_actuelle))
            debut_actuel, fin_actuelle = prochain_debut, prochaine_fin

    # Ajouter la dernière période traitée
    fusionnees.append((debut_actuel, fin_actuelle))

    return fusionnees


def datetostr(dt:datetime) -> str:
    return dt.strftime("%m-%d %H:%M")

def plagetostr(plage:tuple) -> str:
    return datetostr(plage[0])+" -> "+datetostr(plage[1])

def strtodate(dt:str) -> datetime :
    if type(dt)==datetime: return dt
    dt = dt.replace("  ", " ").replace(" ", "/2026 ")
    return datetime.strptime(dt, "%d/%m/%Y %H:%M")



def exclude_from(plage1:tuple,plage2:tuple):
    s1, e1 = plage1
    s2, e2 = plage2

    # Si les plages ne se chevauchent pas, retourner la plage1 intacte
    if e2 <= s1 or s2 >= e1:
        return [plage1]

    result = []
    # S'il y a une partie de plage1 avant plage2
    if s1 < s2:
        result.append((s1, s2))

    # S'il y a une partie de plage1 après plage2
    if e1 > e2:
        result.append((e2, e1))

    return result
