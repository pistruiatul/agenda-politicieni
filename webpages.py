# encoding: utf-8
import os.path
import flask
import auth
import database


_data_dir = os.path.join(os.path.dirname(__file__), 'data')
with open(os.path.join(_data_dir, 'prop_defs.json'), 'rb') as f:
    prop_defs = flask.json.load(f)


webpages = flask.Blueprint('webpages', __name__)


@webpages.route('/test_error')
@auth.require_admin
def test_error():
    raise ValueError("Just checking.")


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
    return flask.render_template('person.html',
                                 person=person,
                                 prop_map=prop_map)


@webpages.route('/person/<int:person_id>/suggest', methods=['GET', 'POST'])
def suggest(person_id):
    errors = []

    user = flask.g.user
    if user is None:
        errors.append(u"Vă rugăm să vă autentificați")

    if flask.request.method == 'POST':
        form = flask.request.form
        name = form.get('name')
        if name not in prop_defs:
            flask.abort(400)
        value = form.get('value')
        # TODO save something

    return flask.render_template('suggest.html',
            person=database.Person.query.get_or_404(person_id),
            errors=errors)


def init_app(app):
    app.register_blueprint(webpages)
    app.jinja_env.globals['known_names'] = prop_defs
    app.jinja_env.filters['datetime'] = lambda v: v.strftime('%d %b, %H:%M')
