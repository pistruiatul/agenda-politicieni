import flask


webpages = flask.Blueprint('webpages', __name__)


@webpages.route('/')
def home():
    return "hello world!"
