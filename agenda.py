#!/usr/bin/env python

import os.path
import logging
import flask
import database
import webpages
import auth


default_config = {
    'DEBUG': False,
    'TIMEZONE': 'Europe/Bucharest',
}


def setup_mail_on_error(app):
    ADMINS = ['yourname@example.com']
    mail_on_error = app.config.get('MAIL_ON_ERROR', [])
    if not mail_on_error:
        return
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler(app.config.get('MAIL_HOST', '127.0.0.1'),
                               app.config['MAIL_FROM'],
                               mail_on_error,
                               "Error in Agenda Politicieni")
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


def create_app():
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///%s/agenda.db' % app.instance_path)
    app.config.update(default_config)
    app.config.from_pyfile('settings.py', silent=True)
    webpages.init_app(app)
    database.db.init_app(app)
    auth.init_app(app)
    setup_mail_on_error(app)
    return app


def main():
    app = create_app()

    log_fmt = logging.Formatter("[%(asctime)s] %(module)s "
                                "%(levelname)s %(message)s")

    suggestion_log_path = os.path.join(app.instance_path, 'database.log')
    suggestion_handler = logging.FileHandler(suggestion_log_path)
    suggestion_handler.setFormatter(log_fmt)
    database.log.addHandler(suggestion_handler)

    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    else:
        cmd = 'runserver'

    if cmd == 'runserver':
        app.run(debug=True)
    elif cmd == 'shell':
        from code import interact
        with app.test_request_context():
            interact(local={'app': app})
    elif cmd == 'fastcgi':
        from flup.server.fcgi import WSGIServer
        error_log_path = os.path.join(app.instance_path, 'error.log')
        error_handler = logging.FileHandler(error_log_path)
        error_handler.setFormatter(log_fmt)
        error_handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(error_handler)
        sock_path = os.path.join(app.instance_path, 'fcgi.sock')
        server = WSGIServer(app, bindAddress=sock_path, umask=0)
        server.run()
    elif cmd == 'update_identities':
        import sync
        with app.test_request_context():
            sync.update_identities()


if __name__ == '__main__':
    main()
