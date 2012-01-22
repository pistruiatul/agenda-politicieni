# encoding: utf-8
import os.path
import flask
import auth
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
                   for s in person.suggestions.filter_by(decision=None)]
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
        form = flask.request.form
        name = form.get('name')
        if name not in prop_defs:
            flask.abort(400)
        value = form.get('value')

        if not errors:
            suggestion = database.save_suggestion(user, person_id, name, value)
            url = flask.url_for('webpages.person', person_id=person_id)

            if auth.is_admin(user) and form.get('auto-approve', '') == 'on':
                return decision(suggestion.id, 'accept', url)

            flask.flash(u"Sugestia de %s pentru %s a fost salvată, mulțumim!" %
                        (prop_defs[name], suggestion.person.name))
            return flask.redirect(url)

    return flask.render_template('suggest.html',
            person=database.Person.query.get_or_404(person_id),
            errors=errors)


@webpages.route('/suggestions')
@auth.require_admin
def suggestions():
    return flask.render_template('suggestions.html',
            suggestions=database.Suggestion.query.filter_by(decision=None))


@webpages.route('/suggestions/<int:suggestion_id>/accept',
                methods=['POST'], defaults={'decision': 'accept'})
@webpages.route('/suggestions/<int:suggestion_id>/reject',
                methods=['POST'], defaults={'decision': 'reject'})
def decision(suggestion_id, decision, redirect_to=None):
    suggestion = database.decision(suggestion_id, flask.g.user, decision)
    decision_label = {'accept': u"aprobată", 'reject': u"ștearsă"}[decision]
    flask.flash(u'Sugestie %s: %s la %s' % (decision_label,
                                            prop_defs[suggestion.name],
                                            suggestion.person.name))
    return flask.redirect(redirect_to or flask.url_for('webpages.suggestions'))


def suggestions_count():
    return database.Suggestion.query.filter_by(decision=None).count()


def init_app(app):
    app.register_blueprint(webpages)
    app.jinja_env.globals['known_names'] = prop_defs
    app.jinja_env.globals['suggestions_count'] = suggestions_count
