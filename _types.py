import datetime
from dataclasses import dataclass, field

from tools import strtodate

class Plage:
    dtStart:datetime.datetime
    dtEnd:datetime.datetime

    def __init__(self,dtStart:str | datetime.datetime | dict ,dtEnd:str | datetime.datetime =""):
        if type(dtStart)==dict:
            dtEnd=dtStart["dtEnd"]
            dtStart=dtStart["dtStart"]
        else:
            if dtEnd=="":
                if ">" in dtStart:
                    dtEnd=dtStart.split(" ")[0]+" "+dtStart.split(">")[1]
                    dtStart=dtStart.split(">")[0].strip()
                else:
                    dtEnd=strtodate(dtStart)+3600

        self.dtStart=strtodate(dtStart)
        self.dtEnd=strtodate(dtEnd)


    def __str__(self):
        if self.dtStart.date() == self.dtEnd.date():
            return self.dtStart.strftime("%d/%m/%Y")+" "+self.dtStart.strftime("%H:%M")+" > "+self.dtEnd.strftime("%H:%M")
        else:
            return self.dtStart.strftime("%d/%m/%Y %H:%M")+" > "+self.dtEnd.strftime("%d/%m/%Y %H:%M")


@dataclass
class Distance:
    Salle_1:str
    Salle_2:str
    distance:int


@dataclass
class Cours:
    duree:int
    titre:str
    groupe:str
    minDate:datetime.datetime
    maxDate:datetime.datetime
    Prof_ID:str
    nb_prof:int
    requirments:str=""

@dataclass
class Professeur:
    Prof_ID:str
    Nom:str
    dispos:list[Plage]=field(default_factory=list[Plage])


@dataclass
class Salle:
    Salle_ID:str
    capacite: int
    dispos:list[Plage]=field(default_factory=list[Plage])
    tags: str = ""

@dataclass
class Groupe:
    Groupe_ID:str
    effectif: int
    professeur:str=""



@dataclass
class Seance:
    plage: Plage
    salle: str
    Prof_ID: str
    titre: str
    group:str
    Nom_Prof: str
    tags: str = ""

    def __repr__(self):
        return f"Seance(dtStart='{self.dtStart}', dtEnd='{self.dtEnd}', salle='{self.salle}', Prof_ID='{self.Prof_ID}')"


@dataclass
class Config:
    planning:list[Seance]
    distance:int=0

def intersection(p1: Plage, p2: Plage) -> Plage | None:
    rc = (max(p1.dtStart, p2.dtStart), min(p1.dtEnd, p2.dtEnd))
    if rc[0] < rc[1]:
        return Plage(rc[0],rc[1])
    else:
        return None


def union(periodes:list[Plage]) -> list[Plage]:
    if not periodes:return []

    # 1. Trier les périodes par date de début
    periodes_triees = sorted(periodes, key=lambda x: x.dtStart)

    fusionnees = []

    # 2. Initialiser avec la première période
    (debut_actuel,fin_actuelle) = periodes_triees[0].dtStart,periodes_triees[0].dtEnd

    for i in range(1, len(periodes_triees)):
        prochain_debut, prochaine_fin = periodes_triees[i].dtStart,periodes_triees[i].dtEnd

        # Si le début de la période suivante est avant ou égal à la fin de l'actuelle
        if prochain_debut <= fin_actuelle:
            # On fusionne en prenant la fin la plus éloignée
            fin_actuelle = max(fin_actuelle, prochaine_fin)
        else:
            # Pas de chevauchement, on ajoute la période précédente et on bascule
            fusionnees.append(Plage(debut_actuel, fin_actuelle))
            debut_actuel, fin_actuelle = prochain_debut, prochaine_fin

    # Ajouter la dernière période traitée
    fusionnees.append(Plage(debut_actuel, fin_actuelle))

    return fusionnees

def exclude_from(dispos:list[Plage],indispo:Plage):
    rc=[]
    for d in dispos:
        if intersection(d,indispo) is None:
            rc.append(d)
        else:
            if indispo.dtStart < d.dtStart and indispo.dtEnd > d.dtEnd:
                #la plage disparait du fait de l'indispo
                pass
            else:
                if indispo.dtStart>d.dtStart and indispo.dtEnd<=d.dtEnd:
                    #la plage d'indispo est incluse dans la plage de dispo
                    rc.append(Plage(d.dtStart,indispo.dtStart))
                    rc.append(Plage(d.dtEnd,indispo.dtEnd))
                else:
                    if indispo.dtStart<d.dtStart:
                        #la plage d'indispo commence avant la plage de dispo
                        rc.append(Plage(indispo.dtEnd,d.dtEnd))
                    else:
                        #la plage d'indispo commence après la plage de dispo
                        rc.append(Plage(d.dtStart,indispo.dtStart))
    return rc



