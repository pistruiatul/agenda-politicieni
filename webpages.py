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


@webpages.route('/stats')
@auth.require_admin
def stats():
    from datetime import datetime, time
    ContentVersion = database.ContentVersion
    today_0 = datetime.combine(datetime.utcnow(), time())
    edits_today = ContentVersion.query.filter(ContentVersion.time > today_0)
    data = {
        'edits_today': edits_today.count(),
    }
    return flask.render_template('stats.html', data=data)


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
    return flask.render_template('person.html',
                                 person=person,
                                 person_content=person.get_content())


@webpages.route('/person/<int:person_id>/edit', methods=['GET', 'POST'])
def edit(person_id):
    errors = []
    person = database.Person.query.get_or_404(person_id)
    content = person.get_content()

    user = flask.g.user
    if user is None:
        msg = u"Vă rugăm să vă autentificați"
        return flask.render_template('message.html', errors=[msg])

    if flask.request.method == 'POST':
        form = flask.request.form
        new_content = {}
        for field_name in prop_defs:
            values = [v.strip() for v in form.getlist(field_name) if v.strip()]
            if values:
                new_content[field_name] = values

        if new_content != content:
            person.save_content_version(new_content, user)
            flask.flash(u"Conținutul a fost salvat")

        else:
            flask.flash(u"Conținutul este neschimbat")

        url = flask.url_for('webpages.person', person_id=person.id)
        return flask.redirect(url)

    person = database.Person.query.get_or_404(person_id)
    return flask.render_template('edit.html',
                                 person=person,
                                 person_content=person.get_content(),
                                 errors=errors)


def init_app(app):
    app.register_blueprint(webpages)
    app.jinja_env.globals['known_names'] = prop_defs
    app.jinja_env.filters['datetime'] = lambda v: v.strftime('%d %b, %H:%M')
