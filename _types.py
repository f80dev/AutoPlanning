import datetime
from dataclasses import dataclass, field

from tools import strtodate




@dataclass
class Cours:
    duree:int
    titre:str
    groupe:str
    Prof_ID:str
    requirments:str=""

@dataclass
class Professeur:
    Prof_ID:str
    Nom:str
    dispos:list=field(default_factory=list)


@dataclass
class Salle:
    Salle_ID:str
    capacite: int
    dispos:list=field(default_factory=list)
    tags: str = ""

@dataclass
class Groupe:
    Groupe_ID:str
    effectif: int

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
class Seance:
    plage: Plage
    salle: str
    Prof_ID: str
    titre: str
    Nom_Prof: str

    def __repr__(self):
        return f"Seance(dtStart='{self.dtStart}', dtEnd='{self.dtEnd}', salle='{self.salle}', Prof_ID='{self.Prof_ID}')"



def intersection(p1: Plage, p2: Plage) -> Plage | None:
    rc = (max(p1.dtStart, p2.dtStart), min(p1.dtEnd, p2.dtEnd))
    if rc[0] < rc[1]:
        return Plage(rc[0],rc[1])
    else:
        return None