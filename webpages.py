# encoding: utf-8
import os.path
from functools import wraps
from pytz import timezone
import cStringIO
import csv
import flask
import auth
import database


office_defs = {
    'deputy': u"deputat",
    'senator': u"senator",
}


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
            'persons': database.Person.query.count(),
        },
    }


@webpages.route('/download')
def download():
    fmt = flask.request.args.get('format')
    def get_meta(person):
        meta = {}
        for key in database.meta_defs:
            value = person.get_meta(key)
            if value:
                meta[key] = value
        return meta

    from sqlalchemy.orm import joinedload
    query = (database.Person.objects_current()
             .options(joinedload(database.Person.meta),
                      joinedload(database.Person.versions)))

    if fmt == 'json':
        rows = [dict(person.get_content(),
                     id=person.id,
                     name=person.name,
                     _meta=get_meta(person))
                for person in query.all()]
        return flask.jsonify({'persons': rows})

    elif fmt == 'csv':
        utf8 = lambda v: unicode(v).encode('utf-8')
        fields = ['id', 'name'] + sorted(database.prop_defs.keys())
        header = dict((k, utf8(v)) for k, v in database.prop_defs.iteritems())
        header.update(id='id', name='Nume')

        csvfile = cStringIO.StringIO()
        csvwriter = csv.DictWriter(csvfile, fields)
        csvwriter.writerow(header)

        for person in query.all():
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
        for field_name in database.prop_defs:
            values = [v.strip() for v in form.getlist(field_name) if v.strip()]
            if values:
                new_content[field_name] = values

        if new_content != content:
            person.save_content_version(new_content, user)
            database.db.session.commit()
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


@webpages.route('/by_hpol_id/<int:hpol_id>')
def hpol_view(hpol_id):
    query = database.PersonMeta.query.filter_by(key='hpol_id', value=hpol_id)
    person = query.first_or_404().person
    return flask.redirect(flask.url_for('.person', person_id=person.id))


@webpages.route('/by_hpol_id/<int:hpol_id>/edit')
def hpol_edit(hpol_id):
    query = database.PersonMeta.query.filter_by(key='hpol_id', value=hpol_id)
    person = query.first_or_404().person
    return flask.redirect(flask.url_for('.edit', person_id=person.id))


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
    person_versions = person.versions
    person_versions.sort(key=lambda v: v.time, reverse=True)
    return {
        'person': person,
        'versions': person_versions,
    }


@webpages.route('/person/<int:person_id>/diff/<int:a_id>...<int:b_id>')
@with_template('diff.html')
def diff(person_id, a_id, b_id):
    person = database.Person.query.get_or_404(person_id)
    person_versions = (database.ContentVersion.query
                       .filter_by(person_id=person.id))
    a = person_versions.filter_by(id=a_id).first_or_404()
    b = person_versions.filter_by(id=b_id).first_or_404()
    def flat_version_items(version):
        items = []
        for key, values in version.get_content().items():
            for value in values:
                items.append((key, value))
        return items
    return {
        'person': person,
        'version_a': a,
        'version_b': b,
        'version_a_items': flat_version_items(a),
        'version_b_items': flat_version_items(b),
    }


@webpages.route('/')
@with_template('search.html')
def search():
    q = flask.request.args.get('q')
    if q is None:
        return {}
    persons = database.Person.objects_current()
    for part in q.split():
        persons = persons.filter(database.Person.name.like('%' + part + '%'))
    return {
        'q': q,
        'count': persons.count(),
        'persons': persons[:50],
    }


def init_app(app):
    app.register_blueprint(webpages)
    app.jinja_env.globals['known_names'] = database.prop_defs
    app.jinja_env.globals['office_label'] = office_defs

    local_timezone = timezone(app.config['TIMEZONE'])
    def filter_datetime(utc_value, fmt='%d %b, %H:%M'):
        return local_timezone.fromutc(utc_value).strftime(fmt)
    app.jinja_env.filters['datetime'] = filter_datetime
