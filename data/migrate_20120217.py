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

def remove_address():
    import database
    invalid_address_persons = [276, 75, 334, 166, 332, 100]

    for person_id in invalid_address_persons:
        person = database.Person.query.get(person_id)
        content = person.get_content()
        del content['address']
        person.save_content_version(content, None)
        database.db.session.add(person)
    database.db.session.commit()

def fix_addresses():
    import database

    persons_with_addresses = [
        (257, u"Bd. Tineretului, Nr. 105 -115, Bl. S1, Sc. A, "
              u"parter, Oltenita, Judetul Calarasi"),
        (252, u"Str. Calea lui Traian, Nr 171, Bl. 7, Rîmnicu Vîlcea, "
              u"Judetul Vîlcea"),
        (296, u"Str. Fântânelor, parter, Pucioasa, Judetul Dâmbovita"),
        (242, u"Str. Regina Elisabeta Nr. 63,  Sc.C, et.6, ap.23,  "
              u"Sector 5, Bucuresti"),
        (80,  u"Bd. 1 Mai, Bl. 25, Sc. B, parter, Husi, Judetul Vaslui"),
        (203, u"Bd. Lapusneanu, Nr. 71, Bl. LV1, parter, Constanta, "
              u"Judetul Constanta"),
        (145, u"Str. Saturn, Nr. 32, Corp A, Et. 1, camera 2, Galati, "
              u"Judetul Galati"),
        (292, u"Str. Tudor Musetescu, Bl.V2B, mezanin, Mioveni, "
              u"Judetul Arges"),
        (107, u"Str. Mihai Eminescu, Bl. 2, Ap. 41, Roman, Judetul Neamt"),
        (285, u"Str. Jupiter, Nr.7, Constanta, Judetul Constanta"),
        (18,  u"Str. Republicii nr. 27, Fagaras , Jud Brasov"),
        (143, u"Floresti, Stoienesti, Sediul Primariei, Judetul Giurgiu"),
    ]

    for (person_id, new_address) in persons_with_addresses:
        person = database.Person.query.get(person_id)
        content = person.get_content()
        content['address'] = [new_address]
        person.save_content_version(content, None)
        database.db.session.add(person)
    database.db.session.commit()
