import flask
import database


webpages = flask.Blueprint('webpages', __name__)


@webpages.route('/')
def home():
    return flask.render_template('homepage.html',
                                 persons=database.get_persons())


@webpages.route('/download.json')
def download():
    return flask.jsonify(database.get_persons())


@webpages.route('/person/<int:person_id>/suggest', methods=['GET', 'POST'])
def suggest(person_id):
    return flask.render_template('suggest.html',
            person=database.Person.query.get_or_404(person_id))


def init_app(app):
    app.register_blueprint(webpages)
    app.jinja_env.globals['known_names'] = {
        'email': "Email",
        'phone': "Telefon",
    }
