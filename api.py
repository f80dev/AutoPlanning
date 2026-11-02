import json
from dataclasses import asdict
from datetime import datetime, date

import pytz
from flask import Flask, Response, request
from icalendar import Calendar, Event

from main import Agenda
from _types import Professeur, Salle, Cours

app = Flask(__name__)
agenda=Agenda()

CLASSEUR_PLANNING = "./planning.xlsm"
PERIODE_RECURENCE = 360


def custom_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if hasattr(obj, "item"):
        return obj.item()
    raise TypeError(f"Type {type(obj)} not serializable")


def init_professeurs(classeur_id: str = CLASSEUR_PLANNING,
                     periode_recurence: int = PERIODE_RECURENCE) -> list[Professeur]:
    """
    Récupère et initialise l'ensemble des professeurs avec leurs disponibilités.
    :param classeur_id: Chemin ou ID du classeur de données.
    :param periode_recurence: Nombre de jours couverts par les récurrences.
    :return: La liste des objets Professeur initialisés.
    """
    agenda.init_listes(classeur_id, periode_recurence)
    return agenda.professeurs


def init_salles(classeur_id: str = CLASSEUR_PLANNING,
                periode_recurence: int = PERIODE_RECURENCE) -> list[Salle]:
    """
    Récupère l'ensemble des salles avec leurs disponibilités.
    :param classeur_id: Chemin ou ID du classeur de données.
    :param periode_recurence: Nombre de jours couverts par les récurrences.
    :return: La liste des objets Salle initialisés.
    """
    agenda.init_listes(classeur_id, periode_recurence)
    return agenda.salles


def init_cours(classeur_id: str = CLASSEUR_PLANNING,
               periode_recurence: int = PERIODE_RECURENCE) -> list[Cours]:
    """
    Récupère l'ensemble des cours du classeur.
    :param classeur_id: Chemin ou ID du classeur de données.
    :param periode_recurence: Nombre de jours couverts par les récurrences.
    :return: La liste des objets Cours initialisés.
    """
    agenda.init_listes(classeur_id, periode_recurence)
    return agenda.cours


@app.route("/professeurs", methods=['GET'])
def get_professeurs():
    """
    Test : http://127.0.0.1:5000/professeurs
    :return: La liste des professeurs et de leurs disponibilités au format JSON.
    """
    professeurs = init_professeurs()
    return Response(
        json.dumps([asdict(p) for p in professeurs], default=custom_serializer, ensure_ascii=False),
        mimetype="application/json"
    )


@app.route("/salles", methods=['GET'])
def get_salles():
    """
    Test : http://127.0.0.1:5000/salles
    :return: La liste des salles et de leurs disponibilités au format JSON.
    """
    salles = init_salles()
    return Response(
        json.dumps([asdict(s) for s in salles], default=custom_serializer, ensure_ascii=False),
        mimetype="application/json"
    )


@app.route("/cours", methods=['GET'])
def get_cours():
    """
    Test : http://127.0.0.1:5000/cours
    :return: La liste des cours au format JSON.
    """
    cours = init_cours()
    return Response(
        json.dumps([c.__dict__ for c in cours], default=custom_serializer, ensure_ascii=False),
        mimetype="application/json"
    )


@app.route("/calendar/json", methods=['GET'])
def get_filtered_json():
    """
    Test : http://127.0.0.1:5000/calendar/json?tags=tag1,tag2
    :return:
    """

    planning = agenda.run()

    tags_from_list = request.args.getlist('tags')
    tags = []
    if tags_from_list:
        tags = [tag.strip() for item in tags_from_list for tag in item.split(',')]

    filtered_planning = []
    for entry in planning.planning:
        # Logique de filtrage : on garde l'événement si un des tags correspond
        # ou si aucun tag n'est spécifié (comportement par défaut)
        if not tags or any(tag in entry.tags for tag in tags):
            filtered_planning.append(asdict(entry))

    return Response(
        json.dumps(filtered_planning, default=custom_serializer, ensure_ascii=False),
        mimetype="application/json"
    )


@app.route("/calendar/export.ics", methods=['GET'])
def get_filtered_ics():
    """
    Test : http://127.0.0.1:5000/calendar/export.ics?tags=tag1,tag2
    :return:
    """
    tags_from_list = request.args.getlist('tags')
    tags = []
    if tags_from_list:
        tags = [tag.strip() for item in tags_from_list for tag in item.split(',')]

    cal = Calendar()
    cal.add('prodid', '-//Mon API Filtrée//FR//')
    cal.add('version', '2.0')

    planning = agenda.run()
    for entry in planning.planning:
        # Logique de filtrage : on garde l'événement si un des tags correspond
        # ou si aucun tag n'est spécifié (comportement par défaut)
        if not tags or any(tag in entry.tags for tag in tags):
            event = Event()
            event.add('summary', entry.titre)
            event.add('dtstart', entry.plage.dtStart.astimezone(pytz.utc))
            event.add('dtend', entry.plage.dtEnd.astimezone(pytz.utc))
            event.add('uid', f"event-{entry.titre}@mon-api.com")

            # Optionnel : ajouter les tags dans la description ICS
            event.add('description', f"Tags: {entry.tags}")

            cal.add_component(event)

    response = Response(
        cal.to_ical(),
        mimetype="text/calendar"
    )
    response.headers["Content-Disposition"] = "attachment; filename=filtre.ics"
    return response


if __name__ == '__main__':
    app.run(debug=True, port=8000)
