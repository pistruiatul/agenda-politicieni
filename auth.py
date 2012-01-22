# encoding: utf-8
import os.path
from functools import wraps
import flask
from flaskext.openid import OpenID, COMMON_PROVIDERS
import database

oid = OpenID()

auth = flask.Blueprint('auth', __name__)


def lookup_current_user():
    flask.g.user = None
    if 'openid_url' in flask.session:
        flask.g.user = database.get_user(flask.session['openid_url'])


@auth.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if flask.g.user is not None:
        return flask.redirect(oid.get_next_url())

    return oid.try_login(COMMON_PROVIDERS['google'],
                         ask_for=['email', 'fullname', 'nickname'])


@oid.after_login
def create_or_login(resp):
    flask.session['openid_url'] = resp.identity_url
    flask.g.user = database.get_update_user(
        openid_url=resp.identity_url,
        name=resp.fullname or resp.nickname,
        email=resp.email)
    flask.flash(u"Autentificare cu succes - " + flask.g.user.name)
    return flask.redirect(oid.get_next_url())


@auth.route('/logout')
def logout():
    flask.session.pop('openid_url', None)
    flask.flash(u"Ați fost dezautentificat.")
    return flask.redirect(oid.get_next_url())


def is_admin(user):
    if user is None:
        return False
    admins = flask.current_app.config.get('ADMIN_OPENIDS', [])
    return (user.openid_url in admins)


def require_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_admin(flask.g.user):
            msg = u"Pagină rezervată administratorilor"
            return flask.render_template('message.html', errors=[msg])

        return func(*args, **kwargs)

    return wrapper


def init_app(app):
    app.register_blueprint(auth)
    oid.init_app(app)
    oid.fs_store_path = os.path.join(app.instance_path, 'openid-store')
    app.before_request(lookup_current_user)
