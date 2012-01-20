import flask
import database
import webpages


default_config = {
    'DEBUG': True,
}


def create_app():
    app = flask.Flask(__name__, instance_relative_config=True)
    app.register_blueprint(webpages.webpages)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///%s/agenda.db' % app.instance_path)
    app.config.update(default_config)
    app.config.from_pyfile('application.cfg', silent=True)
    database.db.init_app(app)
    return app


def main():
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    else:
        cmd = 'runserver'

    app = create_app()
    if cmd == 'runserver':
        app.run()
    elif cmd == 'shell':
        from code import interact
        with app.test_request_context():
            interact(local={'app': app})


if __name__ == '__main__':
    main()
