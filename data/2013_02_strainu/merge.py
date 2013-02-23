# encoding: utf-8
import csv
import codecs
import re
from collections import defaultdict
from path import path
import simplejson as json


ro_to_ascii = {
    u'ș': u's',
    u'ş': u's',
    u'ț': u't',
    u'ţ': u't',
    u'ă': u'a',
    u'î': u'i',
    u'â': u'a',
    u'Ș': u'S',
    u'Ş': u'S',
    u'Ț': u'T',
    u'Ţ': u'T',
    u'Ă': u'A',
    u'Î': u'I',
    u'Â': u'A',
}


def fix_whitespace(name):
    name = re.sub(r'\s*\-\s*', '-', name, re.UNICODE)
    name = re.sub(r'\.\s*', '. ', name, re.UNICODE)
    return name.strip()


def strip_name_initials(name):
    return re.sub(r'\b\w{1,2}\b\.?\s*', ' ', name, re.UNICODE)


def no_diacritics(name):
    for k, v in ro_to_ascii.items():
        name = name.replace(k, v)
    return name


def normalize(name):
    name = no_diacritics(name)
    name = fix_whitespace(name)
    name = strip_name_initials(name)
    name = name.lower()
    name = name.replace(u'-', u' ')
    return tuple(sorted(name.split()))


def switch_to_first_last(name):
    bits = name.split()
    return ' '.join(bits[1:] + bits[:1])


def merge():
    with path('current.json').open() as f:
        current_json = json.load(f)['persons']

    with path('pcj.csv').open() as f:
        pcj_csv = [dict(zip(['id', 'name', 'party', 'year'],
                            line.decode('utf-8').split(',')))
                   for line in f]

    with path('primari.csv').open() as f:
        primari_csv = [dict(zip(['name', 'party', 'year', '_1'],
                                line.decode('utf-8').split(',')))
                       for line in f]

    current_name_count = defaultdict(int)
    current_name_agenda_id = dict()
    new_name_count = defaultdict(list)
    despresate_id_map = defaultdict(list)

    for person in current_json:
        norm_name = normalize(person['name'])
        current_name_count[norm_name] += 1
        if norm_name not in current_name_agenda_id:
            current_name_agenda_id[norm_name] = person['id']

    for n, person in enumerate(pcj_csv, 1):
        norm_name = normalize(person['name'])
        new_name_count[norm_name].append(person['name'])
        despresate_id_map[norm_name].append('pcj:%d' % n)

    for n, person in enumerate(primari_csv, 1):
        norm_name = normalize(person['name'])
        new_name_count[norm_name].append(person['name'])
        despresate_id_map[norm_name].append('primari:%d' % n)

    #print len(current_json) + len(pcj_csv) + len(primari_csv)
    #print len(name_count)
    #print len(set(new_name_count) - set(current_name_count))
    #for norm_name in (set(new_name_count) & set(current_name_count)):
    #    print norm_name

    with path('mapping.csv').open('wb') as f:
        mapping_csv = csv.writer(f)
        mapping_csv.writerow(['despresate_id', 'agenda_id'])
        for name, orig in new_name_count.iteritems():
            if name in current_name_count:
                agenda_id = current_name_agenda_id[name]
                for despresate_id in despresate_id_map[name]:
                    mapping_csv.writerow([despresate_id, agenda_id])
            else:
                new_name = switch_to_first_last(fix_whitespace(
                    strip_name_initials(no_diacritics(orig[0]))))
                print new_name


if __name__ == '__main__':
    merge()
