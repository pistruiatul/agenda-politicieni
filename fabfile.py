from fabric.api import env
from fabric.api import local, run, cd
from fabric.contrib.files import exists


REMOTE_REPO = '/var/local/agenda'


def get_git_remote():
    return env['host_string']

try: from local_fabfile import *
except: pass


paths = {
    'repo': REMOTE_REPO,
    'var': REMOTE_REPO + '/instance',
    'sandbox': REMOTE_REPO + '/sandbox',
}


def deploy():
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
    run("/sbin/start-stop-daemon --start -b "
        "--pidfile %(var)s/fcgi.pid --make-pidfile "
        "--exec %(sandbox)s/bin/python %(repo)s/agenda.py fastcgi"
        % paths)
