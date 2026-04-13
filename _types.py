import datetime
from dataclasses import dataclass, field
from random import Random

from tools import strtodate, get_idx_day_of_string


@dataclass
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
        assert self.dtStart <= self.dtEnd


    def duration(self):
        return (self.dtEnd-self.dtStart).total_seconds()/3600


    def contient(self,pl):
        return self.dtStart<=pl.dtStart and self.dtEnd>=pl.dtEnd


    def __str__(self):
        if self.dtStart.date() == self.dtEnd.date():
            return self.dtStart.strftime("%d/%m/%Y")+" "+self.dtStart.strftime("%H:%M")+" > "+self.dtEnd.strftime("%H:%M")
        else:
            return self.dtStart.strftime("%d/%m/%Y %H:%M")+" > "+self.dtEnd.strftime("%d/%m/%Y %H:%M")

    def to_dict(self):
        return {
            "dtStart": self.dtStart.isoformat(),
            "dtEnd": self.dtEnd.isoformat()
        }

    def requirment_day(self, contrainte:str) -> bool:
        if contrainte is None or len(contrainte)==0 or contrainte=="semaine": return True
        d=self.dtStart.day
        contrainte=contrainte.lower().split(" ")
        idx_day=get_idx_day_of_string(contrainte[0])
        if d!=idx_day: return False
        if len(contrainte)==2:
            if contrainte[1]=="am" and (self.dtStart.hour>12 or self.dtEnd.hour>12): return False
            if contrainte[1]=="pm" and (self.dtStart.hour<12 or self.dtEnd.hour<12): return False
        return True




@dataclass
class Distance:
    Salle_1:str
    Salle_2:str
    distance:int


class Cours:
    duree=2
    titre=""
    groupe=""
    minDate:datetime.datetime=datetime.datetime.now()
    maxDate:datetime.datetime=datetime.datetime.now()+datetime.timedelta(days=30)
    Prof_ID:str=""
    props={}
    requirments:str=""
    forces={}
    priorite=1

    def __str__(self):
        return f"Cours {self.titre} de {self.duree} heures, du groupe {self.groupe} - de {Plage(self.minDate,self.maxDate)} avec {self.Prof_ID} nécéssitant {self.requirments}"

    def __init__(self,d:dict):
        self.duree=d["duree"]
        self.titre=d["titre"]
        self.groupe=d["groupe"]
        self.minDate=strtodate(d["minDate"])
        self.maxDate=strtodate(d["maxDate"])
        self.Prof_ID=d["Prof_ID"]

        props=dict()
        forces=dict()
        for k in d:
            if k.startswith("p_"):
                props[k.split("p_")[1]]=d[k] if type(d[k])!=float else ""

            if k.startswith("c_"):
                forces[k.split("c_")[1]]=d[k].split(",") if type(d[k])==str else []

        self.props=props
        self.forces=forces

        self.requirments=d["requirments"]




@dataclass
class Professeur:
    Prof_ID:str
    Nom:str
    dispos:list[Plage]=field(default_factory=list[Plage])


@dataclass
class Salle:
    Salle_ID:str
    Nom:str
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
    props:dict
    group:str

    def __repr__(self):
        return f"Seance(dtStart='{self.dtStart}', dtEnd='{self.dtEnd}', salle='{self.salle}', Prof_ID='{self.Prof_ID}')"

    def to_dict(self) -> dict:
        d=self.__dict__
        d["dtStart"]=self.plage.dtStart
        d["dtEnd"] = self.plage.dtEnd
        return d




@dataclass
class Config:
    planning:list[Seance]
    distance:int=0
    reliquat:list[Cours]=field(default_factory=list[Cours])
    result:bool=False
    log:str=""

    def __str__(self):
        rc=""
        sorted(self.reliquat, key=lambda x: x.titre)
        for c in self.reliquat:
            rc=rc+f"\ncours problématiques {c}"

        rc=rc+f"\n\nJournal d'incident {self.log}"
        return rc



def intersection(p1: Plage, p2: Plage) -> Plage | None:
    rc = (max(p1.dtStart, p2.dtStart), min(p1.dtEnd, p2.dtEnd))
    if rc[0] < rc[1]:
        return Plage(rc[0],rc[1])
    else:
        return None


def soustraction(A: Plage, B: Plage) -> list[Plage]:
    """
    Soustrait la plage B de la plage A (A - B).
    Retourne une liste de 0, 1 ou 2 objets Plage.
    """
    # 1. Cas où il n'y a aucun chevauchement
    if B.dtStart >= A.dtEnd or B.dtEnd <= A.dtStart:
        return [A]

    # 2. Cas où B englobe totalement A (A devient vide)
    if B.dtStart <= A.dtStart and B.dtEnd >= A.dtEnd:
        return []

    resultats = []


    # 3. Segment restant au début (si B commence après A)
    if B.dtStart > A.dtStart:
        resultats.append(Plage(A.dtStart, B.dtStart))

    # 4. Segment restant à la fin (si B finit avant A)
    if B.dtEnd < A.dtEnd:
        resultats.append(Plage(B.dtEnd, A.dtEnd))

    return resultats




def check_plage(pl:list[Plage]):
    for p in pl:
        #print(f"Analyse de la plage {p}")
        if p.dtStart.weekday()==6 or p.dtEnd.weekday()==6 or p.dtStart.weekday()==5 or p.dtEnd.weekday()==5:
            raise RuntimeError(f"La plage {p} est sur un wekkend")

        if p.dtStart.minute!=0 or p.dtEnd.minute!=0:
            raise RuntimeError(f"La plage {p} est incorrecte")

    if len(union(pl))<len(pl):
        raise RuntimeError(f"Liste de plages non fusionnées")




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


