def remove_persons():
    import database
    persons_to_remove = [128, 302, 302, 158, 16, 225, 339,
                         137, 67, 210, 264, 186, 394, 368]

    for person_id in persons_to_remove:
        meta_removed = database.PersonMeta(person_id=person_id,
                                           key='removed', value='true')
        database.db.session.add(meta_removed)
    database.db.session.commit()
