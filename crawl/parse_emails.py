import os.path
import re
import simplejson as json


mail_pattern = re.compile(r'"mailto:(?P<email>[^"]*)"')
name_pattern = re.compile(r'<td class="cale2".*?&gt; (?P<name>[^;]+?)</td>')
phone_pattern = re.compile(r'<li>(?P<phone>Telefon[^<]*)')


def extract_emails(html_dir):
    for name in os.listdir(html_dir):
        with open(os.path.join(html_dir, name), 'rb') as f:
            html = f.read()

        mail_match = mail_pattern.search(html)
        assert mail_match is not None
        email = mail_match.group('email')

        name_match = name_pattern.search(html)
        assert name_match is not None
        name = name_match.group('name')

        #phone_match = phone_pattern.search(html)
        #if phone_match is not None:
        #    print phone_match.group('phone')

        yield {
            'email': email,
            'name': name.decode('latin2'),
        }


if __name__ == '__main__':
    import sys
    print json.dumps(list(extract_emails(sys.argv[1])), indent=2)
