import pytest
from api import app, init_professeurs, init_salles, init_cours
from _types import Professeur, Salle, Cours

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_read_root(client):
    response = client.get("/calendar/export.ics?tags=tag1,tag2")
    assert response.status_code == 200


def test_init_professeurs():
    professeurs = init_professeurs(periode_recurence=30)
    assert isinstance(professeurs, list)
    assert len(professeurs) > 0
    assert all(isinstance(p, Professeur) for p in professeurs)
    assert all(isinstance(p.dispos, list) for p in professeurs)


def test_init_salles():
    salles = init_salles(periode_recurence=30)
    assert isinstance(salles, list)
    assert len(salles) > 0
    assert all(isinstance(s, Salle) for s in salles)
    assert all(isinstance(s.dispos, list) for s in salles)


def test_init_cours():
    cours = init_cours(periode_recurence=30)
    assert isinstance(cours, list)
    assert len(cours) > 0
    assert all(isinstance(c, Cours) for c in cours)


@pytest.mark.parametrize("route, expected_keys", [
    ("/professeurs", {"Prof_ID", "Nom", "dispos"}),
    ("/salles", {"Salle_ID", "Nom", "capacite", "dispos", "tags"}),
    ("/cours", {"duree", "titre", "groupe", "minDate", "maxDate", "Prof_ID", "props", "requirments"}),
])
def test_routes_nouvelles(client, route, expected_keys):
    response = client.get(route)
    assert response.status_code == 200
    assert response.mimetype == "application/json"

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert expected_keys.issubset(data[0].keys())


def test_route_professeurs_dispos_serialisees(client):
    data = client.get("/professeurs").get_json()
    dispos = [d for p in data for d in p["dispos"]]
    assert len(dispos) > 0
    assert all({"dtStart", "dtEnd"}.issubset(d.keys()) for d in dispos)


def test_route_salles_dispos_serialisees(client):
    data = client.get("/salles").get_json()
    dispos = [d for s in data for d in s["dispos"]]
    assert len(dispos) > 0
    assert all({"dtStart", "dtEnd"}.issubset(d.keys()) for d in dispos)
