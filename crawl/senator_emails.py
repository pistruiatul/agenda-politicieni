import csv
import re
from collections import defaultdict


mail_pattern = re.compile(r'[\w\.\-+]+@[\w\.\-+]+')


def extract_mails(text):
    offset = 0
    while True:
        mail_match = mail_pattern.search(text, offset)
        if mail_match is None:
            break
        yield mail_match.group(0)
        offset = mail_match.end()


blacklist = [
    'pnl@senat.ro',
    'udmr@senat.ro',
    'arad@psd.ro',
    'pnl.bihor@pnl.ro',
    'pnl.brasov@pnl.ro',
    'presedinte@pnl.ro',
]


def filter_mails(mails):
    out = []
    for mail in mails:
        if mail in out:
            continue
        if mail in blacklist:
            continue
        out.append(mail)
    return out


def parse_csv(f):
    raw_mails = defaultdict(list)
    table = csv.DictReader(f)
    for row in table:
        text = row['Text']
        raw_mails[row['Senator']].extend(extract_mails(text))

    for name in sorted(raw_mails.keys()):
        yield {
            'name': name,
            'emails': filter_mails(raw_mails[name]),
        }


def count_mails(people):
    count = defaultdict(int)
    for person in people:
        for m in person['emails']:
            count[m] += 1
    for line in sorted([(count[m], m) for m in count]):
        print line


if __name__ == '__main__':
    import sys
    import simplejson as json
    with open(sys.argv[1], 'rb') as f:
        people = list(parse_csv(f))
        people.sort(key=lambda p: p['name'])
        #count_mails(people)
        print json.dumps(people, indent=2)
