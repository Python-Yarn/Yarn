import os
from getpass import getuser

class Environment(object):

    # This is the list which contains the processes for parallel execution
    parallel_tasks = list()

    # This is only in place to be overridden by the yarn command line.  Normal
    # functions which are tagged with @parallel will automatically execute
    # in parallel.
    run_parallel = True

    # The host to which we are connecting to execute tasks
    host_string = ""

    # The port to use for the connection.
    _port = 22

    # Debugging flag
    debug = True

    # The username to use for the connection authentication.
    _user = getuser()

    # The password (assuming one is needed) for the connection.
    _password = None

    # This is the list which is in play for the cd contextmanager
    working_directory = list()

    # Whether or not to halt on a task failure.
    warn_only = False

    # Whether or not to show all output in the log.  The logging still needs
    # some work for this to truly be as useful as I want.
    # [See GitHub Issue # 13]
    quiet = False

    # If an RSA key is to be used here is the ref
    _key = None

    # If we are using an RSA key, we will need a passphrase
    passphrase = None

    # This is the paramiko key reference.
    _paramiko_key = None

    @property
    def connection_string(self):
        # This is the connection string which is principally used for logging.
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
            raise AttributeError("host_port must be an integer between 1 and 65535")

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

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, username):
        if not isinstance(username, str):
            raise AttributeError("Usernames must be strings")
        self._user = username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        if not isinstance(password, str):
            raise AttributeError("Passwords must be strings")
        self._password = password
