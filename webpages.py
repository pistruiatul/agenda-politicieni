# encoding: utf-8
import os.path
from functools import wraps
from pytz import timezone
import flask
import auth
import database


_data_dir = os.path.join(os.path.dirname(__file__), 'data')
with open(os.path.join(_data_dir, 'prop_defs.json'), 'rb') as f:
    prop_defs = flask.json.load(f)


webpages = flask.Blueprint('webpages', __name__)


def with_template(template_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is None:
                result = {}
            if isinstance(result, (dict,)):
                return flask.render_template(template_name, **result)
            else:
                return result
        return wrapper
    return decorator


@webpages.route('/test_error')
@auth.require_admin
def test_error():
    raise ValueError("Just checking.")


@webpages.route('/stats')
@auth.require_admin
@with_template('stats.html')
def stats():
    from datetime import datetime, time
    ContentVersion = database.ContentVersion
    today_0 = datetime.combine(datetime.utcnow(), time())
    edits_today = ContentVersion.query.filter(ContentVersion.time > today_0)
    return {
        'data': {
            'edits_today': edits_today.count(),
            'users': database.User.query.count(),
        },
    }


@webpages.route('/')
@with_template('homepage.html')
def home():
    return {'persons': database.get_persons()}


@webpages.route('/download.json')
def download():
    return flask.jsonify(database.get_persons())


@webpages.route('/person/<int:person_id>')
@with_template('person.html')
def person(person_id):
    person = database.Person.query.get_or_404(person_id)
    return {
        'person': person,
        'person_content': person.get_content(),
    }


@webpages.route('/person/<int:person_id>/edit', methods=['GET', 'POST'])
@auth.require_login
@with_template('edit.html')
def edit(person_id):
    person = database.Person.query.get_or_404(person_id)
    content = person.get_content()
    user = flask.g.user

    if flask.request.method == 'POST':
        form = flask.request.form
        new_content = {}
        for field_name in prop_defs:
            values = [v.strip() for v in form.getlist(field_name) if v.strip()]
            if values:
                new_content[field_name] = values

        if new_content != content:
            person.save_content_version(new_content, user)
            flask.flash(u"Conținutul a fost salvat", 'success')

        else:
            flask.flash(u"Conținutul este neschimbat")

        url = flask.url_for('webpages.person', person_id=person.id)
        return flask.redirect(url)

    person = database.Person.query.get_or_404(person_id)
    return {
        'person': person,
        'person_content': person.get_content(),
    }


@webpages.route('/person/<int:person_id>/history')
@with_template('history.html')
def history(person_id):
    person = database.Person.query.get_or_404(person_id)
    time_desc = database.ContentVersion.time.desc()
    return {
        'person': person,
        'versions': person.versions.order_by(time_desc).all(),
    }


def init_app(app):
    app.register_blueprint(webpages)
    app.jinja_env.globals['known_names'] = prop_defs

    local_timezone = timezone(app.config['TIMEZONE'])
    def filter_datetime(utc_value, fmt='%d %b, %H:%M'):
        return local_timezone.fromutc(utc_value).strftime(fmt)
    app.jinja_env.filters['datetime'] = filter_datetime
