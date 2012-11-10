import tempfile
from path import path
import flask
import requests
import database
from datetime import datetime


def refresh_json():
    app = flask.current_app
    instance_path = path(app.instance_path)
    json_path = path(app.instance_path)/'hartapoliticii-people.json'
    with tempfile.NamedTemporaryFile(dir=instance_path, delete=False) as t:
        r = requests.get("http://hartapoliticii.ro/"
                         "api/search.php?api_key=%s"
                         % app.config['HPOL_API_KEY'])
        for chunk in r.iter_content(65536):
            t.write(chunk)
    path(t.name).rename(json_path)


def update_identities():
    app = flask.current_app
    json_path = path(app.instance_path)/'hartapoliticii-people.json'
    if not json_path.isfile():
        refresh_json()

    now = datetime.utcnow().strftime('%Y-%m-%d')

    hpol_map = {}
    with json_path.open() as f:
        for hpol_person in flask.json.load(f):
            hpol_map[hpol_person['id']] = hpol_person['name']

    for person in database.Person.objects_current().all():
        hpol_id = person.get_meta('hpol_id')
        #print "ok:", hpol_id, person.id
        hpol_map.pop(hpol_id, None)

    for hpol_id, hpol_name in hpol_map.iteritems():
        print "importing: %r %r %s" % (hpol_id, hpol_name, now)
        person = database.Person(name=hpol_name)
        database.db.session.add(person)
        meta = database.PersonMeta(person=person, key='hpol_id', value=hpol_id)
        database.db.session.add(meta)

    database.db.session.commit()
