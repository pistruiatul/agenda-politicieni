# encoding: utf-8
import sys
import simplejson as json
import re


def normalize_ro(name):
    for pair in [u'şș', u'ţț', u'ŞȘ', u'ŢȚ']:
        name = name.replace(pair[0], pair[1])
    return name


def normalize_name(name, invert=False):
    name = name.replace(u' \u2013 ', ' ')
    name = re.sub(r'\s(\w+)\.\s', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()

    if invert:
        first, last = name.rsplit(' ', 1)
        name = last + ' ' + first

    name = normalize_ro(name).replace('-', ' ')

    name = re.sub(r'\s+', ' ', name).strip()
    assert re.match(r'^(\w+ )*\w+$', name, re.UNICODE) is not None, repr(name)
    return name.lower()


def match(hp_file, ap_file, out_file):
    ap_by_name = {}
    ap_orig_name = {}
    for ap_person in json.load(ap_file)['persons']:
        ap_orig_name[ap_person['id']] = normalize_ro(ap_person['name'])
        name = normalize_name(ap_person['name'], invert=True)
        assert name not in ap_by_name
        ap_by_name[name] = ap_person['id']

    mapping = {}
    for hp_person in json.load(hp_file):
        name = hp_person['name']
        try:
            name = normalize_name(name)
        except:
            print 'fault in HP, id=%d' % int(hp_person['id'])
            raise
        ap_id = ap_by_name.pop(name, None)
        if ap_id is not None:
            mapping[ap_id] = {
                'ap_name': ap_orig_name[ap_id],
                'id_harta_politicii': hp_person['id'],
                'college_name': hp_person['college_name'],
            }


    json.dump(mapping, out_file, indent=2)

    from pprint import pformat
    print>>sys.stderr, pformat(ap_by_name)


if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as hp_file:
        with open(sys.argv[2], 'rb') as ap_file:
            match(hp_file, ap_file, sys.stdout)
