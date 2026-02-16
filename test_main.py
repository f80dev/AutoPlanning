from _types import Professeur, Plage
from main import intersection, Agenda

def test_intersection():
    p1=(1,3)
    p2=(2,4)
    assert intersection(p1,p2)==(2,3)

    p3=(10,12)
    assert intersection(p1,p3) is None
    assert intersection(p3,p1) is None


def test_init_liste():
    a=Agenda()
    a.init_listes(classeur_id ="./planning.xlsx" )


def test_create_dispo():
    l=[
        Plage({"dtStart":"4/2 10:00","dtEnd":"4/2 12:00"}),
        Plage({"dtStart":"4/2 16:00","dtEnd":"4/2 21:00"})
    ]
    p=Professeur("prof1","Prof1",l)
    dispos=Agenda().create_disponibilite(p.dispos, 8, 20)
    print(dispos)

