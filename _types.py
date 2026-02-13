import datetime
from dataclasses import dataclass, field


@dataclass
class Seance:
    dtStart: datetime.datetime
    dtEnd: datetime.datetime
    salle: str
    Prof_ID: str
    titre: str
    Nom_Prof: str

    def __repr__(self):
        return f"Seance(dtStart='{self.dtStart}', dtEnd='{self.dtEnd}', salle='{self.salle}', Prof_ID='{self.Prof_ID}')"


@dataclass
class Cours:
    duree:int
    titre:str
    nb_etudiant:int
    Prof_ID:str
    requirments:str=""

@dataclass
class Professeur:
    Prof_ID:str
    Nom:str
    disponibilites:list=field(default_factory=list)


@dataclass
class Salle:
    Salle_ID:str
    capacite: int
    disponibilites:list=field(default_factory=list)
    tags: str = ""

