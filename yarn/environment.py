import os
import getpass

class Environment:
    host_string = ""
    _port = 22
    debug = True
    _user = getpass.getuser()
    _password = None
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

#    @property
#    def working_directory(self):
#        return self._working_directory
#
#    @working_directory.setter
#    def working_directory(self, pathname):
#        if not isinstance(pathname, str):
#            raise AttributeError("Paths must be strings")
#        self._working_directory.append(pathname)

