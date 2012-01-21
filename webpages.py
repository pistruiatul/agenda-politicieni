import os.path
import flask
import database
import logging


log = logging.getLogger(__name__)


_data_dir = os.path.join(os.path.dirname(__file__), 'data')
with open(os.path.join(_data_dir, 'prop_defs.json'), 'rb') as f:
    prop_defs = flask.json.load(f)


webpages = flask.Blueprint('webpages', __name__)


@webpages.route('/')
def home():
    return flask.render_template('homepage.html',
                                 persons=database.get_persons())


@webpages.route('/download.json')
def download():
    return flask.jsonify(database.get_persons())


@webpages.route('/person/<int:person_id>')
def person(person_id):
    person = database.Person.query.get_or_404(person_id)
    prop_map = {p.name: p.value for p in person.properties.all()}
    suggestions = [{'name': s.name, 'value': s.value, 'date': s.date}
                   for s in person.suggestions.all()]
    return flask.render_template('person.html',
                                 person=person,
                                 prop_map=prop_map,
                                 suggestions=suggestions)


@webpages.route('/person/<int:person_id>/suggest', methods=['GET', 'POST'])
def suggest(person_id):
    if flask.request.method == 'POST':
        name = flask.request.form.get('name')
        if name not in prop_defs:
            flask.abort(400)
        value = flask.request.form.get('value')
        log.info('New suggestion: name=%r, value=%r', name, value)
        database.save_suggestion(person_id, name, value)

    return flask.render_template('suggest.html',
            person=database.Person.query.get_or_404(person_id))


def init_app(app):
    app.register_blueprint(webpages)
    app.jinja_env.globals['known_names'] = prop_defs
