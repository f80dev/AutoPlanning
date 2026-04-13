from _types import Professeur, Plage, union, intersection, soustraction, check_plage
from export import export_planning_to_json
from main import Agenda, export_dict_to_excel


def test_init_liste():
    a=Agenda()
    a.init_listes(classeur_id ="./planning.xlsm",periode_recurence=300 )

def test_export_agenda():
    a=Agenda()
    a.init_listes(classeur_id ="./planning_memoires.xlsm",periode_recurence=300 )
    a.export_to_excel("test.xlsx")


def test_run():
    a=Agenda()
    config=a.run("./planning_memoires.xlsm",max_occ=100,finder_occ=100,export="memoires")
    print(f"{config}")
    export_planning_to_json(a.seances,"planning_memoires.json")
    a.export_to_excel("plannification.xlsx")


def test_recherche_dispo():
    l = [
        Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 12:00"}),
        Plage({"dtStart": "4/2 16:00", "dtEnd": "4/2 21:00"})
    ]

def test_export_excel():
    export_dict_to_excel([{"a":1,"b":2},{"a":3,"b":4}],"test.xlsx","test")
    export_dict_to_excel([{"a": 1, "b": 2}, {"a": 3, "b": 4}], "test.xlsx", "test2")


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



def test_soustraction():
    A = Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 12:00"})
    B = Plage({"dtStart": "4/2 14:00", "dtEnd": "4/2 16:00"})
    assert soustraction(A, B) == [A]

    A=Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 13:00"})
    B=Plage({"dtStart": "4/2 11:00", "dtEnd": "4/2 14:00"})
    assert soustraction(A,B)==[Plage({"dtStart": "4/2 10:00","dtEnd":"4/2 11:00"})]

    A=Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 13:00"})
    B=Plage({"dtStart": "4/2 11:00", "dtEnd": "4/2 12:00"})
    assert soustraction(A,B)==[Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 11:00"}),Plage({"dtStart": "4/2 12:00", "dtEnd": "4/2 13:00"})]

    A=Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 12:00"})
    B=Plage({"dtStart": "4/2 09:00", "dtEnd": "4/2 11:00"})
    assert soustraction(A,B)==[Plage({"dtStart": "4/2 11:00", "dtEnd": "4/2 12:00"})]





def test_l_soustraction():
    a=Agenda()
    l = [
        Plage({"dtStart": "4/2 10:00", "dtEnd": "4/2 12:00"}),
        Plage({"dtStart": "5/2 11:00", "dtEnd": "5/2 21:00"}),
        Plage({"dtStart": "7/2 11:00", "dtEnd": "7/2 21:00"}),
        Plage({"dtStart": "14/2 11:00", "dtEnd": "14/2 21:00"}),
        Plage({"dtStart": "15/2 11:00", "dtEnd": "15/2 21:00"}),
    ]

    excludes = [
        Plage({"dtStart": "6/2 00:00", "dtEnd": "6/2 23:59"}),
        Plage({"dtStart": "5/2 14:00", "dtEnd": "5/2 15:00"}),
        Plage({"dtStart": "7/2 00:00", "dtEnd": "7/2 23:59"}),
        Plage({"dtStart": "14/2 00:00", "dtEnd": "14/2 23:59"}),
        Plage({"dtStart": "15/2 00:00", "dtEnd": "15/2 23:59"}),
    ]

    l=a.update_dispo_with_exclude(l,excludes)
    check_plage(l)
    print("")
    for p in l: print(f"Plage {p}")
    assert len(l)==3





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

