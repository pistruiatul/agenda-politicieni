import os.path
import re
import simplejson as json


mail_pattern = re.compile(r'"mailto:(?P<email>[^"]*)"')
name_pattern = re.compile(r'<td class="cale2".*?&gt; (?P<name>[^;]+?)</td>')
phone_pattern = re.compile(r'<li>(?P<phone>Telefon[^<]*)')


blacklist = ['webmaster@cdep.ro']


def filter_mails(mails):
    out = []
    for mail in mails:
        if mail in out:
            continue
        if mail in blacklist:
            continue
        out.append(mail)
    return out


def extract_emails(html_dir):
    for name in os.listdir(html_dir):
        if not name.startswith('parlamentar_'):
            continue

        with open(os.path.join(html_dir, name), 'rb') as f:
            html = f.read()

        offset = 0
        emails = []
        while True:
            mail_match = mail_pattern.search(html, offset)
            if mail_match is None:
                break
            email = mail_match.group('email')
            emails.append(email)
            offset = mail_match.end()

        name_match = name_pattern.search(html)
        assert name_match is not None
        name = name_match.group('name')

        #phone_match = phone_pattern.search(html)
        #if phone_match is not None:
        #    print phone_match.group('phone')

        yield {
            'emails': filter_mails(emails),
            'name': name.decode('latin2'),
        }


if __name__ == '__main__':
    import sys
    print json.dumps(list(extract_emails(sys.argv[1])), indent=2)
