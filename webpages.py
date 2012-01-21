# encoding: utf-8
import os.path
import flask
import database


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
    prop_map = dict((p.name, p.value) for p in person.properties.all())
    suggestions = [{'name': s.name, 'value': s.value, 'date': s.date}
                   for s in person.suggestions.all()]
    return flask.render_template('person.html',
                                 person=person,
                                 prop_map=prop_map,
                                 suggestions=suggestions)


@webpages.route('/person/<int:person_id>/suggest', methods=['GET', 'POST'])
def suggest(person_id):
    errors = []

    user = flask.g.user
    if user is None:
        errors.append(u"Vă rugăm să vă autentificați")

    if flask.request.method == 'POST':
        name = flask.request.form.get('name')
        if name not in prop_defs:
            flask.abort(400)
        value = flask.request.form.get('value')

        if not errors:
            suggestion = database.save_suggestion(user, person_id, name, value)
            flask.flash(u"Sugestia de %s pentru %s a fost salvată, mulțumim!" %
                        (prop_defs[name], suggestion.person.name))
            url = flask.url_for('webpages.person', person_id=person_id)
            return flask.redirect(url)

    return flask.render_template('suggest.html',
            person=database.Person.query.get_or_404(person_id),
            errors=errors)


def init_app(app):
    app.register_blueprint(webpages)
    app.jinja_env.globals['known_names'] = prop_defs
