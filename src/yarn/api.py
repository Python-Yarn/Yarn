import os
import sys
import getpass
import logging
import paramiko
from contextlib import contextmanager

# TODO: Get the setup.py for runner started
# TODO: Work up the list of context managers
# TODO: Setup command line arguments for the 'knit'

# ATTRIBUTION: I followed the tutorial I found at: http://jessenoller.com/2009/02/05/ssh-programming-with-paramiko-completely-different/

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(funcName)s: %(message)s')


class Environment:
    host_string = None
    debug = True
    user = None
    password = None
    working_directory = None
    warn_only = True
    quiet = False

    @property
    def connection_ref(self):
        return "{}@{}".format(self.user, self.host_string)

env = Environment()


def ssh_connection(wrapped_function):
    logging.info("Creating SSH connection to: {}".format(env.connection_ref))
    def _wrapped(*args, **kwargs):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(env.host_string, username=env.user, password=env.password)
            return wrapped_function(*args, conn=ssh)
        finally:
            logging.info("Closing connection: {}".format(env.connection_ref))
            ssh.close()
    return _wrapped


@contextmanager
def cd(path):
    env.working_directory = path
    yield
    env.working_directory = None


@ssh_connection
def run(*args, **kwargs):
    if env.working_directory:
        command = "cd {} && {}".format(env.working_directory, args[0])
    else:
        command = args[0]
    ssh = kwargs.pop('conn')
    logger.debug("RUNNING '{}' on '{}'".format(command, env.host_string))
    stdin, stdout, stderr = ssh.exec_command(command)
    stdout = "\n".join([a.strip() for a in stdout.readlines()])
    stderr = "\n".join(["ERROR: {}".format(a.strip()) for a in stderr.readlines()])
    if not stderr:
        return stdout
    if not env.warn_only:
        logging.warn(stderr)
        with cd(None):
            logging.warn("ENV_DEBUG: '{}'".format(run("env")))
        sys.exit(1)

    return False


@ssh_connection
def put(*args, **kwargs):
    ssh = kwargs['conn']
    local_path = args[0]
    remote_path = args[1]
    logger.debug("Putting {} on {}.  Placing it: {}".format(local_path, env.connection_ref, remote_path))
    ftp = ssh.open_sftp()
    ftp.put(local_path, remote_path)
    ftp.close()


@ssh_connection
def get(*args, **kwargs):
    ssh = kwargs['conn']
    remote_path = args[0]
    local_path = args[1] if len(args) == 2 else os.path.join(os.path.abspath("."), os.path.split(remote_path)[-1])
    logger.debug("Getting {} from {}.  Placing it: {}".format(remote_path, env.connection_ref, local_path))
    ftp = ssh.open_sftp()
    ftp.get(remote_path, local_path)
    ftp.close()
