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
# I really, really wish I could change the format of this to have my
# connection_string in it, but I am unwilling to break the logger to do it.
logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(funcName)s: %(message)s')


# Here is the global environment for the system.  Pretty much everyone will
# use this.
env = Environment()

# Starting the work for sudo per GitHub Issue #20
def sudo(command):
    @ssh_connection
    def sudo_command(*args, **kwargs):
        conn = kwargs['conn']
        stdin, stdout, stderr = conn.exec_command(kwargs['command'], get_pty=True)
        stdin.flush()
        if not env.password:
            env.password = getpass("Password for {}: ".format(env.connection_string))
        stdin.write('{}\n'.format(env.password))
        stdin.flush()
        # print the results
        stdout = [a.decode('utf-8').strip() for a in stdout.read().splitlines()]
        stderr = ["ERROR: [{}] '{}'".format(env.connection_string, a.decode('utf-8').strip()) for a in stderr.read().splitlines()]
        if not stderr:
            if not env.quiet:
                for a in stdout:
                    logging.info("[{}] - {}".format(env.connection_string, a))
            ret = "\n".join(stdout)
            return ret
        if not env.quiet:
            logging.warning("\n".join(stderr))
            logging.warning("ENV_DEBUG: '{}'".format(run("env")))
        if not env.warn_only:
            sys.exit(1)
    return sudo_command(command='sudo -Si {}'.format(command))

# The joys of running in parallel
def parallel(wrapped_function):
    def _wrapped(*args, **kwargs):
        if env.run_parallel:
            task = multiprocessing.Process(target=wrapped_function, args=args, kwargs=kwargs)
            env.parallel_tasks.append(task)
            task.start()
        else:
            return wrapped_function(*args, **kwargs)
    return _wrapped


# This might be somewhat important.
def ssh_connection(wrapped_function):
    logging.info("Creating SSH connection to: {}".format(env.connection_string))

    def _wrapped(*args, **kwargs):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if env.key is not None and env._paramiko_key is None:
            env._paramiko_key = paramiko.RSAKey.from_private_key(open(env.key), password=env.passphrase)
        if not env.host_string:
            env.host_string = input("No hosts were specified.  Host IP/DNS Name: ")
        try:
            # Here is where the conncetion is setup.
            ssh.connect(env.host_string, env.host_port, username=env.user,
                        pkey=env._paramiko_key)
            return wrapped_function(*args, conn=ssh, **kwargs)
        except AuthenticationException:
            # If there is a problem with the pervious attempt (no/bad password)
            # Here is where we will query for it and try again.
            env.password = getpass("Password for {}: ".format(env.connection_string))
            ssh.connect(env.host_string, env.host_port, username=env.user,
                        password=env.password)
            return wrapped_function(*args, conn=ssh, **kwargs)
        finally:
            # Gotta love the cleanup associated with the finally call in Python.
            logging.info("Closing connection: {}".format(env.connection_string))
            ssh.close()

    return _wrapped


@contextmanager
def cd(path):
    # Yes, I know it's simplistic.  But if it's stupid and it works, then it
    # ain't stupid.
    env.working_directory.append(path)
    yield
    env.working_directory.pop()


# The meat and potatoes of the entire system.
def run(command):
    @ssh_connection
    def run_command(*args, **kwargs):
        command = kwargs['command']
        if env.working_directory:
            command = "cd {} && {}".format(" && cd ".join(env.working_directory), command)
        ssh = kwargs.pop('conn')
        if not env.quiet:
            logger.debug("'{}' on '{}'".format(command, env.connection_string))
        stdin, stdout, stderr = ssh.exec_command(command)
        # I will defeat the horrible setup for logging I have implemented.
        # Give me time.
        stdout = [a.decode('utf-8').strip() for a in stdout.read().splitlines()]
        stderr = ["ERROR: [{}] '{}'".format(env.connection_string, a.decode('utf-8').strip()) for a in stderr.read().splitlines()]
        if not stderr:
            if not env.quiet:
                for a in stdout:
                    logging.info("[{}] - {}".format(env.connection_string, a))
            return "\n".join(stdout)
        if not env.quiet:
            logging.warning("\n".join(stderr))
            logging.warning("ENV_DEBUG: '{}'".format(run("env")))
        if not env.warn_only:
            sys.exit(1)

        return False
    return run_command(command=command)


# Putting a file is handy.  I may decide to check and see if there is already
# an identical file in place so that we don't copy the same file over and over
# again.  Hmmmm....
def put(local_path, remote_path):
    @ssh_connection
    def put_file(*args, **kwargs):
        ssh = kwargs['conn']
        local_path = kwargs['local_path']
        remote_path = kwargs['remote_path']
        logger.debug("Uploading {} to {}:{}".format(
                    local_path, env.connection_string, remote_path))
        ftp = ssh.open_sftp()
        ftp.put(local_path, remote_path)
        ftp.close()
    return put_file(local_path=local_path, remote_path=remote_path)


# Getting a file is nifty.
def get(remote_path, local_path=None):
    @ssh_connection
    def get_file(*args, **kwargs):
        ssh = kwargs['conn']
        remote_path = kwargs['remote_path']
        local_path = kwargs['local_path']
        logger.debug("Downloading {}:{}.  Placing it: {}".format(
                        env.connection_string, remote_path, local_path))
        ftp = ssh.open_sftp()
        ftp.get(remote_path, local_path)
        ftp.close()
    if not local_path:
        local_path = os.path.join(local_path, os.path.split(remote_path)[-1])
    return get_file(remote_path=remote_path, local_path=local_path)
