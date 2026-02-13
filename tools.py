from datetime import datetime

from _types import Seance


def filter(seances:list[Seance],dtStart:datetime,dtEnd:datetime):
    return [s for s in seances if s.dtStart>=dtStart and s.dtEnd<=dtEnd]


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



def intersection(plage1:tuple,plage2:tuple):
    rc=(max(plage1[0],plage2[0]),min(plage1[1],plage2[1]))
    if rc[0]<rc[1]:
        return rc
    else:
        return None
