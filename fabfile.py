from fabric.api import env
from fabric.api import local, run, cd
from fabric.contrib.files import exists


REMOTE_REPO = '/var/local/agenda'


def get_git_remote():
    return env['host_string']

try: from local_fabfile import *
except: pass


def deploy():
    if not exists(REMOTE_REPO):
        run("git init '%s'" % REMOTE_REPO)

    git_remote = "%s:%s" % (get_git_remote(), REMOTE_REPO)
    local("git push -f '%s' master:incoming" % git_remote)
    with cd(REMOTE_REPO):
        run("git reset incoming --hard")

    sandbox = REMOTE_REPO + '/sandbox'
    if not exists(sandbox):
        run("virtualenv --no-site-packages '%s'" % sandbox)
        run("echo '*' > '%s/.gitignore'" % sandbox)

    with cd(REMOTE_REPO):
        run("sandbox/bin/pip install -r requirements.txt")

    instance = REMOTE_REPO + '/instance'
    if not exists(instance):
        run("mkdir -p '%s'" % instance)
