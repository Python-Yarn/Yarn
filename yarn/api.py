import os
import sys
import getpass
import logging
import paramiko
from paramiko.ssh_exception import AuthenticationException
from contextlib import contextmanager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(funcName)s: %(message)s')


class Environment:
    host_string = ""
    _port = 22
    debug = True
    user = getpass.getuser()
    password = None
    working_directory = list()
    warn_only = True
    quiet = False
    _key = None
    passphrase = None
    _paramiko_key = None

    @property
    def connection_ref(self):
        return "{}@{}".format(self.user, self.host_string)

    @property
    def host_port(self):
        return self._port

    @host_port.setter
    def host_port(self, port):
        """ Checks to make sure the port is valid """
        if not isinstance(port, int):
            raise AttributeError("host_port must be an integer")
        elif 0 < port <= 65535:
            self._port = port
        else:
            raise AttributeError("host_port must be ain integer between 1 and 65535")

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key_file):
        """ Verify the key file exists. Will remove stored paramiko key. """
        if not os.path.exists(key_file):
            raise OSError("key file does not exist")
        self._key = key_file
        self._paramiko_key = None


env = Environment()


def ssh_connection(wrapped_function):
    logging.info("Creating SSH connection to: {}".format(env.connection_ref))

    def _wrapped(*args, **kwargs):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if env.key is not None and env._paramiko_key is None:
            env._paramiko_key = paramiko.RSAKey.from_private_key(open(env.key), password=env.passphrase)
        if not env.host_string:
            env.host_string = input("No hosts were specified.  Host IP/DNS Name: ")
        try:
            ssh.connect(env.host_string, env.host_port, username=env.user,
                        pkey=env._paramiko_key)
            return wrapped_function(*args, conn=ssh)
        except AuthenticationException:
            env.password = getpass.getpass("Password for {}: ".format(env.connection_ref))
            ssh.connect(env.host_string, env.host_port, username=env.user,
                        password=env.password)
            return wrapped_function(*args, conn=ssh)
        finally:
            logging.info("Closing connection: {}".format(env.connection_ref))
            ssh.close()

    return _wrapped


@contextmanager
def cd(path):
    env.working_directory.append(path)
    yield
    env.working_directory.pop()


@ssh_connection
def run(*args, **kwargs):
    if env.working_directory:
        command = "cd {} && {}".format(" && cd ".join(env.working_directory), args[0])
    else:
        command = args[0]
    ssh = kwargs.pop('conn')
    logger.debug("'{}' on '{}'".format(command, env.connection_ref))
    stdin, stdout, stderr = ssh.exec_command(command)
    stdout = "\n".join([a.strip() for a in stdout.readlines()])
    stderr = "\n".join(["ERROR: {}".format(a.strip()) for a in stderr.readlines()])
    if not stderr:
        return stdout
    if not env.warn_only:
        logging.warning(stderr)
        with cd(None):
            logging.warning("ENV_DEBUG: '{}'".format(run("env")))
        sys.exit(1)

    return False


@ssh_connection
def put(*args, **kwargs):
    ssh = kwargs['conn']
    local_path = args[0]
    remote_path = args[1]
    logger.debug("Uploading {} to {}:{}".format(local_path, env.connection_ref, remote_path))
    ftp = ssh.open_sftp()
    ftp.put(local_path, remote_path)
    ftp.close()


@ssh_connection
def get(*args, **kwargs):
    ssh = kwargs['conn']
    remote_path = args[0]
    local_path = args[1] if len(args) == 2 else os.path.join(os.path.abspath("."), os.path.split(remote_path)[-1])
    logger.debug("Downloading {}:{}.  Placing it: {}".format(env.connection_ref, remote_path, local_path))
    ftp = ssh.open_sftp()
    ftp.get(remote_path, local_path)
    ftp.close()
