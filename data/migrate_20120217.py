# encoding: utf-8

def remove_persons():
    import database
    persons_to_remove = [128, 302, 302, 158, 16, 225, 339,
                         137, 67, 210, 264, 186, 394, 368]

    for person_id in persons_to_remove:
        meta_removed = database.PersonMeta(person_id=person_id,
                                           key='removed', value='true')
        database.db.session.add(meta_removed)
    database.db.session.commit()

def nationally_elected():
    import database
    national_persons = [138, 19, 71, 37, 87, 261, 285, 282, 12,
                        50, 52, 78, 89, 144, 166, 173, 242]

    for person_id in national_persons:
        person = database.Person.query.get(person_id)
        meta = person.meta.filter_by(key='college').first()
        if meta is None:
            meta = database.PersonMeta(person=person, key='college')
        meta.value = u"Ales la nivel național"
        database.db.session.add(meta)
    database.db.session.commit()
