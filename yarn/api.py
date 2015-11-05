import os
import sys
import logging
import paramiko
import multiprocessing
if sys.version_info.major == 2:
    from environment import Environment
else:
    from yarn.environment import Environment
from getpass import getpass
from contextlib import contextmanager
from paramiko.ssh_exception import AuthenticationException

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(funcName)s: %(message)s')


env = Environment()


def parallel(wrapped_function):
    def _wrapped(*args, **kwargs):
        if env.run_parallel:
            task = multiprocessing.Process(target=wrapped_function, args=args, kwargs=kwargs)
            env.parallel_tasks.append(task)
            task.start()
        else:
            return wrapped_function(*args, **kwargs)
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
            return wrapped_function(*args, conn=ssh, **kwargs)
        except AuthenticationException:
            env.password = getpass("Password for {}: ".format(env.connection_ref))
            ssh.connect(env.host_string, env.host_port, username=env.user,
                        password=env.password)
            return wrapped_function(*args, conn=ssh, **kwargs)
        finally:
            logging.info("Closing connection: {}".format(env.connection_ref))
            ssh.close()

    return _wrapped


@contextmanager
def cd(path):
    env.working_directory.append(path)
    yield
    env.working_directory.pop()


def run(command):
    @ssh_connection
    def run_command(*args, **kwargs):
        command = kwargs['command']
        if env.working_directory:
            command = "cd {} && {}".format(" && cd ".join(env.working_directory), command)
        ssh = kwargs.pop('conn')
        if not env.quiet:
            logger.debug("'{}' on '{}'".format(command, env.connection_ref))
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout = [a.decode('utf-8').strip() for a in stdout.read().splitlines()]
        stderr = ["ERROR: [{}] '{}'".format(env.connection_ref, a.decode('utf-8').strip()) for a in stderr.read().splitlines()]
        if not stderr:
            if not env.quiet:
                for a in stdout:
                    logging.info("[{}] - {}".format(env.connection_ref, a))
            return "\n".join(stdout)
        if not env.quiet:
            logging.warning("\n".join(stderr))
            logging.warning("ENV_DEBUG: '{}'".format(run("env")))
        if not env.warn_only:
            sys.exit(1)

        return False
    return run_command(command=command)


def put(local_path, remote_path):
    @ssh_connection
    def put_file(*args, **kwargs):
        ssh = kwargs['conn']
        local_path = kwargs['local_path']
        remote_path = kwargs['remote_path']
        logger.debug("Uploading {} to {}:{}".format(local_path, env.connection_ref, remote_path))
        ftp = ssh.open_sftp()
        ftp.put(local_path, remote_path)
        ftp.close()
    return put_file(local_path=local_path, remote_path=remote_path)


def get(remote_path, local_path=None):
    @ssh_connection
    def get_file(*args, **kwargs):
        ssh = kwargs['conn']
        remote_path = kwargs['remote_path']
        local_path = kwargs['local_path']
        logger.debug("Downloading {}:{}.  Placing it: {}".format(env.connection_ref, remote_path, local_path))
        ftp = ssh.open_sftp()
        ftp.get(remote_path, local_path)
        ftp.close()
    if not local_path:
        local_path = os.path.join(local_path, os.path.split(remote_path)[-1])
    return get_file(remote_path = remote_path, local_path = local_path)
