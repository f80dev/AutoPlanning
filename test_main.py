from _types import Professeur, Plage, union, intersection
from main import Agenda



def test_init_liste():
    a=Agenda()
    a.init_listes(classeur_id ="./planning.xlsx",periode_recurence=300 )

def test_run():
    a=Agenda()
    a.run("./planning.xlsx")


def test_recherche_dispo():
    l = [
        Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 12:00"}),
        Plage({"dtStart": "4/2 16:00", "dtEnd": "4/2 21:00"})
    ]

def test_union():
    l = [
        Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 12:00"}),
        Plage({"dtStart": "4/2 16:00", "dtEnd": "4/2 21:00"}),
        Plage({"dtStart": "4/2 22:00", "dtEnd": "4/2 23:00"})
    ]
    l=union(l)
    assert len(l)==3

    l = [
        Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 12:00"}),
        Plage({"dtStart": "4/2 11:00", "dtEnd": "4/2 21:00"}),
        Plage({"dtStart": "4/2 22:00", "dtEnd": "4/2 23:00"})
    ]
    l = union(l)
    assert len(l) == 2
    assert l[0].dtStart.hour==10
    assert l[0].dtEnd.hour==21




def test_intersection():
    l = [
        Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 12:00"}),
        Plage({"dtStart": "4/2 16:00", "dtEnd": "4/2 21:00"})
    ]
    r=intersection(l[0],l[1])
    assert r is None

    l = [
        Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 12:00"}),
        Plage({"dtStart": "4/2 11:00", "dtEnd": "4/2 21:00"})
    ]
    r = intersection(l[0],l[1])
    assert r.dtStart.hour==11
    assert r.dtEnd.hour==12





def test_create_dispo():
    l=[
        Plage({"dtStart":"4/2 10:00","dtEnd":"4/2 12:00"}),
        Plage({"dtStart":"4/2 16:00","dtEnd":"4/2 21:00"})
    ]
    p=Professeur("prof1","Prof1",l)
    dispos=Agenda().create_disponibilite(p.dispos, 8, 20)
    print(dispos)

