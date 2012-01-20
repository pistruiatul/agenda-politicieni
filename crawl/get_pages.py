import os.path
import subprocess


URL_TMPL = 'http://www.cdep.ro/pls/parlam/structura.mp?idm=%d&cam=2&leg=2008'

def bulk_download(html_dir):
    for c in range(100, 340):
        html_path = os.path.join(html_dir, 'parlamentar_%d.html' % c)
        if os.path.isfile(html_path):
            continue
        url = URL_TMPL % (c,)
        print url
        data = subprocess.check_output(['curl', url])
        with open(html_path, 'wb') as f:
            f.write(data)


if __name__ == '__main__':
    import sys
    bulk_download(sys.argv[1])
