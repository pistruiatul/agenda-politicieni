import database
from webpages import hartapoliticii_data

def set_meta(p, key, value):
  m = database.PersonMeta(person=p, key=key, value=value)
  database.db.session.add(m)
  database.log.info('Metadata update for person id=%d key=%r value=%r',
    p.id, key, value)

def initial_meta():
    for p in database.Person.query[:339]:
      set_meta(p, 'office', 'deputy')

    for p in database.Person.query[339:]:
      set_meta(p, 'office', 'senator')

    for p_id, hp_row in hartapoliticii_data.iteritems():
      value = hp_row['college_name']
      set_meta(database.Person.query.get(p_id), 'college', value)

    database.db.session.commit()
