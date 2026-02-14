
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