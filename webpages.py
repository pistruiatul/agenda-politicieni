# encoding: utf-8
import os.path
from functools import wraps
from pytz import timezone
import cStringIO
import csv
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
    return {'persons': database.Person.query.order_by('name').all()}


@webpages.route('/download')
def download():
    fmt = flask.request.args.get('format')
    if fmt == 'json':
        rows = [dict(person.get_content(), id=person.id, name=person.name)
                for person in database.Person.query.all()]
        return flask.jsonify({'persons': rows})

    elif fmt == 'csv':
        utf8 = lambda v: unicode(v).encode('utf-8')
        fields = ['id', 'name'] + sorted(prop_defs.keys())
        header = dict((k, utf8(v)) for k, v in prop_defs.iteritems())
        header.update(id='id', name='Nume')

        csvfile = cStringIO.StringIO()
        csvwriter = csv.DictWriter(csvfile, fields)
        csvwriter.writerow(header)

        for person in database.Person.query.all():
            bytes_row = {'id': str(person.id), 'name': utf8(person.name)}
            for key, value_list in person.get_content().iteritems():
                bytes_row[key] = '; '.join(utf8(v) for v in value_list)

            csvwriter.writerow(bytes_row)

        return flask.Response(csvfile.getvalue(), mimetype='text/csv')

    else:
        flask.abort(404)


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


@webpages.route('/history')
@with_template('all_history.html')
def all_history():
    time_desc = database.ContentVersion.time.desc()
    return {
        'versions': database.ContentVersion.query.order_by(time_desc).all(),
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


@webpages.route('/person/<int:person_id>/diff/<int:a_id>...<int:b_id>')
@with_template('diff.html')
def diff(person_id, a_id, b_id):
    person = database.Person.query.get_or_404(person_id)
    a = person.versions.filter_by(id=a_id).first_or_404()
    b = person.versions.filter_by(id=b_id).first_or_404()
    return {
        'person': person,
        'version_a': a,
        'version_b': b,
    }


def init_app(app):
    app.register_blueprint(webpages)
    app.jinja_env.globals['known_names'] = prop_defs

    local_timezone = timezone(app.config['TIMEZONE'])
    def filter_datetime(utc_value, fmt='%d %b, %H:%M'):
        return local_timezone.fromutc(utc_value).strftime(fmt)
    app.jinja_env.filters['datetime'] = filter_datetime
