# encoding: utf-8
from webpages import webpages, with_template, office_defs
import flatland, flatland.out.markup
import flask
import database


SearchSchema = flatland.Dict.of(
    flatland.Enum.named('office') \
                 .valued(*sorted(office_defs.keys())) \
                 .using(optional=True) \
                 .with_properties(label=u"Funcție", value_labels=office_defs),
)


@webpages.route('/')
@with_template('search.html')
def search():
    search_schema = SearchSchema.from_flat(flask.request.args.to_dict())
    form_gen = flatland.out.markup.Generator()
    form_gen.begin(auto_domid=True, auto_for=True)
    persons = database.Person.query
    office_value = search_schema['office'].value
    if office_value:
        persons = persons.filter(
            database.Person.meta.any(
                database.PersonMeta.key == 'office'
            )
        ).filter(
            database.Person.meta.any(
                database.PersonMeta.value == office_value
            )
        )
    return {
        'persons': persons.order_by('name').all(),
        'search_schema': search_schema,
        'form_gen': form_gen,
    }
