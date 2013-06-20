from webpages import webpages, with_template
import database


@webpages.route('/')
@with_template('search.html')
def search():
    persons = database.Person.objects_current()
    return {
        'persons': persons.order_by('name').all(),
    }
