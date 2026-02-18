from dataclasses import asdict

import pytz
from flask import Flask, Response, request, jsonify
from icalendar import Calendar, Event

from main import Agenda

app = Flask(__name__)
planning = Agenda().run()


@app.route("/calendar/json", methods=['GET'])
def get_filtered_json():
    """
    Test : http://127.0.0.1:5000/calendar/json?tags=tag1,tag2
    :return:
    """
    tags_from_list = request.args.getlist('tags')
    return jsonify([asdict(entry) for entry in planning.planning])


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

    for entry in planning.planning:
        # Logique de filtrage : on garde l'événement si un des tags correspond
        # ou si aucun tag n'est spécifié (comportement par défaut)
        if not tags or any(tag in entry.tags for tag in tags):
            event = Event()
            event.add('summary', entry.titre)
            event.add('dtstart', entry.plage.dtStart.astimezone(pytz.utc))
            event.add('dtend', entry.plage.dtStart.astimezone(pytz.utc))
            event.add('uid', f"event-{entry.titre}@mon-api.com")

            # Optionnel : ajouter les tags dans la description ICS
            event.add('description', f"Tags: {entry.titre}")

            cal.add_component(event)

    response = Response(
        cal.to_ical(),
        mimetype="text/calendar"
    )
    response.headers["Content-Disposition"] = "attachment; filename=filtre.ics"
    return response


if __name__ == '__main__':
    app.run(debug=True, port=8000)
