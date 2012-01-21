import os.path
import flask
import database
import webpages
import auth


default_config = {
    'DEBUG': False,
}


def create_app():
    app = flask.Flask(__name__, instance_relative_config=True)
    webpages.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///%s/agenda.db' % app.instance_path)
    app.config.update(default_config)
    app.config.from_pyfile('settings.py', silent=True)
    database.db.init_app(app)
    auth.init_app(app)
    return app


def main():
    app = create_app()

    import logging
    suggestion_log_path = os.path.join(app.instance_path, 'suggestions.log')
    suggestion_handler = logging.FileHandler(suggestion_log_path)
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
        error_handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(error_handler)
        sock_path = os.path.join(app.instance_path, 'fcgi.sock')
        server = WSGIServer(app, bindAddress=sock_path, umask=0)
        server.run()


if __name__ == '__main__':
    main()
