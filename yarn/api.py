import os
import sys
import getpass
import logging
import paramiko
import multiprocessing
if sys.version_info.major == 2:
    from environment import Environment
else:
    from yarn.environment import Environment
from paramiko.ssh_exception import AuthenticationException
from contextlib import contextmanager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(funcName)s: %(message)s')


env = Environment()


def parallel(wrapped_function):
    def _wrapped(*args, **kwargs):
        task = multiprocessing.Process(target=wrapped_function, args=args, kwargs=kwargs)
        env.parallel_jobs.append(task)
        task.start()
    return _wrapped


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


