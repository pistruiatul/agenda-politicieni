import os.path
from fabric.api import *
from fabric.contrib.files import exists
from fabric.operations import get
from fabric import colors


REMOTE_REPO = '/var/local/agenda'
LOCAL_REPO = os.path.dirname(__file__)


def get_git_remote():
    return env['host_string']

try: from local_fabfile import *
except: pass


paths = {
    'repo': REMOTE_REPO,
    'var': REMOTE_REPO + '/instance',
    'sandbox': REMOTE_REPO + '/sandbox',
}


def install():
    if not exists(REMOTE_REPO):
        run("git init '%s'" % REMOTE_REPO)

    git_remote = "%s:%s" % (get_git_remote(), REMOTE_REPO)
    local("git push -f '%s' master:incoming" % git_remote)
    with cd(REMOTE_REPO):
        run("git reset incoming --hard")

    if not exists(paths['sandbox']):
        run("virtualenv --no-site-packages '%(sandbox)s'" % paths)
        run("echo '*' > '%(sandbox)s/.gitignore'" % paths)

    run("%(sandbox)s/bin/pip install -r %(repo)s/requirements.txt" % paths)

    instance = REMOTE_REPO + '/instance'
    if not exists(instance):
        run("mkdir -p '%s'" % instance)


def start():
    run("/sbin/start-stop-daemon --start --background "
        "--pidfile %(var)s/fcgi.pid --make-pidfile "
        "--exec %(sandbox)s/bin/python %(repo)s/agenda.py fastcgi"
        % paths, pty=False)


def stop():
    run("/sbin/start-stop-daemon --stop --retry 3 --oknodo "
        "--pidfile %(var)s/fcgi.pid" % paths)


def restart():
    stop()
    start()


def deploy():
    install()
    restart()


def backup():
    from datetime import datetime
    for name in ['agenda.db', 'database.log']:
        filename = datetime.now().strftime('%Y-%m-%d-%H-%M') + '-' + name
        local_path = os.path.join(LOCAL_REPO, 'backup', filename)
        get('%(var)s/%(name)s' % dict(paths, name=name), local_path)
        local("gzip '%s'" % local_path)
    print colors.green('Backup successful')
