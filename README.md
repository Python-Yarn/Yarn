# Yarn
A python2/3 library for host actuation via SSH.  It was inspired by Fabric, as will be evident by the similarity in commands and environment options.  I have used - and loved - Fabric for many years.  But, I needed python3 support; so I wrote my own minimal system.  


Yarn is intended as a minimal subset of common-use commands.  The current list of commands is:
* run - Run a command on the command line
* get - Download a file from a remote path
* put - Upload a file to a remote path

A single context manager (cd) is provided for running commands in a particular directory.

### Module-Use Example:
```
from yarn.api import cd, env, run


env.host_string = '192.168.1.2'
env.user = 'yarn'
env.password = 'yarn_is_aw3some!'

with cd("/usr/bin"):
    print(run("ls -al pytho*"))

```


This example shows how simple the interface really is.  This would be the same as connecting to the host (192.168.1.2) with the user (yarn) and the password (yarn_is_aw3some!), then changing directory to ```/usr/bin``` and running ```ls -al pytho*```.  


Of course, you could have nested the 'cd' contextmanager thusly:

```
with cd("/usr"):
    with cd("bin"):
        print(run("ls -al pytho*"))

```

And it would have worked the same.


### Yarnfile Example:
```
from yarn.api import cd, run


def test():
    with cd("/usr/bin"):
        print(run("ls -al pytho*"))

```

Then on the command line you would run:
```yarn --user yarn -H 192.168.1.2 test```

The output might look like:

```
[2015-10-23 16:30:05,119] DEBUG - run: RUNNING 'cd /usr/bin/ && ls -l pyth*' on '192.168.1.2'
lrwxrwxrwx 1 root root       9 Mar 16  2015 python -> python3.4
lrwxrwxrwx 1 root root       9 Mar 16  2015 python2 -> python2.7
-rwxr-xr-x 1 root root 3345416 Mar  1  2015 python2.7
lrwxrwxrwx 1 root root       9 Mar 16  2015 python3 -> python3.4
-rwxr-xr-x 1 root root 3709944 Mar  1  2015 python3.4

```

This would output the same as the previous module example.  Of note, is that the yarn command line does not take a password on the command line.  It will, however, query you for it.  This is done to keep a password out of your history.


### The Environment
The 'env' namespace contains several variables which can be set by the developer.
* host_string - (String) This is the host to which the system is going to connect.  DNS names (if dns is working) can be used here.
* user - (String) This is the username to use when connecting to the host.
* password - (String) This is the password for the user.  If you have already copied an SSH key to the remote host, this is not required.
* port - (Integer)

### Using a RSA key to authenticate

```
from yarn.api import cd, run

env.host_string = "192.168.1.2"
env.host_port = 22
env.user = "root"
env.key = "/home/user/.ssh/id_rsa"
env.passphrase = "example_passphrase"

print(run("uname"))

```

Output:

```
[2015-10-26 12:27:00,865] DEBUG - run: RUNNING 'uname' on '192.168.1.2'
Linux
```